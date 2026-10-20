# Test pack index

- `../test_inputs.jsonl`: seed cases for script generation, ambiguous wording, and empty input.
- Run `python -m pytest -q` for local unit/API tests. Save the terminal output for the exact submitted commit.
- Run `python scripts/batch_runner.py test_inputs.jsonl --base-url http://127.0.0.1:8000 --out test-pack/batch-results.json` against a running local API to save job evidence.
- For each completed sample, retain the input, generated MP4, captions, timeline, manifest, logs, and any failure details.
- For the 10-input relevance benchmark, record human scene relevance (1–5), rationale, coverage, aspect ratio, and warnings. Do not invent ratings or use cosine similarity as a human score.
- The deployed UI is https://incubrix-ps3-broll-engine-htngdsxkqfbc5dftgkxu52.streamlit.app/ and the API is https://incubrix-ps3-broll-engine.onrender.com. A Render 502 occurred during deployed status polling, so record a cloud test as passed only after a complete video is successfully generated and retrieved.
