# AI use disclosure

Update this disclosure to reflect the actual work performed before submission. The entries below reflect the known development flow; add or remove entries if your usage differs.

## AI coding and documentation assistance

- **ChatGPT (OpenAI):** used to help plan the project, explain implementation steps, troubleshoot local execution, draft/revise documentation, and prepare test and submission guidance. All submitted code and claims must be reviewed and understood by the candidate, who remains responsible for correctness and attribution.
- **Other AI coding assistants:** list each tool actually used to write, explain, debug or modify code. Do not list a tool merely because it was available or used for unrelated tasks.

## Models and AI services used by the application

- **Sentence Transformers — `sentence-transformers/all-MiniLM-L6-v2`:** used for semantic similarity/ranking of candidate footage against scene text in the observed run. The output's `relevance_score_estimate` is an automated estimate, not a human rating or independent vision-language evaluation.
- **Edge TTS:** used to synthesize narration from text in the observed run. Verify applicable terms before asserting commercial suitability.
- **Audio transcription model/library:** disclose the exact transcription library and model only if it was actually used in the submitted audio-input path. The project has referenced faster-whisper; verify the exact runtime path and model revision before claiming it was used for the sample.

## AI-generated media

The inspected job's manifest records `ai_generated_media: false`; the B-roll was retrieved from Pixabay and the narration was synthesized with Edge TTS. Do not interpret `ai_generated_media: false` as meaning that the voice was not synthesized. Keep the metadata semantics clear: distinguish stock footage, generated narration, and AI-generated visual footage. If the implementation changes, update the metadata and this disclosure accordingly.

## Required final check

Before submission, record every AI coding assistant, model, API and generated component actually used, including approximate purpose. Remove untrue or speculative statements. Do not claim independent authorship of code you cannot explain and modify in a live session.
