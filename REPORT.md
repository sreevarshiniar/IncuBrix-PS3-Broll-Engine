# Engineering Report — PS3 Script and Voiceover to B-roll Video Engine

## 1. Objective

Build an HTTP service that accepts a script, scene list or voiceover and produces a scene-timed B-roll video, captions, and metadata describing the footage and generation configuration.

## 2. Implementation and design choices

- **FastAPI** exposes the HTTP API and validates requests.
- **Streamlit** provides a browser-based interface for trying the workflow.
- **Edge TTS** is used for narration from text in the observed script workflow.
- **Pixabay** is the configured footage provider in the latest observed local run.
- **Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`)** ranks candidate footage semantically.
- **FFmpeg/FFprobe** are used for media processing and should be used to verify output properties.
- Per-job output includes a video, SRT captions, `timeline.json`, and `manifest.json`.

## 3. Evidence from the latest observed run

The latest inspected output folder was `outputs/fb25d88b870345dd834f313028d77dd8/`.

| Item | Observed value | Evidence / qualification |
|---|---|---|
| Job status | `succeeded` | `manifest.json` |
| Footage provider | Pixabay | `manifest.json` and timeline records |
| TTS provider | Edge TTS | `manifest.json` |
| Semantic model | `sentence-transformers/all-MiniLM-L6-v2` | `manifest.json` |
| Scenes | 27 | `timeline.json` |
| Narration duration | 203.424 seconds | `timeline.json` / manifest |
| Rendered video | `video_16x9.mp4` | Job output directory |
| Render duration | 203.367 seconds | `manifest.json` |
| Captions | `captions.srt` present | Job output directory |
| Timeline and manifest | Both present | Job output directory |
| FPS | Configured as 30 | Manifest setting; actual encoded stream still requires ffprobe verification |

The current timeline includes source URLs, creator names, licence text, attribution text, selection reasons, and estimated relevance scores for scenes. Some estimates are low (including values around 2.0–2.9), so this run alone does not establish the assessment's required average human relevance of at least 3.5/5.

## 4. Measurement results

Do not fill unknown metrics with estimates. Replace `NOT MEASURED` only after collecting evidence.

| Metric | Result | Evidence required |
|---|---|---|
| 60-second cold turnaround | NOT MEASURED | Timestamped cold run |
| 60-second warm turnaround | NOT MEASURED | Timestamped warm run |
| Cost per finished minute | NOT MEASURED | Provider charges and compute assumptions |
| Coverage with human relevance >= 3 | NOT MEASURED | Scene-level human rating sheet |
| Mean human relevance across 10 varied videos | NOT MEASURED | Ten outputs and reviewer ratings |
| Render success rate | NOT MEASURED | Batch results including failures |
| Repeat-clip rate | NOT MEASURED across the full test pack | Timeline audit for every test |
| Peak memory / GPU time | NOT MEASURED | Resource measurement |

## 5. Known gaps / risks

- The current manifest warning still refers to Pexels terms even though the observed run used Pixabay. Update the manifest-generation code so warnings accurately reflect the configured provider, then regenerate and inspect outputs.
- The latest job is only 16:9. Support for 9:16 and 1:1 must be tested before claiming all aspect ratios.
- Validate the encoded video using FFprobe; a configured FPS value alone is not proof of the encoded frame rate or resolution.
- Run ten varied inputs and manually rate scene relevance. Do not treat embedding similarity or the generated estimated relevance field as human ratings.
- Verify every asset's actual terms and attribution requirements. Metadata labels do not themselves establish commercial clearance.
- Validate provider outage/fallback, upload formats, audio limits, scene coverage, no-repeat behaviour, safety cases, and caption timing.
- Check integration requirements such as durable background jobs, retry/idempotency behaviour, S3-compatible storage, structured logs/correlation IDs, HMAC callbacks if claimed, and one-command Docker/test execution. Mark unimplemented or untested items as partial/no.

## 6. Next steps

1. Correct provider-specific manifest warnings and regenerate the sample.
2. Validate MP4 codec, dimensions, FPS, duration and audio with FFprobe.
3. Run the test pack and preserve both passing and failing outputs.
4. Create a ten-video human relevance sheet and calculate the actual mean.
5. Verify source rights and commercial-use terms.
6. Update the Excel submission workbook with evidence links and truthful Yes/Partial/No status.

## 7. Conclusion

The current evidence demonstrates one successful local script-to-video run with scene metadata and captions. It does not demonstrate that all mandatory assessment requirements are satisfied. This report deliberately separates observed evidence from features and metrics that still need verification.
