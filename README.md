# PS3 — Script and Voiceover to B-roll Video Engine

## Current implementation

This project is a Python application with a FastAPI backend and Streamlit interface. It accepts a script or uploaded/remote voiceover, splits narration into scenes, searches stock footage through the configured provider, ranks candidates with Sentence Transformers when available, renders video with FFmpeg, and writes captions and per-job metadata.

The most recently inspected local run (job `fb25d88b870345dd834f313028d77dd8`, created 2026-10-20) used:

- Footage provider: Pixabay
- Text-to-speech provider: Edge TTS
- Semantic model: `sentence-transformers/all-MiniLM-L6-v2`
- Output: `video_16x9.mp4`
- Duration: about 203.4 seconds
- Timeline: 27 scenes
- Captions: `captions.srt`; manifest says burn-in and SRT enabled
- Frame-rate setting: 30 FPS (verify actual output with ffprobe before claiming the rendered file meets the spec)

These details describe one observed run, not a guarantee that every input or output format works.

## Architecture

```text
Streamlit UI / HTTP client
          |
          v
FastAPI (/api/v1)
          |
          v
Background job + input validation
   |          |             |
   v          v             v
TTS / ASR  Semantic ranker  Pixabay footage search
   \          |             /
    \         v            /
     ------ FFmpeg rendering
                 |
                 v
 MP4 + captions.srt + timeline.json + manifest.json
```

## Windows setup

1. Install Python 3.12 and FFmpeg/FFprobe. Ensure both executables are on `PATH`.
2. Open PowerShell in this directory.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and set `FOOTAGE_PROVIDER=pixabay` and `PIXABAY_API_KEY` to your own key. Never commit `.env`.
6. Start the API in terminal 1:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```
7. Start the UI in terminal 2:
   ```powershell
   python -m streamlit run ui.py
   ```
8. Open `http://localhost:8501`; API docs are at `http://127.0.0.1:8000/docs`.

If FFmpeg is not on PATH in a new PowerShell session, set it for that session before starting the API:

```powershell
$ffmpegBin = "C:\path\to\ffmpeg\bin"
$env:Path = "$ffmpegBin;$env:Path"
```

## Docker

The repository includes Docker files. Docker startup and the full container workflow must be tested on the final version before claiming one-command integration compliance. Configure environment variables through an untracked `.env` file or deployment secrets.

## API routes

- `GET /health` — process health.
- `GET /ready` — readiness check.
- `POST /api/v1/broll/jobs` — create a job from a script, scenes, or remote audio URL.
- `POST /api/v1/broll/jobs/upload` — create a job from uploaded audio.
- `GET /api/v1/jobs/{job_id}` — poll job status and result metadata.
- Output files are served under `/outputs/...` by the current local implementation.

Use an `Idempotency-Key` on POST requests where supported. Check `/docs` against `openapi.yaml` before submission; the OpenAPI file must match the running API exactly.

## Output files

Each job folder under `outputs/<job_id>/` may include:

- `video_16x9.mp4` and other requested aspect-ratio videos, if generated
- `captions.srt`
- `narration.mp3` for script-based TTS jobs
- scene/clip intermediate files
- `timeline.json`
- `manifest.json`

Do not manually replace `timeline.json` or `manifest.json` with generic documentation. They are generated evidence for a specific job. Regenerate a job after changing metadata-generation code, then inspect its output.

## Testing

Run unit/API tests:

```powershell
python -m pytest -q
```

Run the batch runner against the running API:

```powershell
python scripts/batch_runner.py test_inputs.jsonl --base-url http://localhost:8000 --out test-pack/batch-results.json
```

Keep the raw test output, batch results, generated files, and failure cases in `test-pack/`. Complete the human relevance rating sheet for ten varied inputs; automated similarity estimates are not human ratings.

## Known limitations and honest status

The latest inspected job proves that one script-based run produced a 16:9 MP4, SRT, timeline and manifest with 27 scenes. It does not prove all must-haves pass. In that timeline, several estimated relevance values are below 3.5/5, so ten varied cases must be tested and scenes must be human-rated before claiming the required mean relevance. The current manifest also contains a stale Pexels licence warning even though the observed job uses Pixabay; correct the code that creates the warning and regenerate the output.

Before claiming compliance, verify: MP3/WAV/M4A input and 10-minute limit; all aspect ratios; actual codecs/resolution/frame rate; no gaps or repeated clips; no black/frozen frames or audio drift; safety handling; provider-failure fallback; background progress; idempotency; persistent jobs; MinIO/S3 storage; structured logs and correlation IDs; HMAC callbacks if claimed; and a reproducible one-command Docker/test flow. Do not claim any untested capability.

## Rights and secrets

Verify the current Pixabay licence/API terms and the rights for each actual clip before commercial use. A source URL and a licence label in metadata are records, not independent proof that rights have been cleared. Verify Edge TTS service terms for the intended use. Never commit API keys, `.env`, access tokens, or personal credentials.
