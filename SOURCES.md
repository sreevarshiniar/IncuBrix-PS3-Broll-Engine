# Sources, models, APIs, libraries and rights

This file describes components observed in the current project. Before final submission, verify exact installed versions, official terms and the actual default configuration. Do not include API keys.

| Component | Use in project | Licence / rights notes | Status |
|---|---|---|---|
| Python 3.12.7 | Runtime | Python Software Foundation License | Version observed locally; verify at final build |
| FastAPI | HTTP API | MIT | Verify installed version |
| Pydantic / pydantic-settings | Validation and environment configuration | MIT | Verify installed versions |
| Streamlit | Browser UI | Apache-2.0 | Verify installed version |
| Requests | HTTP requests | Apache-2.0 | Verify installed version |
| Sentence Transformers `sentence-transformers/all-MiniLM-L6-v2` | Semantic text embeddings/ranking | Verify exact model card and terms for the downloaded revision | Used in latest manifest; exact revision not recorded |
| Pixabay API and stock videos | B-roll search and source assets | Review current Pixabay Content License/API terms and each asset's restrictions; preserve source URL, creator and attribution | Used in latest observed job; rights still require verification |
| Edge TTS | Text-to-speech narration | Verify Microsoft's applicable service terms, voice terms, and permitted commercial use | Used in latest observed job; terms not independently verified here |
| FFmpeg / FFprobe | Clip processing, encoding and media inspection | Build licence depends on configuration; verify the exact distribution and enabled codecs | FFmpeg 9.0.2 essentials build was used locally; verify actual executable/build in final environment |
| faster-whisper | Audio transcription, if enabled in the audio-input path | Code and selected model weights can have different terms; verify exact model and terms | Verify actual usage and model before claiming |
| pytest / httpx | Automated tests | Verify installed versions and package licences | Used by test pack; exact versions should be recorded |
| ChatGPT (OpenAI) | AI coding/documentation assistance | Record actual assistance accurately in `AI_USE.md` | Used during project development; details in `AI_USE.md` |

## Media audit

For each selected clip, retain its exact source URL, provider, creator, applicable licence, attribution requirements, and the date/record used to verify those details. A generic string such as “Pixabay Content License; verify current terms” is not a completed rights review. Do not claim every clip is commercially cleared until the current terms and asset-level restrictions have been checked.

## Environment and secrets

API keys belong in `.env` or deployment secrets and must never appear in this file, source control, logs, screenshots, or demo recordings. The repository should contain `.env.example` with variable names and non-secret example values only.
