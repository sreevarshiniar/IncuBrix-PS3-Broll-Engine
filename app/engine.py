import json, time, uuid, hashlib, re, logging, os
from pathlib import Path
from datetime import datetime, timezone
from app.config import settings
from app.schemas import JobRequest
from app.semantic import split_scenes, rank_candidates
from app.providers import get_provider, download_clip, ProviderError
from app.media import download_audio, make_tts, duration, make_srt, render_scene, concat_scenes, MediaError

log = logging.getLogger("broll")

class JobStore:
    def __init__(self): self.jobs={}; self.idempotency={}
    def create(self, payload: dict, key: str | None):
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        if key and key in self.idempotency:
            old_digest, job_id = self.idempotency[key]
            if old_digest != digest: raise ValueError("Idempotency-Key was already used with a different request")
            return self.jobs[job_id], False
        job_id = uuid.uuid4().hex
        job={"job_id":job_id,"status":"queued","progress":0,"created_at":datetime.now(timezone.utc).isoformat(),"updated_at":datetime.now(timezone.utc).isoformat(),"request":payload,"warnings":[],"result":None,"error":None}
        self.jobs[job_id]=job
        if key: self.idempotency[key]=(digest, job_id)
        return job, True
    def update(self, job_id, **fields):
        self.jobs[job_id].update(fields, updated_at=datetime.now(timezone.utc).isoformat())

store = JobStore()

def _transcribe(audio: Path) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(os.getenv("WHISPER_MODEL", "tiny"), device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio), vad_filter=True)
        return [{"text":s.text.strip(),"start":float(s.start),"end":float(s.end)} for s in segments if s.text.strip()]
    except Exception as e:
        raise MediaError(f"Could not transcribe audio. Install/download faster-whisper model and retry. Details: {e}")

def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text[:45]).strip("_") or "scene"

def run_job(job_id: str, req: JobRequest, input_audio_path: Path | None = None):
    job_dir = settings.outputs_dir / job_id; job_dir.mkdir(parents=True, exist_ok=True)
    try:
        store.update(job_id, status="running", progress=2)
        audio = input_audio_path
        if input_audio_path is not None:
            audio = input_audio_path
        elif req.audio_url:
            audio = job_dir / "input_audio"
            download_audio(str(req.audio_url), audio)
        elif req.script:
            audio = job_dir / "narration.mp3"
            make_tts(req.script, audio, req.voice)
        elif req.scenes:
            combined = " ".join(s.text for s in req.scenes)
            audio = job_dir / "narration.mp3"
            make_tts(combined, audio, req.voice)
        if not audio or not audio.exists(): raise MediaError("No audio was created or supplied")
        total_duration = duration(audio)
        if total_duration <= 0 or total_duration > settings.max_audio_seconds:
            raise MediaError(f"Audio duration must be between 0 and {settings.max_audio_seconds} seconds")
        store.update(job_id, progress=12)
        if req.scenes:
            texts = [{"text":s.text,"visual_hint":s.visual_hint} for s in req.scenes]
            # Allocate scene durations proportional to words; the voiceover remains the timing authority.
            weights=[max(1,len(s["text"].split())) for s in texts]; denom=sum(weights); cursor=0.0
            for i,s in enumerate(texts):
                s["start"]=cursor; cursor=total_duration if i==len(texts)-1 else cursor+total_duration*weights[i]/denom; s["end"]=cursor
        elif req.script:
            texts=split_scenes(req.script)
            if not texts: raise MediaError("Script is empty")
            weights=[max(1,len(s["text"].split())) for s in texts]; denom=sum(weights); cursor=0.0
            for i,s in enumerate(texts):
                s["start"]=cursor; cursor=total_duration if i==len(texts)-1 else cursor+total_duration*weights[i]/denom; s["end"]=cursor
        else:
            texts=_transcribe(audio)
            if not texts: raise MediaError("No speech detected in audio")
            # Merge short whisper segments to phrase boundaries; keep chronological timing.
            merged=[]
            for s in texts:
                if merged and (s["start"]-merged[-1]["end"] < 0.35) and (merged[-1]["end"]-merged[-1]["start"] < 7):
                    merged[-1]["text"] += " " + s["text"]; merged[-1]["end"] = s["end"]
                else: merged.append(dict(s))
            texts=merged
        # Normalize to complete coverage and avoid zero-length scenes.
        texts[0]["start"] = 0.0; texts[-1]["end"] = total_duration
        for i,s in enumerate(texts):
            s["start"] = max(0.0, float(s["start"])); s["end"] = min(total_duration, max(s["start"]+0.5, float(s["end"])))
            if i: s["start"] = texts[i-1]["end"]
            if i < len(texts)-1: s["end"] = max(s["start"]+0.5, float(texts[i]["end"]))
        store.update(job_id, progress=20)
        provider = get_provider(settings)
        used_ids=set(); timeline=[]; clip_paths=[]
        for i,scene in enumerate(texts):
            query = " ".join(x for x in [scene.get("visual_hint"), scene["text"], req.style] if x)
            # Search semantic description first; if the provider returns no footage, use a shorter query fallback.
            candidates=[]
            errors=[]
            for q in [query, " ".join(scene["text"].split()[:5]) + " real world footage"]:
                try:
                    candidates=provider.search(q, req.avoid, per_page=12)
                    if candidates: break
                except Exception as e: errors.append(str(e))
            if not candidates:
                raise ProviderError("No footage candidates returned. " + "; ".join(errors[-2:]))
            ranked=rank_candidates((scene.get("visual_hint") or "") + " " + scene["text"], candidates)

            
            chosen = None
            reason = ""
            relevance_score = None

            for score, candidate, why in ranked:
                if candidate.get("id") in used_ids:
                    continue

                chosen = candidate
                reason = f"Highest-ranked unused candidate; {why}; score={score:.3f}"
                relevance_score = round(float(score), 4)
                break

            if chosen is None: raise ProviderError("Provider returned no unique unused clips for all scenes")
            used_ids.add(chosen.get("id"))
            clip = job_dir / f"clip_{i:03}.mp4"
            download_clip(chosen, clip); clip_paths.append(clip)
            item={"scene_id":i+1,"text":scene["text"],"start":round(scene["start"],3),"end":round(scene["end"],3),"duration":round(scene["end"]-scene["start"],3),
                  "visual_hint":scene.get("visual_hint"),"clip_file":clip.name,"clip_id":chosen.get("id"),"source":chosen.get("source_url"),"provider":chosen.get("provider"),
                  "creator":chosen.get("creator"),"license":chosen.get("license"),"attribution":chosen.get("attribution"),"ai_generated":False,"reason_chosen":reason,"semantic_similarity_score":relevance_score}
            timeline.append(item)
            store.update(job_id, progress=20 + int(35*(i+1)/len(texts)))
        # Scene-specific SRTs avoid showing captions from other scenes in split renders.
        srt_path=job_dir/"captions.srt"; make_srt(timeline,srt_path)
        videos=[]
        for ratio_index,ratio in enumerate(req.aspect_ratios):
            parts=[]
            for i,(scene,clip) in enumerate(zip(timeline,clip_paths)):
                local_srt=job_dir/f"scene_{i:03}.srt"
                local_scene={**scene,"start":0.0,"end":scene["end"]-scene["start"]}; make_srt([local_scene],local_srt)
                part=job_dir/f"part_{ratio.replace(':','x')}_{i:03}.mp4"
                render_scene(clip,audio,part,scene["start"],scene["end"],ratio,local_srt,req.captions.burn_in,settings.default_fps)
                parts.append(part)
            out=job_dir/f"video_{ratio.replace(':','x')}.mp4"; concat_scenes(parts,out,settings.default_fps)
            videos.append({"aspect_ratio":ratio,"path":str(out),"download_url":f"/outputs/{job_id}/{out.name}","duration_seconds":round(duration(out),3)})
            store.update(job_id, progress=60 + int(25*(ratio_index+1)/len(req.aspect_ratios)))
        timeline_path=job_dir/"timeline.json"; timeline_path.write_text(json.dumps({"job_id":job_id,"duration_seconds":total_duration,"scenes":timeline},indent=2),encoding="utf-8")
        manifest={"job_id":job_id,"created_at":datetime.now(timezone.utc).isoformat(),"status":"succeeded","providers":{"footage":provider.name,"tts":settings.tts_provider,"semantic_model":settings.embedding_model},
          "versions":{"python":os.sys.version.split()[0]},"settings":{"aspect_ratios":req.aspect_ratios,"style":req.style,"avoid":req.avoid,"fps":settings.default_fps,"captions":req.captions.model_dump()},
          "timings":{"audio_duration_seconds":round(total_duration,3)},"cost_estimate_usd":0.0 if settings.footage_provider=="mock" else None,
          
          "warnings": [
            "Cost estimate excludes compute and must be measured by the candidate.",
            (
                "Verify current Pixabay content licence terms for the intended use."
                if provider.name.lower() == "pixabay"
                else "Verify the active footage provider's current licence and API terms."
            ),
          ],

          "rights":{"footage_provider":provider.name,"per_clip_rights_recorded":True,"ai_generated_media":False},"outputs":videos}
        manifest_path=job_dir/"manifest.json"; manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
        result={"videos":videos,"captions_url":f"/outputs/{job_id}/captions.srt","timeline_url":f"/outputs/{job_id}/timeline.json","manifest_url":f"/outputs/{job_id}/manifest.json","duration_seconds":round(total_duration,3)}
        store.update(job_id,status="succeeded",progress=100,result=result)
    except Exception as e:
        log.exception("job_failed job_id=%s", job_id)
        store.update(job_id,status="failed",progress=100,error={"code":"JOB_FAILED","message":str(e),"retryable":isinstance(e,(ProviderError,TimeoutError,ConnectionError)),"details":{}})
