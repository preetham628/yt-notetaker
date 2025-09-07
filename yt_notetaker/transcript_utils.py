import re
from typing import Dict, List, Optional, Tuple

import requests
from yt_dlp import YoutubeDL


YDL_BASE_OPTS = {
    'quiet': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    'ignoreerrors': True,
}


def get_playlist_info(playlist_url: str) -> Dict:
    with YoutubeDL({'quiet': True}) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
    return playlist_info


def get_video_info(video_url: str) -> Dict:
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
    return info


def get_video_transcript(video_url: str) -> str:
    with YoutubeDL(YDL_BASE_OPTS) as ydl:
        info = ydl.extract_info(video_url, download=False)

    requested_subtitles = info.get('requested_subtitles') or {}
    en_sub = requested_subtitles.get('en') if isinstance(requested_subtitles, dict) else None
    if en_sub and en_sub.get('url'):
        response = requests.get(en_sub['url'], timeout=30)
        if response.ok:
            return response.text

    automatic_captions = info.get('automatic_captions') or {}
    en_auto_list = automatic_captions.get('en') if isinstance(automatic_captions, dict) else None
    if en_auto_list and isinstance(en_auto_list, list) and len(en_auto_list) > 0:
        sub_url = en_auto_list[0].get('url')
        if sub_url:
            response = requests.get(sub_url, timeout=30)
            if response.ok:
                return response.text

    return "Transcript not available."


def captions_to_plaintext(captions_text: str) -> str:
    if not captions_text:
        return ""
    text = captions_text
    text = re.sub(r"^WEBVTT.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d{1,2}:\d{2}:\d{2}[\.,]\d{1,3}\s+-->.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d{1,2}:\d{2}[\.,]\d{1,3}\s+-->.*$", "", text, flags=re.MULTILINE)  # hh:mm.mmm -->
    text = re.sub(r"^\s*NOTE.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_timestamp_to_seconds(ts: str) -> Optional[float]:
    ts = ts.strip()
    m = re.match(r"^(\d{2}):(\d{2}):(\d{2})[\.,](\d{1,3})$", ts)
    if m:
        h, mnt, s, ms = m.groups()
        return int(h) * 3600 + int(mnt) * 60 + int(s) + int(ms) / 1000.0
    m = re.match(r"^(\d{2}):(\d{2})[\.,](\d{1,3})$", ts)
    if m:
        mnt, s, ms = m.groups()
        return int(mnt) * 60 + int(s) + int(ms) / 1000.0
    m = re.match(r"^(\d{2}):(\d{2}):(\d{2})$", ts)
    if m:
        h, mnt, s = m.groups()
        return int(h) * 3600 + int(mnt) * 60 + int(s)
    return None


def captions_to_segments(captions_text: str, segment_seconds: int = 1800) -> List[Tuple[int, int, str]]:
    """
    Roughly bucket caption cues into segments of segment_seconds length based on cue start times.
    Returns list of (segment_index, segment_start_seconds, text) where text is concatenated lines for that bucket.
    """
    if not captions_text:
        return []

    lines = captions_text.splitlines()
    current_start: Optional[float] = None
    buckets: Dict[int, List[str]] = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match VTT/SRT timestamp lines
        if '-->' in line:
            parts = [p.strip() for p in line.split('-->')]
            if len(parts) >= 1:
                start_s = _parse_timestamp_to_seconds(parts[0])
                if start_s is not None:
                    current_start = start_s
                    continue
        # If caption text line
        if current_start is None:
            # Skip header / noise
            continue
        seg_index = int(current_start // segment_seconds)
        # Strip tags
        clean = re.sub(r"<[^>]+>", "", line)
        buckets.setdefault(seg_index, []).append(clean)

    # Convert to list in order of segment index
    results: List[Tuple[int, int, str]] = []
    for seg_index in sorted(buckets.keys()):
        start_sec = seg_index * segment_seconds
        text = re.sub(r"\s+", " ", " ".join(buckets[seg_index])).strip()
        results.append((seg_index, start_sec, text))
    return results


