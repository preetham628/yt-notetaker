## Overview

Generate DOCX notes from YouTube playlists or single videos. Includes a Typer CLI and a Streamlit UI. Optionally uses an LLM to create structured outlines aligned with the video flow.

## Installation

- With pip (editable):

```bash
pip install -e .
```

- With uv:

```bash
uv pip install -e .
```

Python 3.10+ is required.

## Configuration

For LLM features, set your OpenAI API key (if using `langchain-openai`):

```bash
export OPENAI_API_KEY=sk-...
```

## CLI

After installation, use the CLI (entry points the root `main.py`):

```bash
yt-notetaker generate "https://youtube.com/playlist?list=..." -o playlists_docx
yt-notetaker generate-single "https://www.youtube.com/watch?v=..." -o playlists_docx
```

Or run from the repo root without installing:

```bash
python main.py generate "https://youtube.com/playlist?list=..."
```

## Streamlit app

```bash
streamlit run streamlit_app.py
```

Paste playlist URLs (one per line) or a single video URL, adjust options, and click Generate.

## Notes

- Subtitles are fetched via `yt-dlp` and downloaded from YouTube. If a video has neither manual nor auto English captions, the transcript will say "Transcript not available.".
- Output DOCX files are saved under `playlists_docx/` by default.

