# Engineering Report — IncuBrix PS3 Script and Voiceover to B-roll Video Engine

## 1. Objective
Build a prototype that accepts a text script or narration and produces scene-based B-roll video with voiceover, captions, and supporting timeline/manifest metadata.

## 2. Current deployment and flow
- **Frontend:** Streamlit Cloud — https://incubrix-ps3-broll-engine-htngdsxkqfbc5dftgkxu52.streamlit.app/
- **Backend:** FastAPI on Render — https://incubrix-ps3-broll-engine.onrender.com
- **Repository:** https://github.com/sreevarshiniar/IncuBrix-PS3-Broll-Engine
- The Streamlit UI submits a job to the FastAPI service, receives a job ID, polls for status, and displays output artifacts when available.
- The UI is currently displaying. Cloud end-to-end generation is not yet confirmed stable because a status poll returned a Render 502 HTML response during testing.

## 3. Design choices
- **Streamlit** provides the browser-based user interface.
- **FastAPI** provides API endpoints, input validation, health/readiness checks, and job status responses.
- **In-process background executor** lets job creation return before rendering finishes, but current in-memory state is not durable across restarts.
- **Edge TTS** is used for text-to-speech where configured.
- **faster-whisper** supports transcription of uploaded narration where configured and available.
- **Sentence Transformers** supports semantic matching when the embedding model is available; similarity values are not human ratings.
- **Configured stock-footage provider** supplies candidate B-roll assets. Verify the actual deployed environment and provider settings before claiming a specific provider or asset rights.
- **FFmpeg/FFprobe** handle media processing and rendering.

## 4. Implemented in the codebase
The source includes health/readiness endpoints, JSON job creation, upload-based job creation, job-status endpoints, input validation, an idempotency path for JSON requests, script-to-TTS processing, audio transcription, footage retrieval, scene/timeline metadata, SRT/manifest generation, Docker configuration, and selected unit/API tests.

## 5. Deployment observations (20 October 2026)
- `GET /health` returned HTTP 200.
- `GET /ready` returned HTTP 200 in earlier checks.
- `POST /api/v1/broll/jobs` returned HTTP 202 for a cloud job.
- Repeated `GET /api/v1/jobs/{job_id}` calls returned HTTP 200 for a period.
- A later status request surfaced an HTTP 502 HTML response from Render.
- The log excerpt ended with Uvicorn starting a new server process, but does not include enough preceding lines to identify whether this was a crash, deploy, platform restart, or resource event.

The failure cause remains unconfirmed. The current in-memory job model is a known risk because a restart can erase job records. Review Render Events and the logs immediately before the process restart; then retest a complete cloud job.

## 6. Measurements and evidence
Do not invent metrics. Update the table only after running tests and saving evidence.

| Metric | Status | Evidence required |
|---|---|---|
| Local unit/API tests | Previously reported: 5 passed | Re-run exact submitted commit and save terminal output |
| Complete cloud video generation | NOT CONFIRMED | Successful job plus accessible rendered MP4 |
| 60-second cold turnaround | NOT MEASURED | Timestamped test/log |
| 60-second warm turnaround | NOT MEASURED | Timestamped test/log |
| Cost per finished minute | NOT MEASURED | Provider/API/compute assumptions and calculation |
| 10-input human relevance benchmark | NOT COMPLETED/VERIFIED | Ten completed examples and human ratings |
| Mean human relevance (1–5) | NOT MEASURED | Human-rated scene sheet |
| Render success rate | NOT MEASURED | Batch runner results |
| Duplicate clip rate | NOT VERIFIED | Timeline audit across completed jobs |
| Peak memory / GPU | NOT MEASURED | Runtime/system measurement |

## 7. Known gaps and next steps
1. Diagnose the Render 502 and confirm the cause of the process start/restart.
2. Persist job records and idempotency state outside process memory.
3. Configure persistent/object storage for generated videos and artifacts.
4. Add a durable task queue if long-running jobs must survive process restarts.
5. Validate provider failover and rights metadata for every selected asset.
6. Test audio formats, long inputs, aspect ratios, frame quality, frozen/black frames, and audio drift.
7. Run the required 10-input benchmark and record human relevance scores separately from model similarity scores.
8. Verify TTS, model, stock media, and FFmpeg build terms/configuration.

## 8. Conclusion
The project has a deployed Streamlit interface and a separately deployed FastAPI processing service. The UI is visible, but cloud end-to-end generation still requires verification because a Render 502 occurred during status polling. Report the current state honestly as a prototype/demo with outstanding reliability and evaluation work; do not claim every assessment must-have is complete.
