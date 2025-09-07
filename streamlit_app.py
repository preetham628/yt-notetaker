import os
from typing import List

import streamlit as st

from yt_notetaker.notetaker import generate_playlist_docx, generate_single_video_docx


st.set_page_config(page_title="YouTube Playlist → DOCX", page_icon="📄", layout="centered")

st.title("YouTube Notetaker → DOCX + LLM Notes")
st.write("Enter a playlist or a single video. We'll fetch transcripts and optionally use an LLM to produce structured notes aligned to the video.")

default_output = "playlists_docx"
tab_playlist, tab_single = st.tabs(["Playlist", "Single Video"])

with tab_playlist:
    playlist_text = st.text_area("Playlist URLs", placeholder="https://youtube.com/playlist?list=...\nhttps://youtube.com/playlist?list=...", height=150)
    output_dir = st.text_input("Output directory", value=default_output, key="out_playlist")

with tab_single:
    single_url = st.text_input("Video URL", placeholder="https://www.youtube.com/watch?v=...", key="single_url")
    output_dir_single = st.text_input("Output directory", value=default_output, key="out_single")

with st.expander("LLM settings"):
    use_llm = st.checkbox("Use LLM for outline and notes", value=True)
    model = st.text_input("Model", value="gpt-4o-mini")
    include_raw = st.checkbox("Include raw transcript in DOCX", value=False)

run_playlist = st.button("Generate Playlist DOCX")
run_single = st.button("Generate Single Video DOCX")

if run_playlist:
    urls: List[str] = [u.strip() for u in playlist_text.splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one playlist URL.")
        st.stop()

    os.makedirs(output_dir, exist_ok=True)

    progress = st.progress(0)
    status_area = st.empty()
    results = []
    total = len(urls)

    for idx, url in enumerate(urls, start=1):
        status_area.info(f"Processing playlist {idx}/{total}: {url}")
        try:
            path = generate_playlist_docx(
                url,
                output_dir=output_dir,
                use_llm=use_llm,
                llm_model=model,
                include_raw_transcript=include_raw,
                max_workers=250,
            )
            results.append((url, path, None))
        except Exception as exc:
            results.append((url, None, str(exc)))
        progress.progress(int(idx / total * 100))

    st.subheader("Results")
    for url, path, err in results:
        if err:
            st.error(f"Failed: {url} — {err}")
        elif path and os.path.exists(path):
            st.success(f"Saved: {path}")
            with open(path, "rb") as fh:
                st.download_button(
                    label=f"Download {os.path.basename(path)}",
                    data=fh.read(),
                    file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        else:
            st.warning(f"No file generated for: {url}")

if run_single:
    if not single_url:
        st.warning("Please enter a video URL.")
        st.stop()
    os.makedirs(output_dir_single, exist_ok=True)
    try:
        path = generate_single_video_docx(
            single_url,
            output_dir=output_dir_single,
            use_llm=use_llm,
            llm_model=model,
        )
        st.success(f"Saved: {path}")
        with open(path, "rb") as fh:
            st.download_button(
                label=f"Download {os.path.basename(path)}",
                data=fh.read(),
                file_name=os.path.basename(path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    except Exception as exc:
        st.error(f"Failed: {single_url} — {exc}")


