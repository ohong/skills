#!/usr/bin/env python3
"""Create a probe inventory and timestamped contact sheet for a video.

This helper samples still frames. It does not watch motion at playback speed or
listen to the soundtrack, so its output is evidence for inspection rather than
a complete creative review.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


COMMAND_TIMEOUT_SECONDS = 300


class ToolError(RuntimeError):
    """A clear, user-facing failure from an external media tool."""


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise ToolError(f"Required executable not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ToolError(
            f"Command exceeded the {COMMAND_TIMEOUT_SECONDS}s limit: {command[0]}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "no diagnostic output").strip()
        raise ToolError(f"{command[0]} failed: {detail}") from exc


def probe_video(source: Path, ffprobe: str) -> dict[str, Any]:
    result = run_command(
        [
            ffprobe,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-show_chapters",
            "-show_programs",
            "-of",
            "json",
            str(source),
        ]
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ToolError(f"ffprobe returned invalid JSON: {exc}") from exc


def probe_last_video_frame(
    source: Path,
    ffprobe: str,
    video_stream: dict[str, Any],
    duration: float,
) -> dict[str, Any]:
    try:
        time_base = Fraction(str(video_stream.get("time_base")))
        if time_base <= 0:
            raise ValueError
    except (ValueError, ZeroDivisionError):
        time_base = None
    try:
        stream_start_pts = int(video_stream.get("start_pts", 0))
    except (TypeError, ValueError):
        stream_start_pts = 0
    if time_base is not None:
        stream_start = float(stream_start_pts * time_base)
    else:
        try:
            stream_start = float(video_stream.get("start_time", 0.0))
        except (TypeError, ValueError):
            stream_start = 0.0
        if not math.isfinite(stream_start):
            stream_start = 0.0

    # A tail interval reaches the true end while avoiding a full-file frame listing.
    interval_start = max(stream_start, stream_start + duration - 10.0)

    def read_frames(read_from: float | None) -> list[dict[str, Any]]:
        command = [ffprobe, "-v", "error", "-select_streams", "v:0"]
        if read_from is not None:
            command.extend(["-read_intervals", f"{read_from:.6f}%"])
        command.extend(
            [
                "-show_frames",
                "-show_entries",
                "frame=best_effort_timestamp,best_effort_timestamp_time,pts,pts_time",
                "-of",
                "json",
                str(source),
            ]
        )
        result = run_command(command)
        try:
            return json.loads(result.stdout).get("frames", [])
        except json.JSONDecodeError as exc:
            raise ToolError(f"ffprobe returned invalid frame-timestamp JSON: {exc}") from exc

    frames = read_frames(interval_start)
    method = "ffprobe tail show_frames"
    if not frames and interval_start > stream_start:
        # A bad declared duration can place the tail interval past real media.
        frames = read_frames(None)
        method = "ffprobe full show_frames after empty declared-duration tail"

    timestamp_ticks = []
    timestamps = []
    for frame in frames:
        tick_value = frame.get("best_effort_timestamp") or frame.get("pts")
        try:
            timestamp_ticks.append(int(tick_value))
        except (TypeError, ValueError):
            pass
        value = frame.get("best_effort_timestamp_time") or frame.get("pts_time")
        try:
            timestamp = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(timestamp):
            timestamps.append(timestamp)
    if timestamp_ticks and time_base is not None:
        last_tick = max(timestamp_ticks)
        last_pts = float(last_tick * time_base)
        relative_ticks = last_tick - stream_start_pts
        last_frame_time = max(0.0, float(relative_ticks * time_base))
        endpoint_seek = max(
            0.0, float((relative_ticks - Fraction(1, 2)) * time_base)
        )
    elif timestamps:
        last_pts = max(timestamps)
        last_frame_time = max(0.0, last_pts - stream_start)
        preroll = float(time_base) / 2 if time_base is not None else 0.000000001
        endpoint_seek = max(0.0, last_frame_time - preroll)
    else:
        raise ToolError("Could not determine the final decodable video-frame timestamp")
    return {
        "method": method,
        "stream_start_time_seconds": stream_start,
        "stream_time_base_seconds": float(time_base) if time_base is not None else None,
        "last_decodable_frame_pts_seconds": last_pts,
        "last_decodable_frame_time_seconds": last_frame_time,
        "endpoint_seek_time_seconds": endpoint_seek,
        "endpoint_seek_preroll_seconds": last_frame_time - endpoint_seek,
    }


def first_stream(probe: dict[str, Any], stream_type: str) -> dict[str, Any] | None:
    return next(
        (stream for stream in probe.get("streams", []) if stream.get("codec_type") == stream_type),
        None,
    )


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def rational_float(value: Any) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        number = float(Fraction(str(value)))
    except (ValueError, ZeroDivisionError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def parse_timestamp(value: str) -> float:
    """Parse seconds or HH:MM:SS(.sss) into seconds."""
    raw = value.strip()
    try:
        if ":" not in raw:
            seconds = float(raw)
        else:
            parts = raw.split(":")
            if len(parts) not in (2, 3):
                raise ValueError
            seconds = 0.0
            for part in parts:
                seconds = seconds * 60 + float(part)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid timestamp {value!r}; use seconds or HH:MM:SS.sss"
        ) from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise argparse.ArgumentTypeError("timestamps must be finite and non-negative")
    return seconds


def parse_range(value: str) -> tuple[float, float]:
    try:
        start_raw, end_raw = value.split("-", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "range must be START-END, using seconds or HH:MM:SS.sss"
        ) from exc
    start = parse_timestamp(start_raw)
    end = parse_timestamp(end_raw)
    if end <= start:
        raise argparse.ArgumentTypeError("range END must be greater than START")
    return start, end


def parse_explicit_times(values: list[str]) -> list[float]:
    times: list[float] = []
    for value in values:
        for part in value.split(","):
            if part.strip():
                times.append(parse_timestamp(part))
    return times


def format_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def format_optional_duration(value: float | None) -> str:
    return f"{value:.6f}s" if value is not None else "unknown"


def sample_plan(
    duration: float,
    last_frame_time: float,
    endpoint_seek_time: float,
    overview_samples: int,
    sample_fps: float | None,
    sample_range: tuple[float, float] | None,
    explicit_times: list[float],
    max_frames: int,
) -> list[dict[str, Any]]:
    candidates: list[tuple[float, float, str, float, str]] = []

    def add_request(requested: float, reason: str) -> None:
        if requested > last_frame_time:
            seek = endpoint_seek_time
            target = last_frame_time
            selection = "last_decodable_frame"
        else:
            seek = target = requested
            selection = "requested_time"
        candidates.append((seek, target, reason, requested, selection))

    if overview_samples == 1:
        add_request(0.0, "overview")
    elif overview_samples > 1:
        for index in range(overview_samples):
            add_request(duration * index / (overview_samples - 1), "overview")

    if sample_fps is not None:
        start, end = sample_range or (0.0, duration)
        if start >= duration:
            raise ToolError(f"Dense range starts at {start:.3f}s, after the {duration:.3f}s video")
        end = min(end, duration)
        step = 1.0 / sample_fps
        count = int(math.floor((end - start) / step + 1e-9)) + 1
        for index in range(count):
            timestamp = start + index * step
            if timestamp <= last_frame_time + 1e-9:
                add_request(timestamp, "dense")

    for timestamp in explicit_times:
        if timestamp > duration + 1e-6:
            raise ToolError(
                f"Explicit timestamp {timestamp:.3f}s is after the {duration:.3f}s video"
            )
        add_request(timestamp, "explicit")

    # Millisecond-level de-duplication keeps coincident overview/dense samples honest.
    grouped: dict[int, dict[str, Any]] = {}
    for seek, target, reason, requested, selection in candidates:
        key = round(target * 1000)
        entry = grouped.setdefault(
            key,
            {
                "timestamp_seconds": target,
                "seek_timestamp_seconds": seek,
                "reasons": [],
                "requests": [],
            },
        )
        if reason not in entry["reasons"]:
            entry["reasons"].append(reason)
        entry["requests"].append(
            {
                "reason": reason,
                "requested_timestamp_seconds": requested,
                "selection": selection,
            }
        )
    plan = sorted(grouped.values(), key=lambda entry: entry["timestamp_seconds"])
    if not plan:
        raise ToolError("No frames requested; increase --overview-samples or add --times")
    if len(plan) > max_frames:
        raise ToolError(
            f"Sampling requested {len(plan)} frames, over --max-frames {max_frames}; "
            "use a narrower --range, lower --sample-fps, or raise the cap explicitly"
        )
    return plan


def ensure_output_available(paths: list[Path], overwrite: bool) -> None:
    collisions = [path for path in paths if path.exists()]
    if collisions and not overwrite:
        rendered = "\n  ".join(str(path) for path in collisions[:8])
        suffix = "\n  ..." if len(collisions) > 8 else ""
        raise ToolError(
            "Refusing to overwrite existing output(s); choose another --output-dir or pass "
            f"--overwrite:\n  {rendered}{suffix}"
        )


def paths_alias(left: Path, right: Path) -> bool:
    try:
        if left.resolve() == right.resolve():
            return True
        return left.exists() and right.exists() and left.samefile(right)
    except (OSError, RuntimeError):
        return True


def reject_output_aliases(source: Path, outputs: list[Path]) -> None:
    for index, output in enumerate(outputs):
        if paths_alias(source, output):
            raise ToolError(f"Output aliases the input video and is unsafe: {output}")
        for earlier in outputs[:index]:
            if paths_alias(earlier, output):
                raise ToolError(f"Outputs alias each other: {earlier} and {output}")


def pillow_modules() -> tuple[Any, Any, Any]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise ToolError(
            "Pillow is required to build the contact sheet. Run this helper with a Python "
            "environment that provides Pillow (module PIL)."
        ) from exc
    return Image, ImageDraw, ImageFont


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def extract_frame(
    source: Path,
    destination: Path,
    timestamp: float,
    width: int | None,
    ffmpeg: str,
    overwrite: bool,
) -> None:
    run_command(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y" if overwrite else "-n",
            "-ss",
            f"{timestamp:.12f}",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            *(["-vf", f"scale={width}:-2"] if width is not None else []),
            str(destination),
        ]
    )
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ToolError(
            f"ffmpeg produced no frame near {timestamp:.6f}s for {destination}; "
            "try an earlier timestamp"
        )


def make_contact_sheet(
    frame_entries: list[dict[str, Any]],
    destination: Path,
    columns: int,
    thumbnail_width: int = 480,
) -> tuple[int, int]:
    Image, ImageDraw, ImageFont = pillow_modules()

    frames = []
    for entry in frame_entries:
        with Image.open(entry["absolute_path"]) as opened:
            entry["width"], entry["height"] = opened.size
            frame = opened.convert("RGB")
        # Keep only small copies in memory; the PNGs remain at their saved resolution.
        target_width = min(frame.width, thumbnail_width)
        target_height = max(1, round(frame.height * target_width / frame.width))
        frame.thumbnail((target_width, target_height), getattr(Image, "Resampling", Image).LANCZOS)
        entry["thumbnail_width"], entry["thumbnail_height"] = frame.size
        frames.append(frame)

    gap = 10
    label_height = 34
    tile_width = max(frame.width for frame in frames)
    tile_height = max(frame.height for frame in frames)
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new(
        "RGB",
        (
            columns * tile_width + (columns + 1) * gap,
            rows * (tile_height + label_height) + (rows + 1) * gap,
        ),
        color=(18, 18, 20),
    )
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=18)
    except TypeError:  # Pillow before 10.1 does not accept size.
        font = ImageFont.load_default()

    for index, (entry, frame) in enumerate(zip(frame_entries, frames, strict=True)):
        column = index % columns
        row = index // columns
        x = gap + column * tile_width
        y = gap + row * (tile_height + label_height)
        sheet.paste(frame, (x + (tile_width - frame.width) // 2, y))
        reasons = "+".join(entry["reasons"])
        label = f"#{index + 1:03d}  {entry['timestamp']}  {reasons}"
        adjusted = [
            request
            for request in entry["requests"]
            if request["selection"] == "last_decodable_frame"
        ]
        if adjusted:
            label += f" req={adjusted[-1]['requested_timestamp_seconds']:.3f}s"
        draw.text((x + 4, y + tile_height + 7), label, fill=(245, 245, 247), font=font)

    sheet.save(destination, format="JPEG", quality=90, optimize=True)
    return sheet.size


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Probe a video and create timestamped sampled frames plus a contact sheet. "
            "Sampling stills does not replace full-speed viewing or listening."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("video", type=Path, help="input video")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="output directory (default: ./<video-stem>-inspection)",
    )
    parser.add_argument(
        "--overview-samples",
        type=int,
        default=12,
        help="evenly spaced start-to-end frames; use 0 to disable",
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        help="additional still samples per second, over --range or the full video",
    )
    parser.add_argument(
        "--range",
        dest="sample_range",
        type=parse_range,
        metavar="START-END",
        help="dense sampling range; requires --sample-fps",
    )
    parser.add_argument(
        "--times",
        action="append",
        default=[],
        metavar="T[,T...]",
        help="additional exact timestamps; repeatable",
    )
    parser.add_argument("--max-frames", type=int, default=240, help="sampling safety cap")
    parser.add_argument(
        "--thumbnail-width", type=int, default=480,
        help="maximum contact-sheet thumbnail width in pixels; does not resize saved PNGs",
    )
    parser.add_argument(
        "--frame-width", type=int,
        help="explicit saved PNG width in pixels, preserving aspect ratio; omit for native decoded resolution",
    )
    parser.add_argument("--columns", type=int, default=3, help="contact-sheet columns")
    parser.add_argument(
        "--extract-audio",
        nargs="?",
        const="",
        metavar="WAV",
        help="extract PCM WAV; omit WAV to write <output-dir>/audio.wav",
    )
    parser.add_argument("--overwrite", action="store_true", help="replace named outputs")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable")
    parser.add_argument("--ffprobe", default="ffprobe", help="ffprobe executable")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source = args.video.expanduser().resolve()
    if not source.is_file():
        parser.error(f"input video does not exist or is not a file: {source}")
    if args.overview_samples < 0:
        parser.error("--overview-samples must be at least 0")
    if args.sample_fps is not None and (
        not math.isfinite(args.sample_fps) or args.sample_fps <= 0
    ):
        parser.error("--sample-fps must be finite and greater than 0")
    if args.sample_range is not None and args.sample_fps is None:
        parser.error("--range requires --sample-fps")
    if args.max_frames < 1:
        parser.error("--max-frames must be at least 1")
    if args.thumbnail_width < 64:
        parser.error("--thumbnail-width must be at least 64")
    if args.frame_width is not None and args.frame_width < 1:
        parser.error("--frame-width must be a positive integer")
    if args.columns < 1:
        parser.error("--columns must be at least 1")

    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else (Path.cwd() / f"{source.stem}-inspection").resolve()
    )

    try:
        pillow_modules()  # Fail before writing partial outputs when Pillow is unavailable.
        probe = probe_video(source, args.ffprobe)
        video_stream = first_stream(probe, "video")
        audio_stream = first_stream(probe, "audio")
        if video_stream is None:
            raise ToolError("Input contains no video stream")
        video_duration = positive_float(video_stream.get("duration"))
        container_duration = positive_float(probe.get("format", {}).get("duration"))
        audio_duration = positive_float(audio_stream.get("duration")) if audio_stream else None
        duration = video_duration or container_duration
        if duration is None:
            raise ToolError("Could not determine a positive video duration")
        endpoint = probe_last_video_frame(source, args.ffprobe, video_stream, duration)
        last_frame_time = endpoint["last_decodable_frame_time_seconds"]
        endpoint_seek_time = endpoint["endpoint_seek_time_seconds"]
        source_fps = rational_float(video_stream.get("avg_frame_rate")) or rational_float(
            video_stream.get("r_frame_rate")
        )
        explicit_times = parse_explicit_times(args.times)
        plan = sample_plan(
            duration,
            last_frame_time,
            endpoint_seek_time,
            args.overview_samples,
            args.sample_fps,
            args.sample_range,
            explicit_times,
            args.max_frames,
        )

        frames_dir = output_dir / "frames"
        inventory_path = output_dir / "inventory.json"
        coverage_path = output_dir / "coverage.json"
        sheet_path = output_dir / "contact-sheet.jpg"
        for index, entry in enumerate(plan, start=1):
            entry["path"] = f"frames/frame-{index:03d}.png"
            entry["absolute_path"] = str(output_dir / entry["path"])
            entry["timestamp"] = format_timestamp(entry["timestamp_seconds"])
        audio_path = None
        if args.extract_audio is not None:
            if audio_stream is None:
                raise ToolError("--extract-audio was requested, but the input has no audio stream")
            audio_path = (
                (output_dir / "audio.wav")
                if args.extract_audio == ""
                else Path(args.extract_audio).expanduser().resolve()
            )

        named_outputs = [
            inventory_path,
            coverage_path,
            sheet_path,
            *(Path(entry["absolute_path"]) for entry in plan),
        ]
        if audio_path is not None:
            named_outputs.append(audio_path)
        reject_output_aliases(source, named_outputs)
        ensure_output_available(named_outputs, args.overwrite)
        output_dir.mkdir(parents=True, exist_ok=True)
        frames_dir.mkdir(parents=True, exist_ok=True)
        if audio_path is not None:
            audio_path.parent.mkdir(parents=True, exist_ok=True)

        for entry in plan:
            extract_frame(
                source,
                Path(entry["absolute_path"]),
                entry["seek_timestamp_seconds"],
                args.frame_width,
                args.ffmpeg,
                args.overwrite,
            )
        sheet_width, sheet_height = make_contact_sheet(
            plan, sheet_path, args.columns, args.thumbnail_width
        )

        if audio_path is not None:
            run_command(
                [
                    args.ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y" if args.overwrite else "-n",
                    "-i",
                    str(source),
                    "-map",
                    "0:a:0",
                    "-vn",
                    "-c:a",
                    "pcm_s16le",
                    str(audio_path),
                ]
            )

        write_json(inventory_path, probe)
        public_frames = [
            {key: value for key, value in entry.items() if key != "absolute_path"}
            for entry in plan
        ]
        coverage = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(source),
            "limitations": [
                "Frames are discrete timestamp samples, not full-speed motion playback.",
                "The contact sheet does not represent audio; listen to the source or extracted WAV.",
                "Frames record requested positions separately from seek timestamps; non-endpoint seeks may quantize to nearby source frames.",
                "The endpoint seek timestamp comes from ffprobe's last reported decodable frame PTS.",
                "Contact-sheet thumbnails are reduced previews; inspect saved PNG dimensions before judging fine detail.",
            ],
            "media_summary": {
                "duration_seconds": duration,
                "video_duration_seconds": video_duration,
                "container_duration_seconds": container_duration,
                "audio_duration_seconds": audio_duration,
                "width": video_stream.get("width"),
                "height": video_stream.get("height"),
                "average_fps": source_fps,
                "video_codec": video_stream.get("codec_name"),
                "audio_present": audio_stream is not None,
                "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            },
            "sampling": {
                "overview_samples_requested": args.overview_samples,
                "dense_sample_fps": args.sample_fps,
                "dense_range_seconds": list(args.sample_range) if args.sample_range else None,
                "explicit_times_seconds": explicit_times,
                "unique_frames_extracted": len(plan),
                "saved_frame_resolution": "native_decoded" if args.frame_width is None else "explicit_width",
                "saved_frame_width_requested": args.frame_width,
                "contact_sheet_thumbnail_max_width": args.thumbnail_width,
                "endpoint": {
                    **endpoint,
                    "video_duration_seconds": duration,
                    "gap_from_video_duration_seconds": max(0.0, duration - last_frame_time),
                },
            },
            "outputs": {
                "inventory": str(inventory_path),
                "contact_sheet": str(sheet_path),
                "contact_sheet_dimensions": {"width": sheet_width, "height": sheet_height},
                "audio": str(audio_path) if audio_path else None,
            },
            "frames": public_frames,
        }
        write_json(coverage_path, coverage)
    except (ToolError, argparse.ArgumentTypeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Inspected: {source}")
    print(f"Duration: {duration:.3f}s | samples: {len(plan)} | audio: {'yes' if audio_stream else 'no'}")
    print(
        "Durations: "
        f"video {format_optional_duration(video_duration)} | "
        f"container {format_optional_duration(container_duration)} | "
        f"audio {format_optional_duration(audio_duration)}"
    )
    print(f"Contact sheet: {sheet_path}")
    print(f"Coverage metadata: {coverage_path}")
    print("Reminder: sampled stills do not replace watching motion at speed or listening to audio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
