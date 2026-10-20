# First-run and demo checklist

## Local run
1. Install Python and FFmpeg/FFprobe.
2. Create/activate `.venv` and run `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure the selected footage provider. Never commit credentials.
4. Start the API: `python -m uvicorn app.main:app --reload`.
5. Start the UI in a second terminal: `python -m streamlit run ui.py`.
6. Open `http://localhost:8501`; set API base URL to `http://127.0.0.1:8000`.
7. Run a short test script first, then inspect MP4, SRT, timeline, and manifest if the job completes.
8. Run `python -m pytest -q` and save the test output.

## Current deployed demo
- UI: https://incubrix-ps3-broll-engine-htngdsxkqfbc5dftgkxu52.streamlit.app/
- API: https://incubrix-ps3-broll-engine.onrender.com
- API docs: https://incubrix-ps3-broll-engine.onrender.com/docs

The UI currently loads, but a cloud job-status request has returned a Render 502 during testing. Do not claim end-to-end cloud generation is stable until a complete video is generated and downloaded from the deployed demo.

## Before final submission
- Confirm the frontend URL opens in an incognito/private browser window.
- Confirm the UI points to the deployed API, not `localhost`.
- If possible, run one short end-to-end cloud generation and capture the result.
- Include only measured test results. Do not convert cosine similarity into human ratings.
- Keep `.env`, API keys, and other secrets out of GitHub and screenshots.
- Clearly disclose remaining limitations in the report/form.
