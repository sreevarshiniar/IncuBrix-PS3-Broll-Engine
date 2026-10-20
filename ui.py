
import os
import time
from typing import Any

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="B-roll Studio | IncuBrix PS3",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_API = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000",
).rstrip("/")

REQUEST_TIMEOUT = 120
POLL_INTERVAL = 2
MAX_POLL_ATTEMPTS = 300


# ============================================================
# DARK THEME
# ============================================================

def apply_dark_theme():
    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap'
        );

        :root {
            color-scheme: dark;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: #08080d !important;
            color: #f5f5fa !important;
            font-family: 'DM Sans', sans-serif;
        }

        [data-testid="stHeader"] {
            background: rgba(8, 8, 13, 0.95) !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: #08080d !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }

        [data-testid="stSidebar"] {
            background: #0e0e16 !important;
            border-right: 1px solid #242435;
        }

        [data-testid="stSidebar"] * {
            color: #ededf7;
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #fafaff !important;
            letter-spacing: -0.5px;
        }

        p, label, span, div {
            font-family: 'DM Sans', sans-serif;
        }

        [data-testid="stMarkdownContainer"] p {
            color: #b9b9cb;
            line-height: 1.65;
        }

        [data-testid="stMetric"] {
            background: #11111b;
            border: 1px solid #28283a;
            border-radius: 15px;
            padding: 18px 20px;
        }

        [data-testid="stMetricLabel"] {
            color: #aaaac0 !important;
        }

        [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        [data-testid="stMetricDelta"] {
            color: #b9a0ff !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input {
            background: #11111b !important;
            color: #f5f5fa !important;
            border: 1px solid #34344a !important;
            border-radius: 10px !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
            border-color: #9270ff !important;
            box-shadow: 0 0 0 1px #9270ff !important;
        }

        [data-baseweb="select"] > div {
            background: #11111b !important;
            color: #f5f5fa !important;
            border-color: #34344a !important;
            border-radius: 10px !important;
        }

        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background: #171722 !important;
            color: #f5f5fa !important;
        }

        [data-baseweb="menu"] * {
            color: #f5f5fa !important;
        }

        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label,
        [data-testid="stSlider"] label {
            color: #d5d5e5 !important;
        }

        [data-testid="stFileUploader"] {
            background: #11111b;
            border: 1px dashed #45455f;
            border-radius: 14px;
            padding: 12px;
        }

        [data-testid="stFileUploader"] section {
            background: #11111b !important;
        }

        [data-testid="stFileUploader"] button {
            background: #242438 !important;
            color: #ffffff !important;
            border: 1px solid #45455f !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: #8257f5 !important;
            color: #ffffff !important;
            border: 1px solid #986fff !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            min-height: 44px;
            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #7044e8 !important;
            border-color: #b09aff !important;
            transform: translateY(-1px);
        }

        .stButton > button:disabled {
            background: #292438 !important;
            color: #777287 !important;
            border-color: #39334d !important;
        }

        [data-testid="stExpander"] {
            background: #101019;
            border: 1px solid #29293b;
            border-radius: 12px;
        }

        [data-testid="stExpander"] summary {
            color: #ededf7 !important;
        }

        [data-testid="stAlert"] {
            background: #141421;
            border: 1px solid #34344a;
            border-radius: 12px;
            color: #f5f5fa;
        }

        [data-testid="stProgressBar"] > div {
            background: #29293c;
            border-radius: 20px;
        }

        [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(
                90deg,
                #7650ec,
                #b38aff
            ) !important;
            border-radius: 20px;
        }

        [data-testid="stStatusWidget"] {
            background: #11111b;
            border: 1px solid #29293b;
            border-radius: 12px;
        }

        hr {
            border-color: #28283a !important;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        a {
            color: #b6a0ff !important;
        }

        code, pre {
            background: #101019 !important;
            color: #d8caff !important;
            border: 1px solid #28283a;
            border-radius: 8px;
        }

        [data-testid="stCode"] {
            background: #101019 !important;
        }

        [data-testid="stTable"],
        [data-testid="stDataFrame"] {
            background: #101019 !important;
        }

        [data-testid="stVideo"] {
            border: 1px solid #34344a;
            border-radius: 12px;
            overflow: hidden;
        }

        .hero {
            padding: 34px;
            border-radius: 22px;
            background:
                radial-gradient(
                    circle at 85% 15%,
                    rgba(130, 87, 245, 0.23),
                    transparent 32%
                ),
                linear-gradient(
                    135deg,
                    #151321 0%,
                    #101019 55%,
                    #11101c 100%
                );
            border: 1px solid #302744;
            margin-bottom: 26px;
        }

        .hero-eyebrow {
            color: #b7a1ff;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(2rem, 4vw, 3.3rem);
            line-height: 1.1;
            letter-spacing: -1.8px;
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 16px;
        }

        .hero-copy {
            color: #bdb9d0;
            font-size: 1.03rem;
            max-width: 760px;
            line-height: 1.7;
        }

        .tag {
            display: inline-block;
            padding: 6px 11px;
            margin: 4px 5px 0 0;
            background: #211b35;
            color: #d5c7ff;
            border: 1px solid #443464;
            border-radius: 100px;
            font-size: 0.76rem;
            font-weight: 600;
        }

        .section-label {
            color: #a994ff;
            text-transform: uppercase;
            letter-spacing: 1.6px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .muted {
            color: #9999b1;
            font-size: 0.88rem;
        }

        .sidebar-brand {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .sidebar-subtitle {
            color: #9f9db5;
            font-size: 0.83rem;
            margin-bottom: 20px;
        }

        .status-pill {
            display: inline-block;
            background: #18291f;
            border: 1px solid #28583a;
            color: #8ce6a7;
            border-radius: 100px;
            padding: 5px 10px;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .footer {
            color: #77778f;
            font-size: 0.78rem;
            text-align: center;
            padding: 22px 0 0 0;
        }

        @media (max-width: 768px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1rem;
            }

            .hero {
                padding: 22px;
            }

            .hero-title {
                letter-spacing: -1px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_dark_theme()


# ============================================================
# SESSION STATE
# ============================================================

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

if "last_job_id" not in st.session_state:
    st.session_state["last_job_id"] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_json(response: requests.Response) -> dict:
    """Return a JSON dictionary, or raise a readable API error."""
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError(
            f"The backend returned a non-JSON response "
            f"(HTTP {response.status_code})."
        )

    if not response.ok:
        detail = data.get("detail", data)
        raise RuntimeError(
            f"API error {response.status_code}: {detail}"
        )

    if not isinstance(data, dict):
        raise RuntimeError("The backend returned an unexpected response.")

    return data


def make_absolute_url(base: str, path: str | None) -> str | None:
    """Convert an API-relative URL into a full URL."""
    if not path:
        return None

    if path.startswith(("http://", "https://")):
        return path

    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def extract_job_id(data: dict) -> str | None:
    """Extract a job ID from common API response formats."""
    if not isinstance(data, dict):
        return None

    for key in ("job_id", "id", "task_id"):
        if data.get(key):
            return str(data[key])

    for key in ("job", "data", "result"):
        nested = data.get(key)
        if isinstance(nested, dict):
            found = extract_job_id(nested)
            if found:
                return found

    return None


def extract_status(data: dict) -> str:
    """Extract status from a job response."""
    if not isinstance(data, dict):
        return "unknown"

    status = data.get("status")
    if status:
        return str(status).lower()

    for key in ("job", "data", "result"):
        nested = data.get(key)
        if isinstance(nested, dict):
            status = extract_status(nested)
            if status != "unknown":
                return status

    return "unknown"


def get_nested_result(data: dict) -> dict:
    """Unwrap common response envelopes without losing job metadata."""
    current = data

    for _ in range(3):
        if not isinstance(current, dict):
            return {}

        nested = current.get("result")

        if isinstance(nested, dict) and (
            "videos" in nested
            or "outputs" in nested
            or "files" in nested
            or "artifacts" in nested
            or "captions_url" in nested
        ):
            return nested

        if isinstance(nested, dict):
            current = nested
        else:
            break

    return current if isinstance(current, dict) else {}


def show_outputs(base: str, data: dict):
    """Display generated videos and downloadable supporting files."""
    output_data = get_nested_result(data)

    st.markdown("### Your generated outputs")
    st.caption(
        "Preview the rendered video and open or download the supporting files."
    )

    videos = output_data.get("videos", [])

    if isinstance(videos, dict):
        videos = [videos]

    if isinstance(videos, list) and videos:
        for index, video in enumerate(videos, start=1):
            if not isinstance(video, dict):
                continue

            video_url = make_absolute_url(
                base,
                video.get("download_url")
                or video.get("url")
                or video.get("path"),
            )

            aspect = video.get("aspect_ratio", "Video")
            duration = video.get("duration_seconds")

            heading = f"{aspect} video"
            if duration is not None:
                try:
                    heading += f" · {float(duration):.1f} seconds"
                except (TypeError, ValueError):
                    pass

            st.markdown(f"#### {heading}")

            if video_url:
                st.video(video_url)

                st.link_button(
                    f"Download {aspect} video",
                    video_url,
                    key=f"download_video_{index}",
                    use_container_width=True,
                )

    # Support alternate output formats from other API versions.
    output_items = []

    for key in ("outputs", "files", "artifacts"):
        value = output_data.get(key)

        if isinstance(value, list):
            output_items.extend(value)
        elif isinstance(value, dict):
            for name, item in value.items():
                if isinstance(item, dict):
                    item.setdefault("name", name)
                    output_items.append(item)
                elif isinstance(item, str):
                    output_items.append(
                        {"name": name, "url": item}
                    )

    if output_items:
        st.markdown("#### Additional files")

        for index, item in enumerate(output_items, start=1):
            if isinstance(item, str):
                item = {"url": item, "name": f"Output {index}"}

            if not isinstance(item, dict):
                continue

            file_url = make_absolute_url(
                base,
                item.get("download_url")
                or item.get("url")
                or item.get("href"),
            )

            label = (
                item.get("name")
                or item.get("filename")
                or item.get("type")
                or f"Output {index}"
            )

            if file_url:
                st.markdown(f"- [{label}]({file_url})")

    supporting_files = [
        ("captions_url", "Download captions (SRT)"),
        ("timeline_url", "View scene timeline (JSON)"),
        ("manifest_url", "View run manifest (JSON)"),
    ]

    available_supporting_files = []

    for key, label in supporting_files:
        url = make_absolute_url(base, output_data.get(key))
        if url:
            available_supporting_files.append((label, url))

    if available_supporting_files:
        st.markdown("#### Project files")

        columns = st.columns(len(available_supporting_files))

        for column, (label, url) in zip(
            columns, available_supporting_files
        ):
            with column:
                st.link_button(
                    label,
                    url,
                    use_container_width=True,
                )

    if not videos and not output_items and not available_supporting_files:
        st.warning(
            "The job completed, but no output links were found in the "
            "response. Check the API response below."
        )

        with st.expander("Inspect API response"):
            st.json(data)


def check_backend(base: str) -> tuple[bool, str]:
    """Check whether the API is reachable."""
    try:
        response = requests.get(
            f"{base.rstrip('/')}/health",
            timeout=10,
        )

        if response.ok:
            return True, "Backend connected"

        return False, f"Backend returned HTTP {response.status_code}"

    except requests.RequestException as exc:
        return False, str(exc)


def create_job(
    base: str,
    script: str,
    aspect_ratio: str,
    voice: str,
    burn_captions: bool,
    avoid_terms: str,
) -> dict:
    """Submit a video generation request to the existing backend."""
    payload: dict[str, Any] = {
        "script": script,
        "aspect_ratio": aspect_ratio,
        "voice": voice,
        "burn_captions": burn_captions,
    }

    if avoid_terms.strip():
        payload["avoid_terms"] = [
            term.strip()
            for term in avoid_terms.split(",")
            if term.strip()
        ]

    response = requests.post(
        f"{base.rstrip('/')}/api/v1/broll/jobs",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    return parse_json(response)


def upload_job(
    base: str,
    uploaded_file,
    aspect_ratio: str,
    voice: str,
    burn_captions: bool,
    avoid_terms: str,
) -> dict:
    """Submit an uploaded script or audio file to the backend."""
    payload = {
        "aspect_ratio": aspect_ratio,
        "voice": voice,
        "burn_captions": str(burn_captions).lower(),
    }

    if avoid_terms.strip():
        payload["avoid_terms"] = avoid_terms

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    response = requests.post(
        f"{base.rstrip('/')}/api/v1/broll/jobs/upload",
        data=payload,
        files=files,
        timeout=REQUEST_TIMEOUT,
    )

    return parse_json(response)


def get_job(base: str, job_id: str) -> dict:
    """Retrieve the current job state."""
    response = requests.get(
        f"{base.rstrip('/')}/api/v1/jobs/{job_id}",
        timeout=30,
    )

    return parse_json(response)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">✦ B-roll Studio</div>
        <div class="sidebar-subtitle">
            IncuBrix 2027 · Problem Statement 3
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("#### Backend configuration")

    api_base = st.text_input(
        "API base URL",
        value=DEFAULT_API,
        help=(
            "Local example: http://localhost:8000. "
            "For deployment, enter your deployed backend URL."
        ),
    ).strip().rstrip("/")

    if st.button("Check connection", use_container_width=True):
        with st.spinner("Checking backend..."):
            connected, message = check_backend(api_base)

        if connected:
            st.success(message)
        else:
            st.error(message)

    st.markdown("---")

    st.markdown("#### Pipeline")
    st.markdown(
        """
        <div class="muted">
        01 · Script processing<br>
        02 · Semantic footage retrieval<br>
        03 · Narration generation<br>
        04 · Timeline and captions<br>
        05 · FFmpeg rendering
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="muted">
        <span class="status-pill">PS3 · Video Engine</span><br><br>
        Create narrated videos from scripts using relevant B-roll,
        captions and automated rendering.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">
            INCUBRIX 2027 · CREATIVE AUTOMATION
        </div>
        <div class="hero-title">
            From words to<br>watchable stories.
        </div>
        <div class="hero-copy">
            Turn a script into a narrated, captioned B-roll video.
            Generate relevant footage selections, render your video,
            and access the finished files from one workspace.
        </div>
        <div style="margin-top: 18px;">
            <span class="tag">Semantic Search</span>
            <span class="tag">AI Narration</span>
            <span class="tag">Auto Captions</span>
            <span class="tag">FFmpeg Rendering</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP METRICS
# ============================================================

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Workflow", "Automated")

with metric2:
    st.metric("Video output", "MP4")

with metric3:
    st.metric("Render engine", "FFmpeg")


st.markdown("---")


# ============================================================
# MAIN INPUT AREA
# ============================================================

left, right = st.columns([1.45, 1], gap="large")

with left:
    st.markdown(
        '<div class="section-label">01 / Your content</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Give your story a starting point")

    input_mode = st.radio(
        "Input method",
        ["Write or paste a script", "Upload a file"],
        horizontal=True,
    )

    script = ""
    uploaded_file = None

    if input_mode == "Write or paste a script":
        script = st.text_area(
            "Video script",
            height=280,
            placeholder=(
                "Paste your narration script here...\n\n"
                "Example:\n"
                "Every day, millions of people rely on clean water. "
                "But for many communities, access is still a challenge..."
            ),
            help="Enter the narration you want the video to communicate.",
        )

        word_count = len(script.split()) if script.strip() else 0
        estimated_minutes = word_count / 130 if word_count else 0

        count_col, time_col = st.columns(2)

        with count_col:
            st.metric("Word count", word_count)

        with time_col:
            st.metric(
                "Estimated narration",
                f"{estimated_minutes:.1f} min",
            )

    else:
        uploaded_file = st.file_uploader(
            "Upload your script or audio",
            type=["txt", "md", "wav", "mp3", "m4a", "mp4"],
            help=(
                "Supported formats depend on your backend upload endpoint. "
                "Text and audio files are the intended inputs."
            ),
        )

        if uploaded_file:
            st.success(
                f"Selected: {uploaded_file.name} "
                f"({uploaded_file.size / 1024:.1f} KB)"
            )

            if uploaded_file.type.startswith("text/") or (
                uploaded_file.name.lower().endswith((".txt", ".md"))
            ):
                try:
                    script = uploaded_file.getvalue().decode("utf-8")
                except UnicodeDecodeError:
                    st.warning(
                        "This text file is not UTF-8 encoded. "
                        "Upload a UTF-8 text file."
                    )


with right:
    st.markdown(
        '<div class="section-label">02 / Creative direction</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Shape the final video")

    aspect_ratio = st.selectbox(
        "Output format",
        options=["16:9", "9:16", "1:1"],
        index=0,
        help=(
            "16:9 for landscape, 9:16 for vertical, "
            "and 1:1 for square videos."
        ),
    )

    voice = st.selectbox(
        "Narration voice",
        options=[
            "en-US-AriaNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
        ],
        index=0,
        help=(
            "The backend must support the selected voice. "
            "These are Edge TTS voice identifiers."
        ),
    )

    burn_captions = st.checkbox(
        "Burn captions into the video",
        value=True,
        help="If supported by the backend, captions appear directly in the video.",
    )

    avoid_terms = st.text_input(
        "Avoid footage containing",
        placeholder="e.g. logos, blurry shots, watermarks",
        help="Separate terms with commas.",
    )

    with st.expander("Generation notes"):
        st.markdown(
            """
            - Use a clear, descriptive script for more relevant footage.
            - The semantic retrieval model ranks candidate footage.
            - Footage availability depends on the configured provider and API.
            - Always review footage licensing and attribution before publishing.
            """
        )


# ============================================================
# GENERATION CONTROLS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-label">03 / Generate</div>',
    unsafe_allow_html=True,
)
st.markdown("### Bring your story to life")

st.caption(
    "Generation time depends on script length, footage retrieval, "
    "narration and video rendering."
)

button_col, info_col = st.columns([1, 2], vertical_alignment="center")

with button_col:
    generate_clicked = st.button(
        "✦  Generate video",
        type="primary",
        use_container_width=True,
    )

with info_col:
    st.markdown(
        '<div class="muted">The finished video and supporting project files '
        'will appear below when processing is complete.</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SUBMIT AND POLL
# ============================================================

if generate_clicked:
    if not api_base:
        st.error("Enter a backend API URL in the sidebar.")
        st.stop()

    if input_mode == "Write or paste a script" and not script.strip():
        st.error("Please enter a script before generating a video.")
        st.stop()

    if input_mode == "Upload a file" and uploaded_file is None:
        st.error("Please upload a file before generating a video.")
        st.stop()

    progress = st.progress(0, text="Preparing your request...")
    status_box = st.status(
        "Starting the video pipeline...",
        expanded=True,
    )

    try:
        with status_box:
            st.write("Connecting to the backend...")

            connected, connection_message = check_backend(api_base)

            if not connected:
                raise RuntimeError(
                    "Cannot connect to the backend. "
                    f"{connection_message}"
                )

            progress.progress(5, text="Submitting job...")

            if input_mode == "Upload a file":
                job_response = upload_job(
                    api_base,
                    uploaded_file,
                    aspect_ratio,
                    voice,
                    burn_captions,
                    avoid_terms,
                )
            else:
                job_response = create_job(
                    api_base,
                    script,
                    aspect_ratio,
                    voice,
                    burn_captions,
                    avoid_terms,
                )

            job_id = extract_job_id(job_response)

            if not job_id:
                st.session_state["last_result"] = job_response
                raise RuntimeError(
                    "The backend did not return a job ID. "
                    "Inspect the submission response below."
                )

            st.session_state["last_job_id"] = job_id

            st.write(f"Job created: `{job_id}`")
            progress.progress(10, text="Job submitted successfully...")

            result = job_response
            final_status = extract_status(job_response)

            # Poll only while the job is still processing.
            for attempt in range(MAX_POLL_ATTEMPTS):
                if final_status in {
                    "succeeded",
                    "success",
                    "completed",
                    "complete",
                    "failed",
                    "error",
                    "cancelled",
                    "canceled",
                }:
                    break

                time.sleep(POLL_INTERVAL)

                result = get_job(api_base, job_id)
                final_status = extract_status(result)

                percent = min(
                    95,
                    10 + int(
                        85 * (attempt + 1) / MAX_POLL_ATTEMPTS
                    ),
                )

                progress.progress(
                    percent,
                    text=f"Processing video... Status: {final_status}",
                )

            st.session_state["last_result"] = result

            if final_status in {
                "succeeded",
                "success",
                "completed",
                "complete",
            }:
                progress.progress(100, text="Generation complete")
                status_box.update(
                    label="Your video is ready",
                    state="complete",
                    expanded=False,
                )

                st.success("Video generation completed successfully.")

            elif final_status in {"failed", "error"}:
                status_box.update(
                    label="Video generation failed",
                    state="error",
                    expanded=True,
                )

                error_message = (
                    result.get("error")
                    or result.get("detail")
                    or "The backend reported a failed job."
                )

                st.error(str(error_message))

            elif final_status in {"cancelled", "canceled"}:
                status_box.update(
                    label="Video generation was cancelled",
                    state="error",
                    expanded=True,
                )
                st.warning("The job was cancelled.")

            else:
                status_box.update(
                    label="Generation is taking longer than expected",
                    state="running",
                    expanded=True,
                )

                st.warning(
                    "The job has not reached a final status yet. "
                    "You can check its latest status below."
                )

    except requests.Timeout:
        status_box.update(
            label="Request timed out",
            state="error",
            expanded=True,
        )

        st.error(
            "The request timed out. If the backend is hosted on a free "
            "service, it may be waking up or rendering a long video. "
            "Check the backend logs and the job status before submitting "
            "the same job again."
        )

    except requests.RequestException as exc:
        status_box.update(
            label="Could not reach the backend",
            state="error",
            expanded=True,
        )

        st.error(f"Network error: {exc}")

    except Exception as exc:
        status_box.update(
            label="Something went wrong",
            state="error",
            expanded=True,
        )

        st.error(str(exc))

        if st.session_state.get("last_result"):
            with st.expander("Inspect last API response"):
                st.json(st.session_state["last_result"])


# ============================================================
# RESULTS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-label">04 / Results</div>',
    unsafe_allow_html=True,
)
st.markdown("### Your video workspace")

last_result = st.session_state.get("last_result")

if last_result:
    job_id = (
        st.session_state.get("last_job_id")
        or extract_job_id(last_result)
    )

    if job_id:
        st.caption(f"Job ID: {job_id}")

    current_status = extract_status(last_result)

    if current_status in {
        "succeeded",
        "success",
        "completed",
        "complete",
    }:
        show_outputs(api_base, last_result)

    elif current_status in {"failed", "error"}:
        st.error("The most recent job failed.")

        with st.expander("View error details", expanded=True):
            st.json(last_result)

    else:
        st.info(
            f"Latest job status: **{current_status}**. "
            "If the job is still running, refresh the status below."
        )

        if job_id and st.button(
            "Refresh job status",
            use_container_width=False,
        ):
            try:
                refreshed = get_job(api_base, job_id)
                st.session_state["last_result"] = refreshed
                st.rerun()
            except Exception as exc:
                st.error(f"Could not refresh job: {exc}")

        with st.expander("View current API response"):
            st.json(last_result)

else:
    st.markdown(
        """
        <div style="
            background: #101019;
            border: 1px dashed #37374c;
            border-radius: 16px;
            padding: 34px;
            text-align: center;
        ">
            <div style="font-size: 2.3rem; margin-bottom: 10px;">🎞️</div>
            <div style="
                color: #f5f5fa;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.15rem;
                font-weight: 600;
            ">
                Your next story starts here
            </div>
            <div style="
                color: #9999b1;
                margin-top: 8px;
                font-size: 0.9rem;
            ">
                Add a script, choose your creative settings,
                and generate your first video.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        IncuBrix 2027 · PS3 B-roll Video Engine<br>
        Built with Streamlit, FastAPI, semantic retrieval and FFmpeg
    </div>
    """,
    unsafe_allow_html=True,
)
