#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fal-client"]
# ///
"""Word-timed captions from the final mix.

    uv run scripts/captions.py MEDIA --backend fal|local [--script script.md]
        [--style lower|word] [--max-chars 42] [--out captions/] [--spend-log spend.jsonl]

Writes words.json ([{word,start,end}]), <stem>.srt, <stem>.vtt, <stem>.ass into --out.
Import `transcribe(media, backend, script=None)` to get the word list from Python.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fal_run  # noqa: E402
from tts import parse_script  # noqa: E402

SCRIBE = "fal-ai/elevenlabs/speech-to-text/scribe-v2"
PUNCT_END = ".?!…"
PUNCT_SOFT = ",;:—–"


class CaptionError(RuntimeError):
    pass


# ---------------------------------------------------------------- media helpers
def probe_size(media: Path) -> tuple[int, int]:
    """Video width/height, or 1920x1080 for audio-only input."""
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height", "-of", "json", str(media)],
                             check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise CaptionError(f"ffprobe failed on {media}: {exc}") from exc
    streams = json.loads(out).get("streams", [])
    return (streams[0]["width"], streams[0]["height"]) if streams else (1920, 1080)


def extract_audio(media: Path, dest: Path) -> None:
    proc = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000",
                           "-c:a", "pcm_s16le", str(dest)], capture_output=True, text=True)
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size < 1000:
        raise CaptionError(f"could not extract audio from {media} (no audio stream?): {proc.stderr.strip()[:300]}")


def script_terms(script: Path | None) -> list[str]:
    """Names and technical terms from the narration: mid-sentence capitalized words, CamelCase, acronyms, digits."""
    if not script:
        return []
    terms: dict[str, None] = {}
    for beat in parse_script(script.read_text()).values():
        text = re.sub(r"<[^>]*>", " ", beat["text"])
        for sentence in re.split(r"(?<=[.?!])\s+|\n+", text):
            tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9.\-']*", sentence)
            for i, tok in enumerate(tokens):
                tok = tok.strip(".-'")
                if len(tok) < 2 or len(tok) > 50:
                    continue
                if (i > 0 and tok[0].isupper()) or re.search(r"[A-Z].*[A-Z]|\d", tok):
                    terms[tok] = None
    return list(terms)[:100]


# ---------------------------------------------------------------- backends
def _fal_words(audio: Path, terms: list[str], spend_log: Path) -> list[dict]:
    payload: dict = {"audio_url": f"@{audio}", "tag_audio_events": False, "diarize": False}
    if terms:
        payload["keyterms"] = terms
    with tempfile.TemporaryDirectory() as tmp:
        res = fal_run.run(SCRIBE, payload, Path(tmp), label="captions", spend_log=spend_log)
    return [{"word": w["text"].strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)}
            for w in res["result"].get("words", []) if w.get("type") == "word" and w.get("text", "").strip()]


def _local_words(audio: Path, terms: list[str], model: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["whisper", str(audio), "--model", model, "--word_timestamps", "True", "--output_format", "json",
               "--output_dir", tmp, "--fp16", "False", "--verbose", "False"]
        if terms:
            cmd += ["--initial_prompt", "Terms: " + ", ".join(terms)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise CaptionError("whisper CLI not found; install it or use --backend fal") from exc
        if proc.returncode != 0:
            raise CaptionError(f"whisper failed: {proc.stderr.strip()[-500:]}")
        data = json.loads((Path(tmp) / f"{audio.stem}.json").read_text())
    return [{"word": w["word"].strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)}
            for seg in data.get("segments", []) for w in seg.get("words", []) if w["word"].strip()]


def transcribe(media, backend: str, script=None, spend_log: Path = Path("spend.jsonl"),
               whisper_model: str = "base") -> list[dict]:
    """Return [{word,start,end}] for the media's audio track. Raises CaptionError on failure or empty result."""
    media = Path(media)
    if not media.is_file():
        raise CaptionError(f"media not found: {media}")
    terms = script_terms(Path(script) if script else None)
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "audio.wav"
        extract_audio(media, audio)
        if backend == "fal":
            words = _fal_words(audio, terms, Path(spend_log))
        elif backend == "local":
            words = _local_words(audio, terms, whisper_model)
        else:
            raise CaptionError(f"unknown backend: {backend}")
    if not words:
        raise CaptionError("transcription returned no words")
    return words


# ---------------------------------------------------------------- cue grouping
def _split_two(words: list[str], max_chars: int) -> list[str] | None:
    """Wrap into at most 2 lines of <= max_chars, balanced, preferring a break after punctuation."""
    whole = " ".join(words)
    if len(whole) <= max_chars:
        return [whole]
    best, best_score = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > max_chars or len(b) > max_chars:
            continue
        score = max(len(a), len(b)) - (6 if words[i - 1][-1] in PUNCT_END + PUNCT_SOFT else 0)
        if best_score is None or score < best_score:
            best, best_score = [a, b], score
    return best


def group_cues(words: list[dict], max_chars: int, min_dur: float = 1.0, max_dur: float = 6.0) -> list[dict]:
    cues, cur = [], []

    def flush() -> None:
        if cur:
            cues.append({"words": list(cur), "start": cur[0]["start"], "end": cur[-1]["end"]})
            cur.clear()

    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            texts = [x["word"] for x in cur] + [w["word"]]
            too_long = _split_two(texts, max_chars) is None or w["end"] - cur[0]["start"] > max_dur
            if too_long or gap > 0.8:
                carry: list[dict] = []
                if too_long and len(cur) >= 4:
                    # move the tail into the next cue: after the last punctuation, else 2 words so no orphan cue
                    cut = next((i + 1 for i in range(len(cur) - 2, len(cur) // 3, -1)
                                if cur[i]["word"][-1] in PUNCT_END + PUNCT_SOFT), None)
                    if cut is None and w["word"][-1] in PUNCT_END + PUNCT_SOFT:
                        cut = len(cur) - 2
                    if cut:
                        carry = cur[cut:]
                        del cur[cut:]
                flush()
                cur.extend(carry)
        cur.append(w)
        text_len = len(" ".join(x["word"] for x in cur))
        dur = w["end"] - cur[0]["start"]
        last = w["word"][-1]
        if (last in PUNCT_END and dur >= min_dur) or (last in PUNCT_SOFT and text_len >= 0.7 * max_chars):
            flush()
    flush()
    # a cue that ended up under min_dur and touches the next cue merges into it when it fits
    merged: list[dict] = []
    for cue in cues:
        prev = merged[-1] if merged else None
        if prev and (prev["end"] - prev["start"] < min_dur) and cue["start"] - prev["end"] < 0.3:
            joined = prev["words"] + cue["words"]
            if _split_two([x["word"] for x in joined], max_chars) and joined[-1]["end"] - joined[0]["start"] <= max_dur:
                prev.update(words=joined, end=cue["end"])
                continue
        merged.append(cue)
    for i, cue in enumerate(merged):  # stretch short cues into the gap after them
        limit = merged[i + 1]["start"] if i + 1 < len(merged) else cue["start"] + min_dur
        cue["end"] = max(cue["end"], min(cue["start"] + min_dur, limit))
        cue["lines"] = _split_two([x["word"] for x in cue["words"]], max_chars)
    return merged


# ---------------------------------------------------------------- writers
def _ts(t: float, sep: str) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def write_srt(cues: list[dict], path: Path) -> None:
    path.write_text("\n".join(f"{i}\n{_ts(c['start'], ',')} --> {_ts(c['end'], ',')}\n" + "\n".join(c["lines"]) + "\n"
                              for i, c in enumerate(cues, 1)))


def write_vtt(cues: list[dict], path: Path) -> None:
    path.write_text("WEBVTT\n\n" + "\n".join(f"{_ts(c['start'], '.')} --> {_ts(c['end'], '.')}\n" + "\n".join(c["lines"]) + "\n"
                                             for c in cues))


def _ass_ts(t: float) -> str:
    cs = round(t * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("{", "(").replace("}", ")")


def write_ass(cues: list[dict], path: Path, width: int, height: int, style: str) -> None:
    portrait = height > width
    font = round(min(width, height) * (0.06 if portrait else 0.05 * 1.0) * (1.0 if portrait else height / min(width, height)))
    margin_v = round(height * (0.16 if portrait else 0.07))
    margin_h = round(width * 0.08)
    header = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {width}\nPlayResY: {height}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
        "MarginV, Encoding\n"
        f"Style: Default,Helvetica,{font},&H0000E5FF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,"
        f"{max(2, round(font * 0.07))},1,2,{margin_h},{margin_h},{margin_v},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    lines = []
    for c in cues:
        if style == "word":
            parts, pos, cursor = [], 0, c["start"]
            line_lens = [len(x) for x in c["lines"]]
            for j, w in enumerate(c["words"]):
                nxt = c["words"][j + 1]["start"] if j + 1 < len(c["words"]) else c["end"]
                cs = max(1, round((nxt - cursor) * 100))
                cursor = nxt
                text = _ass_escape(w["word"])
                sep = ""
                if j + 1 < len(c["words"]):
                    consumed = pos + len(w["word"])
                    if len(line_lens) > 1 and consumed >= line_lens[0] and pos < line_lens[0]:
                        sep = "\\N"
                    else:
                        sep = " "
                    pos = consumed + 1
                parts.append(f"{{\\k{cs}}}{text}{sep}")
            body = "".join(parts)
        else:
            body = "\\N".join(_ass_escape(x) for x in c["lines"])
        lines.append(f"Dialogue: 0,{_ass_ts(c['start'])},{_ass_ts(c['end'])},Default,,0,0,0,,{body}")
    path.write_text(header + "\n".join(lines) + "\n")


# ---------------------------------------------------------------- CLI
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("media", type=Path)
    p.add_argument("--backend", choices=["fal", "local"], required=True)
    p.add_argument("--script", type=Path, help="script.md; narration terms bias the ASR")
    p.add_argument("--style", choices=["lower", "word"], default="lower")
    p.add_argument("--max-chars", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("captions"))
    p.add_argument("--spend-log", type=Path, default=Path("spend.jsonl"))
    p.add_argument("--whisper-model", default="base", help="local backend model (default base)")
    args = p.parse_args()
    try:
        words = transcribe(args.media, args.backend, args.script, args.spend_log, args.whisper_model)
        width, height = probe_size(args.media)
    except (CaptionError, fal_run.FalRunError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    cues = group_cues(words, args.max_chars)
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.media.stem
    (args.out / "words.json").write_text(json.dumps(words, indent=2))
    write_srt(cues, args.out / f"{stem}.srt")
    write_vtt(cues, args.out / f"{stem}.vtt")
    write_ass(cues, args.out / f"{stem}.ass", width, height, args.style)
    print(json.dumps({"words": len(words), "cues": len(cues), "out": str(args.out),
                      "files": ["words.json", f"{stem}.srt", f"{stem}.vtt", f"{stem}.ass"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
