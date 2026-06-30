"""Build synchronized SRT/VTT subtitles from narration text."""

from __future__ import annotations

import re


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_vtt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def estimate_duration(text: str, speed: float = 1.0) -> float:
    words = len(re.findall(r"\S+", text))
    wps = max(1.2, 2.8 * speed)
    return max(2.0, min(words / wps, 300.0))


def build_srt(text: str, duration_seconds: float, speed: float = 1.0) -> str:
    chunks = _chunk_text(text)
    if not chunks:
        return ""
    total = max(duration_seconds, 1.0)
    chunk_dur = total / len(chunks)
    lines: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        start = (i - 1) * chunk_dur
        end = min(i * chunk_dur, total)
        lines.append(str(i))
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        lines.append(chunk)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_vtt(text: str, duration_seconds: float) -> str:
    srt_body = build_srt(text, duration_seconds).strip()
    if not srt_body:
        return "WEBVTT\n\n"
    blocks = srt_body.split("\n\n")
    out = ["WEBVTT", ""]
    for block in blocks:
        parts = block.split("\n")
        if len(parts) < 3:
            continue
        timing = parts[1].replace(",", ".")
        caption = "\n".join(parts[2:])
        out.append(timing)
        out.append(caption)
        out.append("")
    return "\n".join(out)


def _chunk_text(text: str, max_words: int = 10) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i : i + max_words]))
    return chunks
