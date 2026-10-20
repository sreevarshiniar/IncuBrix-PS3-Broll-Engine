import logging, json, uuid, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Header, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.schemas import JobRequest
from app.engine import store, run_job

logging.basicConfig(level=settings.log_level, format='%(message)s')
logger=logging.getLogger("broll-api")
app=FastAPI(title=settings.app_name, version="1.0.0", description="Script/audio to licence-aware B-roll video engine")
executor=ThreadPoolExecutor(max_workers=2)
settings.outputs_dir.mkdir(parents=True,exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(settings.outputs_dir)), name="outputs")

@app.middleware("http")
async def correlation(request: Request, call_next):
    cid=request.headers.get("X-Correlation-Id",str(uuid.uuid4()))
    response=await call_next(request); response.headers["X-Correlation-Id"]=cid
    logger.info(json.dumps({"timestamp":__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),"level":"INFO","job_id":None,"correlation_id":cid,"method":request.method,"path":request.url.path,"status_code":response.status_code}))
    return response

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/ready")
def ready():
    import shutil
    return {"ready": bool(shutil.which("ffmpeg") and shutil.which("ffprobe")),"ffmpeg":bool(shutil.which("ffmpeg")),"ffprobe":bool(shutil.which("ffprobe"))}

@app.post(settings.api_prefix+"/broll/jobs",status_code=202)
def create_job(req: JobRequest, request: Request, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    try: job, created=store.create(req.model_dump(mode="json"),idempotency_key)
    except ValueError as e: raise HTTPException(409,detail={"error":{"code":"IDEMPOTENCY_CONFLICT","message":str(e),"retryable":False,"details":{}}})
    if created: executor.submit(run_job,job["job_id"],req,None)
    return {"job_id":job["job_id"],"status":job["status"],"status_url":f"{settings.api_prefix}/jobs/{job['job_id']}"}

@app.post(settings.api_prefix+"/broll/jobs/upload",status_code=202)
async def create_upload_job(file: UploadFile=File(...), script: str | None=Form(default=None), aspect_ratios: str=Form(default='["16:9"]'), style: str=Form(default="bright, modern, real-world footage"), idempotency_key: str | None=Header(default=None,alias="Idempotency-Key")):
    suffix=Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in {".mp3",".wav",".m4a",".aac",".ogg"}: raise HTTPException(415,detail={"error":{"code":"UNSUPPORTED_AUDIO_TYPE","message":"Upload MP3, WAV or M4A audio","retryable":False,"details":{}}})
    temp=settings.uploads_dir/f"{uuid.uuid4().hex}{suffix}"
    size=0
    with temp.open("wb") as f:
        while chunk:=await file.read(1024*1024):
            size+=len(chunk)
            if size>100*1024*1024: temp.unlink(missing_ok=True); raise HTTPException(413,"Audio exceeds 100 MB")
            f.write(chunk)
    req=JobRequest(audio_url="https://upload.invalid/audio.mp3", aspect_ratios=json.loads(aspect_ratios),style=style)
    payload={"uploaded_audio_sha256":__import__('hashlib').sha256(temp.read_bytes()).hexdigest(),"aspect_ratios":req.aspect_ratios,"style":style}
    try: job,created=store.create(payload,idempotency_key)
    except ValueError as e: temp.unlink(missing_ok=True); raise HTTPException(409,detail={"error":{"code":"IDEMPOTENCY_CONFLICT","message":str(e),"retryable":False,"details":{}}})
    if created: executor.submit(run_job,job["job_id"],req,temp)
    else: temp.unlink(missing_ok=True)
    return {"job_id":job["job_id"],"status":job["status"],"status_url":f"{settings.api_prefix}/jobs/{job['job_id']}"}

@app.get(settings.api_prefix+"/jobs/{job_id}")
def get_job(job_id: str):
    job=store.jobs.get(job_id)
    if not job: raise HTTPException(404,detail={"error":{"code":"JOB_NOT_FOUND","message":"Job not found","retryable":False,"details":{}}})
    return {k:job[k] for k in ["job_id","status","progress","created_at","updated_at","result","error","warnings"]}

@app.get(settings.api_prefix+"/broll/jobs/{job_id}")
def get_broll_job(job_id: str): return get_job(job_id)
