import json, subprocess, shutil, re
from pathlib import Path
from urllib.parse import urlparse
import requests

class MediaError(RuntimeError): pass

def ffmpeg_path():
    path = shutil.which("ffmpeg")
    if not path: raise MediaError("FFmpeg is required. Install FFmpeg and add it to PATH.")
    return path

def run(cmd: list[str], timeout: int = 300):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise MediaError(f"Media command failed: {p.stderr[-1200:]}")
    return p.stdout

def download_audio(url: str, dest: Path) -> Path:
    parsed = urlparse(url)
    if parsed.scheme != "https": raise MediaError("Only HTTPS audio URLs are accepted")
    with requests.get(url, stream=True, timeout=(10, 60)) as r:
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").lower()
        if not any(x in ctype for x in ["audio/", "application/octet-stream"]):
            raise MediaError("URL did not return an audio content type")
        total = 0
        with dest.open("wb") as f:
            for chunk in r.iter_content(256*1024):
                total += len(chunk)
                if total > 100 * 1024 * 1024: raise MediaError("Audio exceeds 100 MB limit")
                f.write(chunk)
    return dest

def duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(out)["format"]["duration"])

def make_tts(text: str, dest: Path, voice: str):
    # edge-tts is an external provider; disclose it and verify current terms before production use.
    try:
        import asyncio, edge_tts
        voice_map = {"en-IN-female":"en-IN-NeerjaNeural", "en-IN-male":"en-IN-PrabhatNeural", "en-US-female":"en-US-AriaNeural", "en-US-male":"en-US-GuyNeural"}
        async def go():
            await edge_tts.Communicate(text, voice_map.get(voice, voice), rate="+0%").save(str(dest))
        asyncio.run(go())
    except Exception as e:
        raise MediaError(f"Text-to-speech failed. Check internet access and voice setting. Details: {e}")

def make_srt(scenes: list[dict], path: Path):
    def ts(t):
        ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    lines=[]
    for i, s in enumerate(scenes, 1):
        lines += [str(i), f"{ts(s['start'])} --> {ts(s['end'])}", s["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")

def render_scene(clip: Path, audio: Path, out: Path, start: float, end: float, ratio: str, srt: Path | None, burn_in: bool, fps: int = 30):
    w,h = {"16:9":(1920,1080), "9:16":(1080,1920), "1:1":(1080,1080)}[ratio]
    dur = max(0.5, end-start)
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},format=yuv420p"
    if burn_in and srt:
        escaped = str(srt.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        vf += f",subtitles='{escaped}':force_style='FontSize=22,Outline=2,Shadow=1,Alignment=2,MarginV=55'"
    run([ffmpeg_path(), "-y", "-stream_loop", "-1", "-i", str(clip), "-ss", str(start), "-t", str(dur), "-i", str(audio),
         "-map", "0:v:0", "-map", "1:a:0", "-vf", vf, "-af", "aresample=async=1:first_pts=0", "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)], timeout=600)

def concat_scenes(parts: list[Path], out: Path, fps: int = 30):
    listfile = out.parent / "concat.txt"
    listfile.write_text("".join("file '" + str(p.resolve()).replace("'", "'\\''") + "'\n" for p in parts), encoding="utf-8")
    run([ffmpeg_path(), "-y", "-f", "concat", "-safe", "0", "-i", str(listfile), "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)], timeout=900)
