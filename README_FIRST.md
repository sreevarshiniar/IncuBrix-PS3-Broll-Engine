# First 30 minutes

1. Install Python 3.11 and FFmpeg (or use Docker).
2. Copy `.env.example` to `.env`; set `PEXELS_API_KEY` from your own Pexels developer account.
3. Run `docker compose up --build`.
4. In another terminal run `pip install -r requirements.txt` and `streamlit run ui.py` (or use `/docs` to test the API).
5. Submit a short 3-sentence script, wait for the job, and inspect the MP4, SRT, timeline and manifest.
6. If the first end-to-end job fails, fix that before adding features.

Never commit your `.env` file or API key. Check current provider/model licences before using outputs commercially.
