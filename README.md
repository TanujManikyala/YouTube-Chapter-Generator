# YouTube Chapter Generator 🎬

**YouTube Chapter Generator** is a Streamlit app that automatically generates concise, well-structured YouTube chapters from a video's transcript using Google Gemini (via `google.genai`). The app fetches the transcript, asks the model to produce time-marked chapter suggestions, renders clickable chapter cards, and allows exporting chapters ready to paste into a YouTube description.

---

## Table of contents

* [Features](#features)
* [Demo / Screenshot](#demo--screenshot)
* [Requirements](#requirements)
* [Quickstart](#quickstart)
* [Configuration / Environment variables](#configuration--environment-variables)
* [How it works (overview)](#how-it-works-overview)
* [Usage](#usage)
* [Project structure](#project-structure)
* [Troubleshooting](#troubleshooting)
* [Security & Privacy](#security--privacy)
* [Contributing](#contributing)
* [License](#license)

---

# Features

* Fetches YouTube transcript using `youtube-transcript-api`.
* Uses Gemini (`google.genai`) to generate concise, grouped chapter time marks.
* Interactive Streamlit UI with:

  * Embedded video preview (play chapters in-app)
  * Clickable chapter cards (auto-start video at chapter time)
  * Copy-to-clipboard & downloadable `.txt` export for description-ready lines
  * Raw model output inspector
* Minimal dependencies and simple setup for local use or deployment.

---

# Demo / Screenshot

*(Replace with an actual screenshot in the repo `assets/` folder if you have one.)*

```
[VIDEO PREVIEW]
▶ Video Preview (embedded)
📌 Clickable Chapters
  0:00 - 1:23 Intro
  1:24 - 4:02 Topic A
  ...
Copy chapters  ⬇️ Export as .txt
```

---

# Requirements

* Python 3.10+ recommended
* See `requirements.txt`. The app depends on:

  * `streamlit`
  * `youtube-transcript-api`
  * `google-genai` (or `google` package that exposes `genai` client)
  * `python-dotenv`

> NOTE: package names sometimes differ between providers; if `google.genai` is unavailable, consult the official Gemini / Google Cloud GenAI SDK docs for the correct package and import path.

---

# Quickstart (local)

1. Clone the repo:

```bash
git clone https://github.com/<your-username>/youtube-chapter-generator.git
cd youtube-chapter-generator
```

2. Create & activate a virtual environment:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file at project root (or set environment vars in your host). Example `.env`:

```env
GEMINI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# (Optional) other env vars if you add them
```

5. Run the app:

```bash
streamlit run app.py
```

6. Open `http://localhost:8501` in your browser.

---

# Configuration / Environment variables

* `GEMINI_API_KEY` — Required if you want to use Google Gemini for chapter generation.

  * Place it in `.env` (project root) or set it as an environment variable.
  * The app reads the key with `dotenv` and shows a secure input in the sidebar.

> No YouTube API key is needed for `youtube-transcript-api` when transcripts are publicly available. For private or special cases you may need to add alternate transcript retrieval logic.

---

# How it works (overview)

1. **User inputs** a YouTube URL.
2. The app extracts the `VIDEO_ID` and fetches the transcript using `YouTubeTranscriptApi`.
3. The transcript is converted into a time-stamped string and sent to Gemini with a clear instruction prompt asking for well-structured chapters.
4. Gemini returns time ranges + descriptions in a strict format.
5. The app parses that output and renders:

   * Clickable chapter cards (play button autostarts the embedded player at the requested timestamp)
   * A description-ready list that can be copied or downloaded as a `.txt` file

---

# Usage notes & tips

* If the model output has formatting errors, check the "Model output (raw)" expander to inspect and, if necessary, manually fix before copying.
* Long videos may produce many segments. The prompt requests grouping related transcript pieces into fewer, concise chapters — adjust the prompt in `generate_timemarks()` if you want more/less granularity.
* If transcripts are not available, `youtube-transcript-api` will throw an error — in such cases you may need to:

  * Provide your own transcript, or
  * Use a speech-to-text service to generate one.

---

# Project structure

```
.
├── app.py                         # Streamlit application
├── requirements.txt               # Python dependencies
├── .env                           # local environment variables (GEMINI_API_KEY)
└── README.md                      # (this file)
```

---

# Troubleshooting

**Transcript fetch fails**

* Public transcripts are required. If the video owner disabled transcripts or it is age-restricted/private, `youtube-transcript-api` may fail. Error details are surfaced in the app.

**Gemini client errors**

* Check `GEMINI_API_KEY` is set and valid.
* Confirm the library `google.genai` version matches the API surface used in `app.py`.
* Inspect raw model response in the app to understand formatting issues.

**Streamlit UI issues**

* Ensure your browser allows embedding YouTube iframes.
* If autoplay does not work, some browsers restrict autoplay; clicking the chapter Play button should still navigate to the timestamp in the embed.

---

# Extending the app

* Add a manual edit UI for chapters before export.
* Provide multiple model choices or adjustable prompt templates (coarse/fine granularity).
* Add support for batch processing of multiple video URLs.
* Add CI / tests for parsing logic & prompt-output validation.
* Add OAuth / user account support if deploying as a public service to manage API keys securely.

---

# Security & Privacy

* **Do not commit** your `.env` or API keys into version control. Add `.env` to `.gitignore`.
* Transcripts fetched are derived from YouTube (public data); confirm you have rights to republish or modify content before sharing.
* API calls to Gemini will send transcript text to the model provider — do not pass sensitive or private content unless you are comfortable with that data being processed by the model provider.

---

# Contributing

Contributions welcome. Suggested workflow:

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/awesome`)
3. Make changes, add tests where appropriate
4. Open a pull request describing the change

Please open issues for bugs or feature requests.

---

# Example `.env` template

```
# .env
GEMINI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

# License

This project is licensed under the **MIT License** — see `LICENSE` (create one if you need to apply a license).

---

If you want, I can:

* Generate a ready-to-commit `README.md` file and include it in the repository layout,
* Add a sample `requirements.txt` tuned to this code,
* Or produce a short `CONTRIBUTING.md` and `LICENSE` file (MIT) for you. Which would you like me to add next?
