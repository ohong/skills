#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Report which tools and API keys the motion-video skill can use. Never prints secret values.

    uv run scripts/preflight.py

Prints a compact table plus the fallback for each missing item. Always exits 0.
"""
from __future__ import annotations

import os
import shutil
import subprocess

# name, version command, fallback when missing
TOOLS = [
    ("ffmpeg", ["ffmpeg", "-version"], "required: no trims, mixing, loudness, or render without it (brew install ffmpeg)"),
    ("ffprobe", ["ffprobe", "-version"], "required: ships with ffmpeg (brew install ffmpeg)"),
    ("yt-dlp", ["yt-dlp", "--version"], "no real-footage search or download; use generated shots or captured UI (brew install yt-dlp)"),
    ("uv", ["uv", "--version"], "the helper scripts run through uv; fall back to python3 with fal-client installed (brew install uv)"),
    ("node", ["node", "--version"], "no HyperFrames, Remotion, or Motion Canvas renders"),
    ("npx", ["npx", "--version"], "no HyperFrames, Remotion, or Motion Canvas renders (comes with node)"),
    ("whisper", ["whisper", "--help"], "no local captions; use --backend fal (needs FAL_KEY) or skip captions (pip install openai-whisper via uv tool)"),
    ("manim", ["manim", "--version"], "no Manim scenes; use HyperFrames or Remotion for motion graphics (uv tool install manim)"),
]

KEYS = [
    ("FAL_KEY", "no image, video, or TTS generation; captions use local whisper; render motion graphics and real footage only"),
    ("GEMINI_API_KEY", "no Gemini-based perceptual review (scripts/review_video.py) and no direct-Gemini TTS fallback; TTS goes through Fal"),
    ("SUNO_API_KEY", "music from Fal instead: fal-ai/elevenlabs/music via scripts/fal_run.py (needs FAL_KEY), or a licensed track"),
]


def version(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return "found (version unknown)"
    text = (proc.stdout or proc.stderr).strip().splitlines()
    return text[0][:60] if text else "found"


FILTERS = [
    ("ffmpeg ass filter", "ass", "no caption burn-in; deliver .srt/.vtt sidecars only (needs an ffmpeg built with libass, e.g. the homebrew-ffmpeg/ffmpeg tap)"),
    ("ffmpeg drawtext", "drawtext", "animatic slates render without text (needs an ffmpeg built with freetype)"),
]


def ffmpeg_filters() -> set[str]:
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {line.split()[1] for line in out.splitlines() if len(line.split()) > 2}


def main() -> int:
    rows, fallbacks = [], []
    filters = ffmpeg_filters() if shutil.which("ffmpeg") else set()
    for name, flt, fallback in FILTERS:
        if flt in filters:
            rows.append((name, "ok", "available"))
        else:
            rows.append((name, "MISSING", "-"))
            fallbacks.append((name, fallback))
    for name, cmd, fallback in TOOLS:
        if shutil.which(name):
            rows.append((name, "ok", version(cmd) if name != "whisper" else "installed"))
        else:
            rows.append((name, "MISSING", "-"))
            fallbacks.append((name, fallback))
    for name, fallback in KEYS:
        if os.environ.get(name):
            rows.append((name, "ok", "set"))
        else:
            rows.append((name, "MISSING", "-"))
            fallbacks.append((name, fallback))
    width = max(len(r[0]) for r in rows)
    print(f"{'item'.ljust(width)}  status   detail")
    for name, status, detail in rows:
        print(f"{name.ljust(width)}  {status.ljust(7)}  {detail}")
    if fallbacks:
        print("\nFallbacks for missing items:")
        for name, fallback in fallbacks:
            print(f"- {name}: {fallback}")
    else:
        print("\nAll items present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
