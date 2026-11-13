#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fal-client"]
# ///
"""Narration per beat via Fal Gemini TTS.

    uv run scripts/tts.py script.md --out vo/ [--voice Kore] [--style "global note"]
        [--beats B03,B04] [--model google/gemini-3.8-flash-tts] [--force] [--spend-log spend.jsonl]

Parses beats like:
    ## B03 · 0:14–0:22 · "title"
    VO [direction]:
    narration paragraph(s) ...
    ON SCREEN: ...
Writes vo/<beat>.wav and vo/timing.json {beat: {file, duration_s, text, direction}}.
Inline tags such as <sigh> or <short pause> stay in the text.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fal_run  # noqa: E402

DEFAULT_MODEL = "google/gemini-3.8-flash-tts"
HEADER = re.compile(r"^##\s+(B\d+)\s*[·|-]?\s*(.*)$")
TIME = re.compile(r"(\d+):(\d{2}(?:\.\d+)?)\s*[–—-]\s*(\d+):(\d{2}(?:\.\d+)?)")
VO_LINE = re.compile(r"^VO\s*(?:\[(.*)\])?\s*:\s*(.*)$")
STOP = re.compile(r"^(ON SCREEN|MUSIC|SFX)\s*:|^##")


def parse_script(text: str) -> dict[str, dict]:
    """Return {beat_id: {title, start, end, direction, text}} in file order (start/end may be None)."""
    beats: dict[str, dict] = {}
    current = None
    collecting = False
    for raw in text.splitlines():
        line = raw.strip()
        m = HEADER.match(line)
        if m:
            rest = m.group(2)
            t = TIME.search(rest)
            title = re.search(r'["“](.*?)["”]', rest)
            current = {"title": title.group(1) if title else "", "direction": "", "text": "",
                       "start": int(t.group(1)) * 60 + float(t.group(2)) if t else None,
                       "end": int(t.group(3)) * 60 + float(t.group(4)) if t else None}
            beats[m.group(1)] = current
            collecting = False
            continue
        if current is None:
            continue
        v = VO_LINE.match(line)
        if v:
            current["direction"] = (v.group(1) or "").strip()
            current["text"] = v.group(2).strip()
            collecting = True
            continue
        if STOP.match(line):
            collecting = False
            continue
        if collecting and line:
            current["text"] = (current["text"] + "\n" + line).strip()
    return beats


def probe_duration(path: Path) -> float:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=nw=1:nk=1", str(path)], check=True, capture_output=True, text=True).stdout
        return round(float(out.strip()), 3)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as exc:
        raise SystemExit(f"error: ffprobe could not read the duration of {path}: {exc}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script", type=Path)
    p.add_argument("--out", type=Path, default=Path("vo"))
    p.add_argument("--voice", default="Kore")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"default {DEFAULT_MODEL}; lite: google/gemini-3.8-flash-lite-tts")
    p.add_argument("--style", default="", help="global delivery note prepended to every beat's direction")
    p.add_argument("--beats", help="comma-separated beat ids, e.g. B03,B04")
    p.add_argument("--force", action="store_true", help="regenerate beats whose wav exists")
    p.add_argument("--spend-log", type=Path, default=Path("spend.jsonl"))
    p.add_argument("--cap-usd", type=float)
    args = p.parse_args()

    if not args.script.is_file():
        print(f"error: script not found: {args.script}", file=sys.stderr)
        return 1
    beats = parse_script(args.script.read_text())
    wanted = [b.strip() for b in args.beats.split(",")] if args.beats else list(beats)
    unknown = [b for b in wanted if b not in beats]
    if unknown:
        print(f"error: beats not in script: {', '.join(unknown)}", file=sys.stderr)
        return 1
    wanted = [b for b in wanted if beats[b]["text"]]
    if not wanted:
        print("error: no beats with VO text found", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    timing_path = args.out / "timing.json"
    timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}
    failures = []
    for beat in wanted:
        b = beats[beat]
        wav = args.out / f"{beat}.wav"
        direction = ". ".join(s for s in (args.style.strip().rstrip("."), b["direction"]) if s)
        if wav.exists() and not args.force:
            print(f"{beat}: exists, skipping", file=sys.stderr)
        else:
            payload = {"prompt": b["text"], "voice": args.voice}
            if direction:
                payload["style_instructions"] = direction
            try:
                res = fal_run.run(args.model, payload, args.out / ".fal" / beat, label=beat,
                                  spend_log=args.spend_log, cap_usd=args.cap_usd)
                produced = [f for f in res["files"] if f.lower().endswith(".wav")]
                if not produced:
                    raise fal_run.FalRunError(f"no wav in result files: {res['files']}")
                tmp = wav.with_suffix(".wav.part")
                shutil.copyfile(produced[0], tmp)
                tmp.replace(wav)
            except Exception as exc:
                print(f"{beat}: FAILED: {exc}", file=sys.stderr)
                failures.append(beat)
                continue
        timing[beat] = {"file": str(wav), "duration_s": probe_duration(wav), "text": b["text"], "direction": direction}
        print(f"{beat}: {timing[beat]['duration_s']}s", file=sys.stderr)
        timing_path.write_text(json.dumps(timing, indent=2))  # save after each beat so progress survives a failure

    print(json.dumps({b: timing[b] for b in wanted if b in timing}, indent=2))
    if failures:
        print(f"error: failed beats: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
