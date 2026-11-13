#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fal-client", "pillow"]
# ///
"""Automated critic pass for a rendered film. It gathers evidence; it does not judge the pictures.

    uv run scripts/critic.py RENDER --script script.md --shots shots.json --out review/critic-01
        [--backend fal|local] [--brief-duration 60 --width 1920 --height 1080 --fps 30]
        [--spend-log spend.jsonl] [--whisper-model base]

Steps: frames (shot midpoints, cuts +/-2 frames, first/last, contact sheet), transcript diff
against the VO text in script.md (WER per beat), loudness and silence, black/frozen frames,
and verify_video.py. Writes report.md and report.json into --out.
Exit 0: no blocking finding. Exit 1: blocking finding(s). Exit 2: the critic itself failed.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import captions  # noqa: E402
import fal_run  # noqa: E402
from tts import parse_script  # noqa: E402

WER_BLOCK = 0.10
TP_BLOCK_DBTP = -1.0
LUFS_RANGE = (-18.0, -12.0)


class CriticError(RuntimeError):
    pass


def tc(t: float) -> str:
    m, s = divmod(max(t, 0.0), 60)
    return f"{int(m)}:{s:05.2f}"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise CriticError(f"executable not found: {cmd[0]}") from exc
    if check and proc.returncode != 0:
        raise CriticError(f"{cmd[0]} failed ({proc.returncode}): {proc.stderr.strip()[-400:]}")
    return proc


def probe(render: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(render)]).stdout
    data = json.loads(out)
    streams = data.get("streams", [])
    video = next((s for s in streams if s["codec_type"] == "video"), None)
    if not video:
        raise CriticError("render has no video stream")
    duration = float(data["format"].get("duration") or video.get("duration") or 0)
    if duration <= 0:
        raise CriticError("could not determine render duration")
    return {"duration": duration, "has_audio": any(s["codec_type"] == "audio" for s in streams)}


# ---------------------------------------------------------------- shots and frames
def load_shots(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
        shots = data["shots"]
        for s in shots:
            s["id"], float(s["start"]), float(s["duration"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CriticError(f"cannot read shots.json ({path}): {exc}") from exc
    if not shots:
        raise CriticError("shots.json has no shots")
    data["shots"] = sorted(shots, key=lambda s: float(s["start"]))
    return data


def shot_at(shots: list[dict], t: float) -> str | None:
    for s in shots:
        if float(s["start"]) <= t < float(s["start"]) + float(s["duration"]):
            return s["id"]
    return shots[-1]["id"] if shots and t >= float(shots[-1]["start"]) else None


def extract_frame(render: Path, t: float, dest: Path) -> None:
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(render), "-frames:v", "1", str(dest)])
    if not dest.exists() or dest.stat().st_size == 0:
        raise CriticError(f"no frame extracted at {tc(t)} -> {dest.name}")


def extract_frames(render: Path, shots: list[dict], fps: float, duration: float, out: Path) -> list[dict]:
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    plan: list[dict] = [{"name": "first.png", "t": 0.0, "kind": "first", "shot": shots[0]["id"]},
                        {"name": "last.png", "t": max(duration - 1.5 / fps, 0.0), "kind": "last", "shot": shots[-1]["id"]}]
    for i, s in enumerate(shots):
        start, dur = float(s["start"]), float(s["duration"])
        plan.append({"name": f"{s['id']}-mid.png", "t": start + dur / 2, "kind": "mid", "shot": s["id"]})
        if i > 0:
            prev = shots[i - 1]["id"]
            for tag, dt in (("before", -2), ("after", 2)):
                plan.append({"name": f"cut-{prev}-{s['id']}-{tag}.png", "t": start + dt / fps,
                             "kind": f"cut-{tag}", "shot": s["id"]})
    for item in plan:
        item["t"] = round(min(max(item["t"], 0.0), duration - 1.5 / fps), 3)
        item["path"] = str(frames_dir / item["name"])
        extract_frame(render, item["t"], frames_dir / item["name"])
    return plan


def contact_sheet(render: Path, out: Path) -> str:
    inspect_dir = out / "inspect"
    run([sys.executable, str(HERE / "inspect_video.py"), str(render), "--output-dir", str(inspect_dir),
         "--sample-fps", "1", "--max-frames", "1000", "--overwrite"])
    sheet = inspect_dir / "contact-sheet.jpg"
    if not sheet.exists():
        raise CriticError("inspect_video.py did not write contact-sheet.jpg")
    return str(sheet)


# ---------------------------------------------------------------- transcript diff
def norm_tokens(text: str) -> list[str]:
    text = re.sub(r"<[^>]*>", " ", text.lower()).replace("\u2019", "'")
    text = re.sub(r"[-\u2013\u2014/_]", " ", text)
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def beat_windows(shots: list[dict], beats: dict) -> dict[str, tuple[float, float]]:
    win: dict[str, tuple[float, float]] = {}
    for s in shots:
        if s.get("beat"):
            a, b = float(s["start"]), float(s["start"]) + float(s["duration"])
            lo, hi = win.get(s["beat"], (a, b))
            win[s["beat"]] = (min(lo, a), max(hi, b))
    for beat, info in beats.items():
        if beat not in win and info.get("start") is not None:
            win[beat] = (info["start"], info["end"])
    return win


def diff_transcript(beats: dict, words: list[dict], windows: dict) -> dict:
    """Global alignment of the script's VO words against the transcript; per-beat error counts.

    Dropped and substituted words belong to the beat they were scripted in. Inserted words go to the beat
    whose time window contains them, else the beat of the preceding scripted word."""
    ref = [(beat, tok) for beat, info in beats.items() if info["text"] for tok in norm_tokens(info["text"])]
    hyp = [(tok, w["start"], w["end"]) for w in words for tok in norm_tokens(w["word"])]
    stats = {b: {"ref_words": 0, "substituted": 0, "dropped": 0, "inserted": 0} for b in {r[0] for r in ref}}
    for beat, _ in ref:
        stats[beat]["ref_words"] += 1
    edits: list[dict] = []

    def beat_for_time(t: float, fallback: str) -> str:
        for beat, (a, b) in windows.items():
            if beat in stats and a <= t < b:
                return beat
        return fallback

    sm = difflib.SequenceMatcher(None, [r[1] for r in ref], [h[0] for h in hyp], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        pairs = min(i2 - i1, j2 - j1) if op == "replace" else 0
        for k in range(pairs):
            beat, rw = ref[i1 + k]
            hw = hyp[j1 + k]
            stats[beat]["substituted"] += 1
            edits.append({"type": "substituted", "beat": beat, "expected": rw, "heard": hw[0], "time": hw[1]})
        for k in range(i1 + pairs, i2):
            beat, rw = ref[k]
            near = hyp[j1 - 1][2] if j1 > 0 else 0.0
            stats[beat]["dropped"] += 1
            edits.append({"type": "dropped", "beat": beat, "expected": rw, "heard": None, "time": near})
        for k in range(j1 + pairs, j2):
            prev_beat = ref[i1 - 1][0] if i1 > 0 else ref[0][0]
            beat = beat_for_time((hyp[k][1] + hyp[k][2]) / 2, prev_beat)
            stats[beat]["inserted"] += 1
            edits.append({"type": "inserted", "beat": beat, "expected": None, "heard": hyp[k][0], "time": hyp[k][1]})
    for st in stats.values():
        st["wer"] = round((st["substituted"] + st["dropped"] + st["inserted"]) / max(st["ref_words"], 1), 4)
    edits.sort(key=lambda e: e["time"])
    return {"beats": stats, "edits": edits}


# ---------------------------------------------------------------- audio and video detectors
def audio_analysis(render: Path, duration: float) -> dict:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(render), "-vn", "-af",
                "ebur128=peak=true,silencedetect=n=-50dB:d=1.5", "-f", "null", "-"])
    err = proc.stderr
    summary = err.split("Summary:")[-1] if "Summary:" in err else ""
    lufs = re.search(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", summary)
    peak = re.search(r"True peak:\s*\n\s*Peak:\s+(-?[\d.]+|-inf)\s+dBFS", summary)
    if not lufs or not peak:
        raise CriticError("could not parse the ebur128 summary from ffmpeg output")

    def num(m: re.Match) -> float:
        return float("-inf") if m.group(1) == "-inf" else float(m.group(1))

    silences, start = [], None
    for line in err.splitlines():
        if (m := re.search(r"silence_start:\s*(-?[\d.]+)", line)):
            start = max(float(m.group(1)), 0.0)
        elif (m := re.search(r"silence_end:\s*([\d.]+)", line)) and start is not None:
            silences.append({"start": start, "end": float(m.group(1))})
            start = None
    if start is not None:
        silences.append({"start": start, "end": duration})
    return {"integrated_lufs": num(lufs), "true_peak_dbtp": num(peak), "silences": silences}


def video_analysis(render: Path, duration: float) -> dict:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(render), "-an", "-vf",
                "blackdetect=d=0.25:pic_th=0.98,freezedetect=n=-60dB:d=1", "-f", "null", "-"])
    err = proc.stderr
    black = [{"start": float(a), "end": float(b)} for a, b in
             re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", err)]
    freezes, start = [], None
    for line in err.splitlines():
        if (m := re.search(r"freeze_start:\s*([\d.]+)", line)):
            start = float(m.group(1))
        elif (m := re.search(r"freeze_end:\s*([\d.]+)", line)) and start is not None:
            freezes.append({"start": start, "end": float(m.group(1))})
            start = None
    if start is not None:
        freezes.append({"start": start, "end": duration})
    return {"black": black, "frozen": freezes}


def verify(render: Path, out: Path, args: argparse.Namespace, shots_data: dict, expect_audio: bool) -> dict:
    last = shots_data["shots"][-1]
    dur = args.brief_duration or float(last["start"]) + float(last["duration"])
    width = args.width or shots_data.get("width")
    height = args.height or shots_data.get("height")
    fps = args.fps or shots_data.get("fps")
    cmd = [sys.executable, str(HERE / "verify_video.py"), str(render), "--decode",
           "--json", str(out / "verify.json"), "--overwrite"]
    for flag, val in (("--duration", dur), ("--width", width), ("--height", height), ("--fps", fps)):
        if val:
            cmd += [flag, str(val)]
    if expect_audio:
        cmd.append("--expect-audio")
    proc = run(cmd, check=False)
    if proc.returncode == 2 or not (out / "verify.json").exists():
        raise CriticError(f"verify_video.py errored: {(proc.stderr or proc.stdout).strip()[-400:]}")
    report = json.loads((out / "verify.json").read_text())
    report["expected"] = {"duration": dur, "width": width, "height": height, "fps": fps}
    return report


# ---------------------------------------------------------------- report
def build(args: argparse.Namespace) -> tuple[dict, int]:
    render = args.render.expanduser().resolve()
    if not render.is_file():
        raise CriticError(f"render not found: {render}")
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    info = probe(render)
    duration = info["duration"]
    shots_data = load_shots(args.shots)
    shots = shots_data["shots"]
    fps = float(args.fps or shots_data.get("fps") or 30)
    beats = parse_script(args.script.read_text())
    vo_beats = {b: i for b, i in beats.items() if i["text"]}
    blocking: list[str] = []
    warnings: list[str] = []
    report: dict = {"render": str(render), "duration_s": duration}

    frames = extract_frames(render, shots, fps, duration, out)
    report["contact_sheet"] = contact_sheet(render, out)

    ver = verify(render, out, args, shots_data, expect_audio=bool(vo_beats))
    report["verify"] = {"status": ver["status"], "expected": ver["expected"], "summary": ver["summary"], "checks": ver["checks"]}
    hard = {"duration", "width", "height", "decode"}
    for chk in ver["checks"]:
        if chk["passed"] or chk["name"] == "audio_present":  # audio presence is judged below
            continue
        msg = f"verify_video {chk['name']}: expected {chk['expected']!r}, observed {chk['observed']!r} ({chk.get('detail', '')})"
        (blocking if chk["name"] in hard else warnings).append(msg)

    audio: dict = {"present": info["has_audio"]}
    if not info["has_audio"]:
        if vo_beats:
            blocking.append("render has no audio stream but script.md has narration")
        else:
            warnings.append("render has no audio stream (no narration expected; fine for a silent film)")
    else:
        a = audio_analysis(render, duration)
        audio.update(a)
        if a["integrated_lufs"] == float("-inf"):
            blocking.append("audio is silent (integrated loudness is -inf LUFS)")
        else:
            if a["true_peak_dbtp"] > TP_BLOCK_DBTP:
                blocking.append(f"true peak {a['true_peak_dbtp']:.1f} dBTP is above {TP_BLOCK_DBTP} dBTP (clipping risk)")
            if not LUFS_RANGE[0] <= a["integrated_lufs"] <= LUFS_RANGE[1]:
                warnings.append(f"integrated loudness {a['integrated_lufs']:.1f} LUFS is outside {LUFS_RANGE[0]}..{LUFS_RANGE[1]}")
        for s in a["silences"]:
            warnings.append(f"silence over 1.5 s at {tc(s['start'])}-{tc(s['end'])} (shot {shot_at(shots, s['start'])}); check it is planned")
    report["audio"] = audio

    vid = video_analysis(render, duration)
    for kind, label in (("black", "black frames"), ("frozen", "frozen picture")):
        for n, it in enumerate(vid[kind], 1):
            mid = (it["start"] + it["end"]) / 2
            warnings.append(f"{label} at {tc(it['start'])}-{tc(it['end'])} (shot {shot_at(shots, it['start'])}); check it is intentional")
            dest = out / "frames" / f"flag-{kind}-{n}.png"
            extract_frame(render, min(mid, duration - 1.5 / fps), dest)
            frames.append({"name": dest.name, "t": round(mid, 3), "kind": f"flag-{kind}", "shot": shot_at(shots, mid), "path": str(dest)})
    report["video"] = vid

    transcript = None
    if vo_beats and info["has_audio"]:
        backend = args.backend or ("fal" if os.environ.get("FAL_KEY") else "local")
        try:
            words = captions.transcribe(render, backend, args.script, args.spend_log, args.whisper_model)
        except (captions.CaptionError, fal_run.FalRunError) as exc:
            raise CriticError(f"transcription failed: {exc}") from exc
        (out / "transcript.json").write_text(json.dumps(words, indent=2))
        transcript = diff_transcript(vo_beats, words, beat_windows(shots, beats))
        transcript["backend"] = backend
        for beat, st in transcript["beats"].items():
            n_edits = st["substituted"] + st["dropped"] + st["inserted"]
            if st["wer"] > WER_BLOCK:
                blocking.append(f"{beat}: word error rate {st['wer']:.2f} exceeds {WER_BLOCK} "
                                f"({st['substituted']} substituted, {st['dropped']} dropped, {st['inserted']} inserted of {st['ref_words']} words)")
            elif n_edits:
                warnings.append(f"{beat}: {n_edits} word difference(s), WER {st['wer']:.2f}; see Transcript diff")
    elif not vo_beats:
        warnings.append("no VO text in script.md; transcript diff skipped")
    report["transcript"] = transcript
    report["blocking"], report["warnings"], report["frames"] = blocking, warnings, frames
    write_report(out, report, shots)
    return report, (1 if blocking else 0)


def write_report(out: Path, r: dict, shots: list[dict]) -> None:
    (out / "report.json").write_text(json.dumps(r, indent=2))
    v = r["verify"]["summary"]
    L: list[str] = [f"# Critic report: {Path(r['render']).name}", "",
                    f"Duration {r['duration_s']:.2f}s. verify_video: {r['verify']['status']}. "
                    f"Blocking findings: {len(r['blocking'])}. Warnings: {len(r['warnings'])}.", "",
                    "## Blocking", ""]
    L += [f"- {b}" for b in r["blocking"]] or ["None."]
    L += ["", "## Warnings", ""] + ([f"- {w}" for w in r["warnings"]] or ["None."])

    L += ["", "## Transcript diff", ""]
    t = r["transcript"]
    if t:
        L += [f"Backend: {t['backend']}. Words are lowercased with tags and punctuation removed, so digits and spelled-out numbers count as different words.", "",
              "| Beat | Words | Substituted | Dropped | Inserted | WER |", "|---|---|---|---|---|---|"]
        L += [f"| {b} | {s['ref_words']} | {s['substituted']} | {s['dropped']} | {s['inserted']} | {s['wer']:.2f} |"
              for b, s in t["beats"].items()]
        L.append("")
        for e in t["edits"]:
            what = {"substituted": f"said \"{e['heard']}\" for \"{e['expected']}\"",
                    "dropped": f"dropped \"{e['expected']}\"", "inserted": f"added \"{e['heard']}\""}[e["type"]]
            L.append(f"- {tc(e['time'])} {e['beat']}: {what}")
        if not t["edits"]:
            L.append("Transcript matches the script.")
    else:
        L.append("Not run.")

    a = r["audio"]
    L += ["", "## Audio", ""]
    if a.get("present"):
        L.append(f"Integrated loudness {a['integrated_lufs']:.1f} LUFS, true peak {a['true_peak_dbtp']:.1f} dBTP, "
                 f"{len(a['silences'])} silence(s) over 1.5 s at -50 dB.")
    else:
        L.append("No audio stream.")
    L += ["", "## Video", "",
          f"Black intervals: {len(r['video']['black'])}. Frozen intervals: {len(r['video']['frozen'])}. "
          f"Expected {r['verify']['expected']}; observed {v.get('width')}x{v.get('height')}, {v.get('average_fps')} fps, {v.get('duration_seconds')} s."]

    L += ["", "## Evidence index", "", f"- Contact sheet: `{r['contact_sheet']}`", "- Sampled frames (1 per second): `inspect/frames/`"]
    by_shot: dict = {}
    for f in r["frames"]:
        by_shot.setdefault("_global" if f["kind"] in ("first", "last") else f["shot"], []).append(f)
    for f in by_shot.get("_global", []):
        L.append(f"- {f['kind']} frame ({tc(f['t'])}): `{f['path']}`")
    for s in shots:
        beat = f" (beat {s['beat']})" if s.get("beat") else ""
        L.append(f"- **{s['id']}**{beat}, {tc(float(s['start']))}-{tc(float(s['start']) + float(s['duration']))}:")
        for f in by_shot.get(s["id"], []):
            L.append(f"  - {f['kind']} ({tc(f['t'])}): `{f['path']}`")

    L += ["", "## Reviewer checklist", "",
          "The critic did not look at the pictures. Open these files and judge them against the brief:", "",
          f"1. Open the contact sheet `{r['contact_sheet']}` and check pacing and story at a glance.",
          "2. Open every `*-mid.png`. Check that the shot shows what its beat says, the subject is on-model against its reference sheet, and there are no generation artifacts (hands, melting text, warped geometry).",
          "3. Open each `cut-*-before.png` and `cut-*-after.png` pair. Check that the cut lands cleanly, with no flash frame or wrong-shot frame.",
          "4. Check that all on-screen text is readable at delivery size and inside the safe area, and that captions collide with nothing.",
          "5. Open `first.png` and `last.png` and check the opening and the end card."]
    n = 6
    if t and t["edits"]:
        beats_hit = ", ".join(sorted({e["beat"] for e in t["edits"]}))
        L.append(f"{n}. Listen to the beats with transcript differences ({beats_hit}) at the timecodes above, and decide whether the voice or the ASR was wrong.")
        n += 1
    flags = [f["name"] for f in r["frames"] if f["kind"].startswith("flag-")]
    if flags:
        L.append(f"{n}. Open the flagged frames ({', '.join(flags)}) and confirm the black or frozen picture is intentional.")
        n += 1
    if a.get("silences"):
        L.append(f"{n}. Listen around the silences listed under Warnings and confirm they are planned pauses.")
    (out / "report.md").write_text("\n".join(L) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("render", type=Path)
    p.add_argument("--script", type=Path, required=True)
    p.add_argument("--shots", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--backend", choices=["fal", "local"], help="ASR backend (default fal if FAL_KEY is set, else local)")
    p.add_argument("--brief-duration", type=float, help="expected duration in s (default: end of last shot)")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--fps", type=float)
    p.add_argument("--spend-log", type=Path, default=Path("spend.jsonl"))
    p.add_argument("--whisper-model", default="base")
    args = p.parse_args()
    for f in (args.script, args.shots):
        if not f.is_file():
            print(f"error: file not found: {f}", file=sys.stderr)
            return 2
    try:
        report, code = build(args)
    except CriticError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"report: {args.out / 'report.md'}")
    print(f"blocking: {len(report['blocking'])}  warnings: {len(report['warnings'])}")
    for b in report["blocking"]:
        print(f"BLOCKING: {b}")
    return code


if __name__ == "__main__":
    sys.exit(main())
