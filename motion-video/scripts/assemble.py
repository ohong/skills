#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["opentimelineio"]
# ///
"""Build an OpenTimelineIO timeline from shots.json and render it with one ffmpeg command.

  assemble.py build shots.json --voice vo/ [--music music/bed.wav] [--sfx sfx/cues.json] \\
      --out timeline.otio [--animatic]
  assemble.py render timeline.otio [--width W --height H --fps F] --out out.mp4 \\
      [--animatic] [--lufs -14]

shots.json: {fps,width,height,shots:[{id,beat,start,duration,source,path?,in?,keyframe?,
prompt?,fit?,transition?:{type,duration}}]}. A shot's `transition` is the transition INTO
that shot from the previous one, centered on the cut (the cut stays at `start`, so the
audio placement never drifts). Transition durations need no media handles: the first or
last frame is held if the source is too short.

Timeline layout: track "video", "voice", "music", "sfx" (extra "sfx.2"... lanes only when
cues overlap). Shot metadata lives in clip.metadata["motion_video"].
"""
import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
import urllib.parse

STILL_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
FITS = {"cover", "contain", "blurfill"}
EPS = 1e-3
# shots.json transition names -> ffmpeg xfade names. Unknown names pass through to xfade.
XFADE_ALIAS = {"dissolve": "fade", "crossfade": "fade", "cross-dissolve": "fade", "fade": "fade"}
FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


def otio_mod():
    try:
        import opentimelineio as otio
        return otio
    except ImportError:
        die("opentimelineio is not installed. Run with `uv run scripts/assemble.py ...` "
            "(inline metadata installs it) or `uv run --with opentimelineio python3 scripts/assemble.py ...`.")


def need(tool):
    if not shutil.which(tool):
        die(f"{tool} not found on PATH")


def probe_duration(path):
    """Media duration in seconds, or None if ffprobe cannot tell."""
    if not shutil.which("ffprobe"):
        return None
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return None


def load_json(path, what):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        die(f"{what} not found: {path}")
    except json.JSONDecodeError as e:
        die(f"{what} is not valid JSON ({path}): {e}")


# --------------------------------------------------------------------------- build

def build(a):
    otio = otio_mod()
    spec = load_json(a.shots, "shots.json")
    base = os.path.dirname(os.path.abspath(a.shots))
    fps = float(spec.get("fps") or 30)
    shots = spec.get("shots")
    if not shots:
        die("shots.json has no shots")

    def rt(sec):
        return otio.opentime.RationalTime(sec * fps, fps)

    def tr(start, dur):
        return otio.opentime.TimeRange(rt(start), rt(dur))

    def resolve(p):
        if not p:
            return None
        p = os.path.expanduser(p)
        return os.path.abspath(p if os.path.isabs(p) else os.path.join(base, p))

    # ---- normalize and validate shots
    ids, problems, items = set(), [], []
    cursor = 0.0
    for i, s in enumerate(sorted(shots, key=lambda x: x.get("start", 1e12))):
        sid = s.get("id") or f"shot{i + 1}"
        if sid in ids:
            problems.append(f"duplicate shot id {sid}")
        ids.add(sid)
        dur = s.get("duration")
        if not isinstance(dur, (int, float)) or dur <= 0:
            problems.append(f"{sid}: duration must be a positive number")
            continue
        start = float(s["start"]) if "start" in s else cursor
        if start < cursor - EPS:
            problems.append(f"{sid}: starts at {start} before previous shot ends ({cursor}); "
                            "shots may not overlap (use `transition` for overlaps)")
        start = max(start, cursor)
        fit = s.get("fit") or "cover"
        if fit not in FITS:
            problems.append(f"{sid}: fit must be one of {sorted(FITS)}, got {fit!r}")
        path = resolve(s.get("path"))
        key = resolve(s.get("keyframe"))
        has_path = bool(path and os.path.isfile(path))
        has_key = bool(key and os.path.isfile(key))
        if has_path:
            media, slate = path, False
        elif a.animatic and has_key:
            media, slate = key, False
        elif a.animatic:
            media, slate = None, True
        else:
            problems.append(f"{sid}: media file missing ({s.get('path') or 'no path'}); "
                            "build without --animatic needs every shot's file")
            media, slate = None, False
        items.append(dict(id=sid, s=s, start=start, dur=float(dur), fit=fit, media=media, slate=slate))
        cursor = start + float(dur)
    if problems:
        die("shots.json problems:\n  " + "\n  ".join(problems))
    total = cursor

    # ---- video track
    timeline = otio.schema.Timeline(name=os.path.splitext(os.path.basename(a.out))[0])
    timeline.metadata["motion_video"] = {
        "fps": fps, "width": spec.get("width"), "height": spec.get("height"),
        "animatic": bool(a.animatic), "total_duration": total, "shots_json": os.path.abspath(a.shots)}
    vtrack = otio.schema.Track(name="video", kind=otio.schema.TrackKind.Video)
    cur, prev_kind = 0.0, None
    for n_it, it in enumerate(items):
        s = it["s"]
        if it["start"] - cur > EPS:
            gap = otio.schema.Gap(source_range=tr(0, it["start"] - cur))
            vtrack.append(gap)
            prev_kind = "gap"
        trans = s.get("transition")
        if trans:
            d = float(trans.get("duration") or 0)
            if d > 0 and prev_kind == "clip":
                prev = items[n_it - 1]
                if d > min(prev["dur"], it["dur"]) + EPS:
                    die(f"{it['id']}: transition {d}s is longer than a neighbouring shot")
                ttype = (trans.get("type") or "dissolve").lower()
                if ttype in XFADE_ALIAS:
                    t = otio.schema.Transition(name=f"{ttype}->{it['id']}",
                                               transition_type=otio.schema.Transition.Type.SMPTE_Dissolve,
                                               in_offset=rt(d / 2), out_offset=rt(d / 2))
                else:
                    t = otio.schema.Transition(name=f"{ttype}->{it['id']}", transition_type=ttype,
                                               in_offset=rt(d / 2), out_offset=rt(d / 2))
                t.metadata["motion_video"] = {"type": ttype, "duration": d, "into": it["id"]}
                vtrack.append(t)
            elif d > 0:
                warn(f"{it['id']}: transition ignored (no adjacent previous clip)")
        ext = it["media"]
        if ext:
            ref = otio.schema.ExternalReference(target_url=ext)
            ad = None if os.path.splitext(ext)[1].lower() in STILL_EXT else probe_duration(ext)
            if ad:
                ref.available_range = tr(0, ad)
        else:
            ref = otio.schema.MissingReference()
        clip = otio.schema.Clip(name=it["id"], media_reference=ref,
                                source_range=tr(float(s.get("in") or 0), it["dur"]))
        clip.metadata["motion_video"] = {
            "id": it["id"], "beat": s.get("beat"), "fit": it["fit"], "prompt": s.get("prompt"),
            "source": s.get("source"), "start": it["start"], "slate": it["slate"],
            "still": bool(ext and os.path.splitext(ext)[1].lower() in STILL_EXT)}
        vtrack.append(clip)
        cur, prev_kind = it["start"] + it["dur"], "clip"
    timeline.tracks.append(vtrack)

    # ---- voice track
    def add_audio_track(name, placements):
        """placements: list of (at, path, src_start, dur, meta). Assumes sorted, non-overlapping."""
        track = otio.schema.Track(name=name, kind=otio.schema.TrackKind.Audio)
        pos = 0.0
        for at, path, src, dur, meta in placements:
            if at - pos > EPS:
                track.append(otio.schema.Gap(source_range=tr(0, at - pos)))
            ref = otio.schema.ExternalReference(target_url=path)
            ad = probe_duration(path)
            if ad:
                ref.available_range = tr(0, ad)
            c = otio.schema.Clip(name=os.path.basename(path), media_reference=ref, source_range=tr(src, dur))
            c.metadata["motion_video"] = dict(meta, at=at)
            track.append(c)
            pos = at + dur
        timeline.tracks.append(track)

    if a.voice:
        vo_dir = os.path.abspath(a.voice)
        timing = load_json(os.path.join(vo_dir, "timing.json"), "voice timing manifest (vo/timing.json)")
        first_start = {}
        for it in items:
            b = it["s"].get("beat")
            if b and b not in first_start:
                first_start[b] = it["start"]
        placements = []
        for beat, info in timing.items():
            if beat not in first_start:
                warn(f"voice beat {beat} in timing.json has no shot with that beat; skipped")
                continue
            f = info.get("file") if isinstance(info, dict) else None
            if not f:
                die(f"timing.json beat {beat} has no `file`")
            cands = [f] if os.path.isabs(f) else [os.path.join(vo_dir, f), os.path.join(base, f), os.path.join(vo_dir, os.path.basename(f))]
            path = next((c for c in cands if os.path.isfile(c)), None)
            if not path:
                die(f"voice file for beat {beat} not found (tried {', '.join(cands)})")
            dur = probe_duration(path) or info.get("duration_s")
            if not dur:
                die(f"cannot determine duration of voice file {path}")
            placements.append([first_start[beat], os.path.abspath(path), 0.0, float(dur), {"beat": beat}])
        for beat in first_start:
            if beat not in timing:
                warn(f"shots.json beat {beat} has no entry in timing.json (no narration for it)")
        placements.sort(key=lambda p: p[0])
        end = 0.0
        for p in placements:
            if p[0] < end - EPS:
                warn(f"voice beat {p[4]['beat']} would overlap the previous narration; moved from "
                     f"{p[0]:.2f}s to {end:.2f}s. Re-time shots.json from the real audio.")
                p[0] = end
            end = p[0] + p[3]
            if end > total + EPS:
                warn(f"voice beat {p[4]['beat']} ends at {end:.2f}s, after the last shot ({total:.2f}s); it will be cut")
        if placements:
            add_audio_track("voice", placements)

    # ---- music track
    if a.music:
        mp = os.path.abspath(a.music)
        if not os.path.isfile(mp):
            die(f"music file not found: {a.music}")
        add_audio_track("music", [(0.0, mp, 0.0, total, {"role": "music", "loops_to_fit": True})])

    # ---- sfx tracks (one lane, more only for overlapping cues)
    if a.sfx:
        cues = load_json(a.sfx, "sfx cues")
        sfx_base = os.path.dirname(os.path.abspath(a.sfx))
        lanes = []  # each lane: [end_time, placements]
        for c in sorted(cues, key=lambda c: c["at"]):
            f = c["file"]
            cands = [f] if os.path.isabs(f) else [os.path.join(sfx_base, f), os.path.join(base, f), os.path.abspath(f)]
            path = next((x for x in cands if os.path.isfile(x)), None)
            if not path:
                die(f"sfx file not found: {f}")
            dur = probe_duration(path)
            if not dur:
                die(f"cannot determine duration of sfx file {path}")
            at = float(c["at"])
            if at + dur > total + EPS:
                warn(f"sfx {f} at {at}s runs past the end ({total:.2f}s); it will be cut")
            lane = next((l for l in lanes if l[0] <= at + EPS), None)
            if lane is None:
                lane = [0.0, []]
                lanes.append(lane)
            lane[1].append((at, os.path.abspath(path), 0.0, dur, {"role": "sfx", "gain_db": float(c.get("gain_db") or 0)}))
            lane[0] = at + dur
        for n, lane in enumerate(lanes, 1):
            add_audio_track("sfx" if n == 1 else f"sfx.{n}", lane[1])

    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    tmp = a.out + ".part"
    try:
        otio.adapters.write_to_file(timeline, tmp, adapter_name="otio_json")
        os.replace(tmp, a.out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    n_slate = sum(1 for it in items if it["slate"])
    print(f"wrote {os.path.abspath(a.out)}: {len(items)} shots ({n_slate} slates), {total:.2f}s, "
          f"{len(timeline.tracks) - 1} audio track(s)")


# --------------------------------------------------------------------------- render

def media_path(clip):
    ref = clip.media_reference
    url = getattr(ref, "target_url", None)
    if not url:
        return None
    if url.startswith("file://"):
        url = urllib.parse.unquote(urllib.parse.urlparse(url).path)
    return url


def esc_filter_path(p):
    return p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def render(a):
    otio = otio_mod()
    need("ffmpeg")
    need("ffprobe")
    tl = otio.adapters.read_from_file(a.timeline)
    meta = tl.metadata.get("motion_video", {}) if hasattr(tl.metadata, "get") else {}
    fps = a.fps or meta.get("fps")
    W = a.width or meta.get("width")
    H = a.height or meta.get("height")
    if not (fps and W and H):
        die("--width/--height/--fps are required (the timeline has no defaults stored)")
    W, H, fps = int(W), int(H), float(fps)
    if a.animatic:
        H = int(round(1280 * H / W / 2)) * 2
        W = 1280
    if W % 2 or H % 2:
        die(f"output size {W}x{H} must be even for yuv420p")

    def frames(sec):
        return int(round(sec * fps))

    def secs(f):
        return f"{f / fps:.6f}"

    vtracks = [t for t in tl.tracks if t.kind == otio.schema.TrackKind.Video]
    if not vtracks:
        die("timeline has no video track")
    vt = vtracks[0]

    # ---- flatten the video track into segments with frame boundaries
    kids = list(vt)
    segs = []  # dict(kind, clip?, b0, b1, trans_in_f, trans_out_f)
    t_cursor = 0.0
    for idx, ch in enumerate(kids):
        if isinstance(ch, otio.schema.Transition):
            continue
        d = ch.source_range.duration.to_seconds()
        b0, b1 = frames(t_cursor), frames(t_cursor + d)
        t_cursor += d
        seg = dict(kind="gap" if isinstance(ch, otio.schema.Gap) else "clip", clip=ch, b0=b0, b1=b1, tin=0, tout=0)
        segs.append(seg)
    # attach transitions
    seg_i = -1
    trans_before = {}  # segment index -> transition frames
    for ch in kids:
        if isinstance(ch, otio.schema.Transition):
            dF = frames(ch.in_offset.to_seconds() + ch.out_offset.to_seconds())
            ttype = (ch.metadata.get("motion_video", {}) or {}).get("type") or "dissolve"
            trans_before[seg_i + 1] = (dF, ttype)
        else:
            seg_i += 1
    for k, (dF, ttype) in trans_before.items():
        if k == 0 or k >= len(segs) or segs[k]["kind"] != "clip" or segs[k - 1]["kind"] != "clip" or dF <= 0:
            warn("a transition next to a gap or at the edge was ignored")
            continue
        segs[k]["tin"] = dF - dF // 2   # frames of head handle on incoming clip
        segs[k - 1]["tout"] = dF // 2   # frames of tail handle on outgoing clip
        segs[k]["tname"] = ttype
        segs[k]["tframes"] = dF
    if not segs:
        die("video track is empty")
    total_f = segs[-1]["b1"]

    inputs, fc = [], []  # ffmpeg input arg lists, filter_complex lines
    slate_dir = None
    slate_files = []

    def add_input(args):
        inputs.append(args)
        return len(inputs) - 1

    has_drawtext = True
    slate_notes = []
    font = next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)
    if any(s["kind"] == "clip" and s["clip"].metadata.get("motion_video", {}).get("slate") for s in segs):
        f = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        if " drawtext " not in f:
            has_drawtext = False
            warn("this ffmpeg build has no drawtext filter (needs libfreetype: brew install homebrew-ffmpeg/ffmpeg/ffmpeg "
                 "--with-freetype). Slates render as plain cards; ids and prompts are listed below and in render.md.")

    def fit_chain(fit, i):
        if fit == "contain":
            return f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"
        if fit == "blurfill":
            return (f"split=2[bg{i}i][fg{i}i];"
                    f"[bg{i}i]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                    f"boxblur=luma_radius={max(W // 24, 10)}:luma_power=2[bg{i}];"
                    f"[fg{i}i]scale={W}:{H}:force_original_aspect_ratio=decrease[fg{i}];"
                    f"[bg{i}][fg{i}]overlay=(W-w)/2:(H-h)/2")
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"

    labels = []
    for i, sg in enumerate(segs):
        L = sg["b1"] - sg["b0"] + sg["tin"] + sg["tout"]  # frames on screen for this segment
        Ls = L / fps
        if sg["kind"] == "gap":
            fc.append(f"color=c=black:s={W}x{H}:r={fps:g}:d={Ls + 1 / fps:.6f},format=yuv420p,setsar=1,"
                      f"trim=end_frame={L},setpts=PTS-STARTPTS[v{i}]")
            labels.append(f"v{i}")
            continue
        clip = sg["clip"]
        mv = clip.metadata.get("motion_video", {}) or {}
        fit = mv.get("fit") or "cover"
        if mv.get("slate"):
            sid = mv.get("id") or clip.name
            prompt = mv.get("prompt") or "(no prompt)"
            if slate_dir is None:
                slate_dir = os.path.join(os.path.dirname(os.path.abspath(a.out)), f".slates-{os.path.splitext(os.path.basename(a.out))[0]}")
                os.makedirs(slate_dir, exist_ok=True)
            fs_id, fs_p = max(H // 10, 16), max(H // 30, 12)
            cols = max(int(W * 0.84 / (fs_p * 0.55)), 12)
            lines = textwrap.wrap(prompt, cols)
            if len(lines) > 9:
                lines = lines[:9]
                lines[-1] = lines[-1][:max(cols - 3, 1)] + "..."
            id_file = os.path.join(slate_dir, f"{sid}.id.txt")
            pr_file = os.path.join(slate_dir, f"{sid}.prompt.txt")
            with open(id_file, "w") as f:
                f.write(sid)
            with open(pr_file, "w") as f:
                f.write("\n".join(lines))
            slate_files += [id_file, pr_file]
            ff = f":fontfile='{esc_filter_path(font)}'" if font else ""
            if not has_drawtext:
                slate_notes.append(f"{sid}: {prompt}")
                print(f"slate {sid}: {prompt}", file=sys.stderr)
                fc.append(f"color=c=0x1c1c22:s={W}x{H}:r={fps:g}:d={Ls + 1 / fps:.6f},"
                          f"format=yuv420p,setsar=1,trim=end_frame={L},setpts=PTS-STARTPTS,fps={fps:g}[v{i}]")
                labels.append(f"v{i}")
                continue
            fc.append(
                f"color=c=0x1c1c22:s={W}x{H}:r={fps:g}:d={Ls + 1 / fps:.6f},"
                f"drawtext=textfile='{esc_filter_path(id_file)}':expansion=none{ff}:fontsize={fs_id}:fontcolor=white:"
                f"x={W // 20}:y={H // 12},"
                f"drawtext=textfile='{esc_filter_path(pr_file)}':expansion=none{ff}:fontsize={fs_p}:fontcolor=0xd0d0d8:"
                f"x={W // 20}:y={H // 12 + fs_id + fs_p}:line_spacing={fs_p // 3},"
                f"format=yuv420p,setsar=1,trim=end_frame={L},setpts=PTS-STARTPTS,fps={fps:g}[v{i}]")
            labels.append(f"v{i}")
            continue
        path = media_path(clip)
        if not path or not os.path.isfile(path):
            die(f"media file missing for clip {clip.name}: {path}")
        in_s = clip.source_range.start_time.to_seconds()
        if mv.get("still") or os.path.splitext(path)[1].lower() in STILL_EXT:
            k = add_input(["-loop", "1", "-framerate", f"{fps:g}", "-t", f"{Ls + 1:.6f}", "-i", path])
            pre = ""
        else:
            head_s = sg["tin"] / fps
            start = max(0.0, in_s - head_s)
            short = max(0.0, head_s - in_s)  # source starts later than the handle needs: hold first frame
            k = add_input(["-ss", f"{start:.6f}", "-t", f"{max(Ls - short, 1 / fps) + 0.5:.6f}", "-i", path])
            pre = ""
            if short > 0:
                pre += f"tpad=start_mode=clone:start_duration={short:.6f},"
            pre += f"tpad=stop_mode=clone:stop_duration={Ls:.6f},"
        chain = fit_chain(fit, i)
        fc.append(f"[{k}:v]setpts=PTS-STARTPTS,fps={fps:g},{pre}{chain},setsar=1,format=yuv420p,"
                  f"trim=end_frame={L},setpts=PTS-STARTPTS,fps={fps:g}[v{i}]")
        labels.append(f"v{i}")

    # ---- join: xfade for transitions (offset accounts for overlap), concat for cuts
    cur, cur_len = labels[0], segs[0]["b1"] - segs[0]["b0"] + segs[0]["tin"] + segs[0]["tout"]
    for i in range(1, len(segs)):
        sg = segs[i]
        L = sg["b1"] - sg["b0"] + sg["tin"] + sg["tout"]
        out = f"j{i}"
        if sg.get("tframes"):
            dF = sg["tframes"]
            name = XFADE_ALIAS.get(sg["tname"], sg["tname"])
            fc.append(f"[{cur}][{labels[i]}]xfade=transition={name}:duration={secs(dF)}:offset={secs(cur_len - dF)}[{out}]")
            cur_len += L - dF
        else:
            fc.append(f"[{cur}][{labels[i]}]concat=n=2:v=1:a=0[{out}]")
            cur_len += L
        cur = out
    if cur_len != total_f:
        warn(f"internal: joined video is {cur_len} frames, expected {total_f}")
    fc.append(f"[{cur}]fps={fps:g},format=yuv420p[vout]")
    total_s = total_f / fps

    # ---- audio
    voice, music, sfx = [], [], []
    for t in tl.tracks:
        if t.kind != otio.schema.TrackKind.Audio:
            continue
        pos = 0.0
        for ch in t:
            if isinstance(ch, otio.schema.Transition):
                continue
            d = ch.source_range.duration.to_seconds()
            if isinstance(ch, otio.schema.Clip):
                p = media_path(ch)
                if not p or not os.path.isfile(p):
                    die(f"audio file missing for {ch.name}: {p}")
                mv = ch.metadata.get("motion_video", {}) or {}
                rec = dict(path=p, at=pos, src=ch.source_range.start_time.to_seconds(), dur=d, gain=float(mv.get("gain_db") or 0))
                (voice if t.name.startswith("voice") else music if t.name.startswith("music") else sfx).append(rec)
            pos += d

    def afmt():
        return "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"

    def audio_clip(rec, loop=False):
        if loop:
            k = add_input(["-stream_loop", "-1", "-i", rec["path"]])
        else:
            k = add_input(["-i", rec["path"]])
        return k

    amix_in, n = [], 0
    if voice or music or sfx:
        vlabels = []
        for rec in voice:
            k = audio_clip(rec)
            ms = int(round(rec["at"] * 1000))
            fc.append(f"[{k}:a]atrim=start={rec['src']:.6f}:duration={rec['dur']:.6f},asetpts=PTS-STARTPTS,{afmt()},"
                      f"adelay=delays={ms}:all=1[va{n}]")
            vlabels.append(f"va{n}")
            n += 1
        voice_bus = None
        if vlabels:
            if len(vlabels) == 1:
                fc.append(f"[{vlabels[0]}]anull[vbus]")
            else:
                fc.append("".join(f"[{l}]" for l in vlabels) + f"amix=inputs={len(vlabels)}:normalize=0:duration=longest[vbus]")
            fc.append("[vbus]asplit=2[vmix][vsc]")
            voice_bus = "vmix"
            amix_in.append("vmix")
        for rec in music[:1]:
            k = audio_clip(rec, loop=True)
            fade_st = max(total_s - 1.0, 0.0)
            fc.append(f"[{k}:a]atrim=start={rec['src']:.6f}:duration={total_s:.6f},asetpts=PTS-STARTPTS,{afmt()},"
                      f"volume={a.music_db}dB,afade=t=out:st={fade_st:.6f}:d={min(1.0, total_s):.6f}[mus]")
            if voice_bus:
                fc.append("[mus][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[musd]")
                amix_in.append("musd")
            else:
                amix_in.append("mus")
        if len(music) > 1:
            warn("more than one music clip on the timeline; only the first is used")
        for rec in sfx:
            k = audio_clip(rec)
            ms = int(round(rec["at"] * 1000))
            fc.append(f"[{k}:a]atrim=start={rec['src']:.6f}:duration={rec['dur']:.6f},asetpts=PTS-STARTPTS,{afmt()},"
                      f"volume={rec['gain']}dB,adelay=delays={ms}:all=1[sx{n}]")
            amix_in.append(f"sx{n}")
            n += 1
        mix_in = "".join(f"[{l}]" for l in amix_in)
        fc.append(f"{mix_in}amix=inputs={len(amix_in)}:normalize=0:duration=longest,"
                  f"atrim=end={total_s:.6f},asetpts=PTS-STARTPTS,"
                  f"loudnorm=I={a.lufs}:TP=-1:LRA=11,aresample=48000,aformat=channel_layouts=stereo[aout]")

    # ---- assemble command (video inputs come first in `inputs`, in order of creation)
    out_abs = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    tmp_out = os.path.join(os.path.dirname(out_abs), f".{os.path.basename(out_abs)}.part.mp4")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    for args in inputs:
        cmd += args
    cmd += ["-filter_complex", ";\n".join(fc), "-map", "[vout]"]
    if amix_in:
        cmd += ["-map", "[aout]"]
    else:
        cmd += ["-an"]
    crf, preset = ("28", "ultrafast") if a.animatic else ("18", "medium")
    cmd += ["-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p", "-r", f"{fps:g}"]
    if amix_in:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-t", f"{total_s:.6f}", "-movflags", "+faststart", "-f", "mp4"]
    run_cmd = cmd + [tmp_out]
    log_cmd = cmd + [out_abs]

    md = os.path.join(os.path.dirname(out_abs), "render.md")
    with open(md, "a") as f:
        f.write(f"\n## {dt.datetime.now().astimezone().isoformat(timespec='seconds')}  "
                f"{os.path.basename(out_abs)}{' (animatic)' if a.animatic else ''}\n\n"
                f"Timeline: `{os.path.abspath(a.timeline)}`, {W}x{H} @ {fps:g} fps, {total_s:.3f}s"
                f"{f', slate text files in {slate_dir}' if slate_dir else ''}\n"
                + ("".join(f"Text-less slate (no drawtext in ffmpeg) - {n}\n" for n in slate_notes)) +
                f"The script writes to a temp file and renames it to the output on success.\n\n"
                f"```sh\n{shlex.join(log_cmd)}\n```\n")

    print(f"rendering {W}x{H} @ {fps:g}fps, {total_s:.2f}s ...", file=sys.stderr)
    r = subprocess.run(run_cmd)
    if r.returncode != 0 or not os.path.isfile(tmp_out) or os.path.getsize(tmp_out) == 0:
        if os.path.exists(tmp_out):
            os.remove(tmp_out)
        die(f"ffmpeg failed (exit {r.returncode}); command is recorded in {md}")
    os.replace(tmp_out, out_abs)
    dur = probe_duration(out_abs)
    print(f"{out_abs}  duration {dur:.3f}s" if dur else out_abs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="shots.json + audio -> timeline.otio")
    b.add_argument("shots")
    b.add_argument("--voice", help="dir with timing.json and per-beat wavs")
    b.add_argument("--music")
    b.add_argument("--sfx", help="cues.json: [{file,at,gain_db?}]")
    b.add_argument("--out", required=True)
    b.add_argument("--animatic", action="store_true",
                   help="allow shots without media: use keyframe if present, else mark as slate")
    b.set_defaults(fn=build)
    r = sub.add_parser("render", help="timeline.otio -> mp4 via one ffmpeg command")
    r.add_argument("timeline")
    r.add_argument("--width", type=int)
    r.add_argument("--height", type=int)
    r.add_argument("--fps", type=float)
    r.add_argument("--out", required=True)
    r.add_argument("--animatic", action="store_true", help="1280-wide, crf 28, ultrafast")
    r.add_argument("--lufs", type=float, default=-14.0)
    r.add_argument("--music-db", type=float, default=-6.0, help="static music gain before ducking (default -6)")
    r.set_defaults(fn=render)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
