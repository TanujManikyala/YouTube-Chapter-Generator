import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
import re
import os
import dotenv
import urllib.parse

dotenv.load_dotenv()

st.set_page_config(
    page_title="YouTube Chapter Generator",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------
# ROYAL LIGHT THEME + ANIMATIONS
# ---------------------------
st.markdown(
    """
<style>
:root {
  --bg-1: #fbfcfd;
  --bg-2: #ffffff;
  --text: #081425;
  --muted: #6b7280;
  --accent: #5b21b6;     /* royal purple */
  --accent-2: #0ea5e9;   /* cyan */
  --card: #ffffff;
  --border: rgba(8,20,37,0.06);
}

/* Page */
.stApp {
  background: linear-gradient(180deg, var(--bg-1), var(--bg-2));
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  padding-bottom: 48px;
}

/* Hero */
.hero {
  padding: 32px 16px;
}
.hero h1 {
  font-size: 36px;
  margin: 0;
  font-weight: 900;
  background: linear-gradient(90deg,var(--accent),var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p {
  margin: 8px 0 0 0;
  color: var(--muted);
}

/* Controls card */
.card {
  background: var(--card);
  border-radius: 14px;
  padding: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 10px 30px rgba(8,20,37,0.04);
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
  background: #fbfdff !important;
  border-radius: 10px !important;
  border: 1px solid var(--border) !important;
  padding: 10px !important;
}

/* Button styles */
.stButton > button {
  background: linear-gradient(90deg,var(--accent),var(--accent-2));
  color: white;
  border-radius: 12px;
  padding: 10px 18px;
  font-weight: 800;
  box-shadow: 0 10px 30px rgba(91,33,182,0.12);
  transition: transform .13s ease, box-shadow .13s ease;
}
.stButton > button:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 40px rgba(91,33,182,0.18);
}

/* Chapter card */
.chapter {
  border-radius: 10px;
  padding: 12px;
  border: 1px solid var(--border);
  background: linear-gradient(180deg,#ffffff,#fbfdff);
  margin-bottom: 10px;
  transition: transform .16s ease, box-shadow .16s ease;
}
.chapter:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(8,20,37,0.06); }
.chapter-time { color: var(--accent); font-weight: 800; font-size: 13px; }
.chapter-desc { margin-top: 6px; color: var(--text); font-size: 14px; }

/* Play button small */
.play-btn {
  background: transparent;
  border: 1px solid rgba(8,20,37,0.06);
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background .12s ease, transform .12s ease;
}
.play-btn:hover { background: rgba(91,33,182,0.06); transform: translateY(-2px); }

/* Transcript line */
.trans-line { padding: 6px; border-radius: 8px; }
.trans-line:hover { background: rgba(14,165,233,0.04); }

/* small muted text */
.small-muted { color: var(--muted); font-size: 13px; }

/* Expander */
[data-testid="stExpandable"] { border-radius: 10px; background: #fff; border: 1px solid var(--border); }

/* responsive iframe container */
.video-wrap { border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
</style>
""",
    unsafe_allow_html=True
)

# ---------------------------
# HERO
# ---------------------------
st.markdown(
    """
<div class="hero">
  <h1>YouTube Chapter Generator</h1>
  <p>Create royal, interactive, clickable YouTube chapters with Gemini — preview & play inside the app.</p>
</div>
""",
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar - API key + model
# ---------------------------
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY"))
model_name = "models/gemini-2.5-flash-lite"
st.sidebar.markdown(f"**Model:** `{model_name}`")
client = genai.Client(api_key=api_key) if api_key else None

# ---------------------------
# Inputs (search removed)
# ---------------------------
col_left, col_right = st.columns([3, 1])
with col_left:
    youtube_url = st.text_input(
        "🎥 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID"
    )

with col_right:
    st.write("")
    generate = st.button("✨ Generate Chapters")
    st.markdown("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Utilities**")
    st.caption("After generating, use Play buttons to preview in the embedded player.")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Helpers (unchanged logic, extended for interactivity)
# ---------------------------
def extract_video_id(url: str):
    if not url:
        return None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&/]|$)',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def format_time_seconds(sec: int):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def parse_time_to_seconds(t: str):
    if not t:
        return None
    parts = t.strip().split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    return None

def get_transcript(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        try:
            return transcript.to_raw_data()
        except Exception:
            return transcript
    except Exception as e:
        return str(e)

def generate_timemarks(transcript_list):
    if client is None:
        return "Error: Gemini client not initialized. Add your API key in the sidebar."
    # build transcript string safely (preprocess)
    transcript_text = ""
    for item in transcript_list:
        start = int(item.get("start", 0))
        clean_text = item.get("text", "").replace("\n", " ")
        transcript_text += f"[{format_time_seconds(start)}] {clean_text}\n"

    prompt = f"""
You are an expert at creating concise, well-structured YouTube chapters.

Output rules:
- Output only lines in the form: Start - End Description
- Use M:SS or H:MM:SS time formats (no leading zeros on hours)
- Group related segments into a single chapter where appropriate
- Do not add headings, markdown, or extra commentary

Transcript:
{transcript_text}
"""
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = getattr(response, "text", None)
        return text if text is not None else str(response)
    except Exception as e:
        return f"Error generating chapters: {e}"

def render_chapters_and_interactions(chapter_text: str, video_id: str):
    """
    Renders chapter cards with Play buttons that update the embedded player via session_state.
    Also builds a YouTube description-ready lines list for export/copy.
    """
    lines = [l.strip() for l in chapter_text.splitlines() if l.strip()]
    yt_desc_lines = []
    # iterate and create UI; use unique keys for buttons
    for i, line in enumerate(lines):
        m = re.match(r'^\s*([\d:]+)\s*[-–—]\s*([\d:]+)\s*(.*)$', line)
        if not m:
            continue
        start_raw, end_raw, desc = m.groups()
        start_seconds = parse_time_to_seconds(start_raw)
        if start_seconds is None:
            continue
        # prepare yt desc line
        yt_desc_lines.append(f"{start_raw} - {desc}")
        # layout per chapter: two columns (info + action)
        cols = st.columns([1, 0.28])
        with cols[0]:
            st.markdown(
                f"""
                <div class="chapter">
                    <div class="chapter-time">{start_raw} – {end_raw}</div>
                    <div class="chapter-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with cols[1]:
            # Play in-app: set session_state iframe source to embed with start and autoplay
            play_key = f"play_ch_{i}"
            if st.button("Play ▶", key=play_key):
                st.session_state['iframe_src'] = f"https://www.youtube.com/embed/{video_id}?start={start_seconds}&autoplay=1"
    return "\n".join(yt_desc_lines)

# ---------------------------
# Initialize session_state values if missing
# ---------------------------
if 'iframe_src' not in st.session_state:
    st.session_state['iframe_src'] = ""

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None

if 'chapters_text' not in st.session_state:
    st.session_state['chapters_text'] = ""

# ---------------------------
# Generate / Fetch flow
# ---------------------------
if generate:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not youtube_url:
        st.error("Please enter a YouTube URL.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Could not extract a YouTube video ID. Check the URL.")
        else:
            # set iframe to base embed initially
            st.session_state['iframe_src'] = f"https://www.youtube.com/embed/{video_id}"
            # fetch transcript
            with st.spinner("Fetching transcript..."):
                transcript = get_transcript(video_id)
            if isinstance(transcript, list):
                st.session_state['transcript'] = transcript
                # show preview + transcript + search results + interactive chapters in a two-column layout
                left_col, right_col = st.columns([1.45, 1])

                # LEFT: player + transcript search results
                with left_col:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### ▶ Video Preview")
                    # embed iframe from session_state (updates when Play buttons are clicked)
                    iframe_src = st.session_state.get('iframe_src', f"https://www.youtube.com/embed/{video_id}")
                    st.markdown(
                        f'<div class="video-wrap"><iframe width="100%" height="360" src="{iframe_src}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Transcript expander + search results
                    with st.expander("📄 View Full Transcript", expanded=False):
                        full_text = " ".join([item.get("text", "") for item in transcript])
                        st.text_area("Raw Transcript", value=full_text, height=260)

                # RIGHT: chapters & utilities
                with right_col:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### 📌 Clickable Chapters")
                    with st.spinner("Generating chapters (Gemini)..."):
                        chapters = generate_timemarks(transcript)
                    # store raw chapters in session state
                    st.session_state['chapters_text'] = chapters if isinstance(chapters, str) else str(chapters)
                    if isinstance(st.session_state['chapters_text'], str) and st.session_state['chapters_text'].startswith("Error"):
                        st.error(st.session_state['chapters_text'])
                    else:
                        # render interactive chapter cards
                        yt_desc = render_chapters_and_interactions(st.session_state['chapters_text'], video_id)
                        # Copy to clipboard button (JS uses encoded text)
                        encoded = urllib.parse.quote(yt_desc)
                        copy_button_html = f"""
                        <button class="play-btn" onclick="(function(){{ navigator.clipboard.writeText(decodeURIComponent('{encoded}')); this.innerText='Copied ✓'; }})();">Copy chapters</button>
                        """
                        st.markdown(copy_button_html, unsafe_allow_html=True)
                        # download button
                        st.download_button("⬇️ Export as .txt", data=yt_desc, file_name=f"yt_chapters_{video_id}.txt", mime="text/plain")
                        # raw model output expander
                        with st.expander("🧾 Model output (raw)", expanded=False):
                            st.text_area("Model Output (raw)", value=st.session_state['chapters_text'], height=200)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Could not retrieve transcript. Details: {transcript}")

# If iframe_src exists but user didn't press generate in this run (persistent play)
# show the current iframe above results area when present (non-intrusive)
elif st.session_state.get('iframe_src'):
    # basic interface showing current player + small instructions
    col_l, col_r = st.columns([1.6, 1])
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ▶ Current Preview")
        iframe_src = st.session_state['iframe_src']
        st.markdown(f'<div class="video-wrap"><iframe width="100%" height="360" src="{iframe_src}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Actions")
        st.write("Use the search box and Generate button to fetch transcript & chapters.")
        st.markdown("</div>", unsafe_allow_html=True)
