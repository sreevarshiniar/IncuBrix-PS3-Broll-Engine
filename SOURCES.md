# Sources, models, APIs, and licence verification

This document describes intended/known dependencies. Check the exact deployed configuration, package versions, model cards, API terms, and selected asset licences before making any compliance claim. Never store credentials in this file.

| Component | Use | Licence/terms notes | Current verification status |
|---|---|---|---|
| Python | Application runtime | Python Software Foundation License | Development used Python 3.12.7; verify deployed runtime |
| Streamlit | Frontend UI | Apache-2.0 | UI is deployed on Streamlit Cloud; verify exact package version |
| FastAPI / Uvicorn | HTTP API service | MIT | Backend deployed on Render; verify exact package versions |
| Pydantic / pydantic-settings | Configuration and validation | MIT | Verify installed versions |
| Requests / HTTPX | HTTP clients and tests | Apache-2.0 / BSD-3-Clause | Verify pinned/resolved versions |
| FFmpeg / FFprobe | Media probing, processing, and rendering | LGPL/GPL status depends on build configuration and enabled components | Local FFmpeg 9.0.2 essentials build was used; verify deployment build and codec configuration |
| sentence-transformers/all-MiniLM-L6-v2 | Embeddings for semantic matching | Verify model card, exact revision, and model-file terms | Used/intended; confirm successful load in deployed runtime |
| faster-whisper and selected model | Speech transcription | Code and model weights can have different terms; verify the exact model card | Transcription path exists; verify deployed usage and model selection |
| Edge TTS | Text-to-speech narration | Online speech service; verify applicable Microsoft/service/voice terms and usage conditions | Configured in project; commercial/assessment use terms not independently cleared |
| Stock footage provider (deployment setting) | B-roll retrieval | Follow current provider API terms and each selected asset's licence and attribution requirements | Verify actual deployed provider and every chosen asset; manifest metadata alone is not clearance |
| pytest | Automated tests | MIT | Used for local tests; re-run and save evidence for submitted commit |

## Evidence to retain
- `python --version`, `pip freeze` or package version output.
- `ffmpeg -version` and relevant codec/build configuration.
- Model name/revision and model-card URL for the actual loaded model.
- Provider name, asset URL, creator, licence, and required attribution for each selected stock clip.
- Test output and actual completed video artifacts.

Do not claim assets are commercially cleared solely because the API returned them. Do not put API keys, tokens, or `.env` values into source control or evidence screenshots.
