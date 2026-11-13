#!/usr/bin/env python3
"""Verify explicit technical video invariants with ffprobe and ffmpeg.

Black, silence, and volume diagnostics are reported as review cues. They do not
claim that a video is creatively effective or that an intentional edit is bad.
"""

from __future__ import annotations

import argparse
import json
import math
import re
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
            "-of",
            "json",
            str(source),
        ]
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ToolError(f"ffprobe returned invalid JSON: {exc}") from exc


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


def parse_positive_ratio(value: str) -> float:
    try:
        if ":" in value:
            numerator, denominator = value.split(":", 1)
            ratio = float(numerator) / float(denominator)
        elif "/" in value:
            ratio = float(Fraction(value))
        else:
            ratio = float(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ratio {value!r}; use 16:9, 16/9, or a decimal"
        ) from exc
    if not math.isfinite(ratio) or ratio <= 0:
        raise argparse.ArgumentTypeError("ratio must be finite and greater than 0")
    return ratio


def parse_expected_fps(value: str) -> float:
    try:
        fps = float(Fraction(value)) if "/" in value else float(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError(
            f"invalid frame rate {value!r}; use 30, 29.97, or 30000/1001"
        ) from exc
    if not math.isfinite(fps) or fps <= 0:
        raise argparse.ArgumentTypeError("frame rate must be finite and greater than 0")
    return fps


def display_aspect(video: dict[str, Any]) -> tuple[float | None, str]:
    declared = video.get("display_aspect_ratio")
    if declared and declared != "0:1":
        try:
            return parse_positive_ratio(str(declared)), "stream display_aspect_ratio"
        except argparse.ArgumentTypeError:
            pass
    width = positive_float(video.get("width"))
    height = positive_float(video.get("height"))
    if width is None or height is None:
        return None, "unavailable"
    sample_aspect = 1.0
    declared_sample = video.get("sample_aspect_ratio")
    if declared_sample and declared_sample != "0:1":
        try:
            sample_aspect = parse_positive_ratio(str(declared_sample))
        except argparse.ArgumentTypeError:
            pass
    return width * sample_aspect / height, "dimensions and sample_aspect_ratio"


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    expected: Any,
    observed: Any,
    passed: bool,
    detail: str,
) -> None:
    checks.append(
        {
            "name": name,
            "expected": expected,
            "observed": observed,
            "passed": passed,
            "detail": detail,
        }
    )


def interval_total(intervals: list[dict[str, float]], duration: float) -> float:
    normalized = []
    for interval in intervals:
        start = max(0.0, interval.get("start", 0.0))
        end = min(duration, interval.get("end", duration))
        if end > start:
            normalized.append((start, end))
    if not normalized:
        return 0.0
    normalized.sort()
    merged = [list(normalized[0])]
    for start, end in normalized[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def black_diagnostics(
    source: Path,
    ffmpeg: str,
    duration: float,
    min_duration: float,
    picture_threshold: float,
) -> dict[str, Any]:
    result = run_command(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-loglevel",
            "info",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-vf",
            f"blackdetect=d={min_duration}:pic_th={picture_threshold}",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    intervals = []
    pattern = re.compile(
        r"black_start:(?P<start>-?[0-9.]+)\s+black_end:(?P<end>-?[0-9.]+)"
        r"\s+black_duration:(?P<duration>[0-9.]+)"
    )
    for match in pattern.finditer(result.stderr):
        intervals.append({key: float(value) for key, value in match.groupdict().items()})
    return {
        "status": "completed",
        "minimum_interval_seconds": min_duration,
        "black_picture_threshold": picture_threshold,
        "intervals": intervals,
        "total_seconds": interval_total(intervals, duration),
    }


def audio_diagnostics(
    source: Path,
    ffmpeg: str,
    duration: float,
    min_duration: float,
    noise_threshold: str,
) -> dict[str, Any]:
    result = run_command(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-loglevel",
            "info",
            "-i",
            str(source),
            "-map",
            "0:a:0",
            "-vn",
            "-af",
            f"silencedetect=noise={noise_threshold}:d={min_duration},volumedetect",
            "-f",
            "null",
            "-",
        ]
    )
    intervals: list[dict[str, float]] = []
    open_start: float | None = None
    for line in result.stderr.splitlines():
        start_match = re.search(r"silence_start:\s*(-?[0-9.]+)", line)
        if start_match:
            open_start = float(start_match.group(1))
        end_match = re.search(
            r"silence_end:\s*(-?[0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)",
            line,
        )
        if end_match:
            end = float(end_match.group(1))
            parsed_duration = float(end_match.group(2))
            start = open_start if open_start is not None else end - parsed_duration
            intervals.append({"start": start, "end": end, "duration": parsed_duration})
            open_start = None
    if open_start is not None:
        intervals.append(
            {"start": open_start, "end": duration, "duration": max(0.0, duration - open_start)}
        )

    def volume_value(label: str) -> float | str | None:
        match = re.search(rf"{label}:\s*(-?inf|-?[0-9.]+)\s*dB", result.stderr)
        if not match:
            return None
        return match.group(1) if match.group(1) == "-inf" else float(match.group(1))

    return {
        "status": "completed",
        "minimum_silence_seconds": min_duration,
        "silence_noise_threshold": noise_threshold,
        "silence_intervals": intervals,
        "silence_total_seconds": interval_total(intervals, duration),
        "mean_volume_db": volume_value("mean_volume"),
        "max_volume_db": volume_value("max_volume"),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def paths_alias(left: Path, right: Path) -> bool:
    try:
        if left.resolve() == right.resolve():
            return True
        return left.exists() and right.exists() and left.samefile(right)
    except (OSError, RuntimeError):
        return True


def format_optional_number(value: float | None) -> str:
    return f"{value:.6f}" if value is not None else "unknown"


def format_optional_duration(value: float | None) -> str:
    return f"{value:.6f}s" if value is not None else "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify requested technical video invariants. Diagnostics provide review cues, "
            "not a guarantee of creative quality."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("video", type=Path, help="input video")
    parser.add_argument("--duration", type=float, help="expected video duration in seconds")
    parser.add_argument(
        "--duration-tolerance-frames",
        type=float,
        default=1.0,
        help="allowed absolute duration error, measured at expected or observed FPS",
    )
    parser.add_argument("--width", type=int, help="expected coded width")
    parser.add_argument("--height", type=int, help="expected coded height")
    parser.add_argument("--fps", type=parse_expected_fps, help="expected average frame rate")
    parser.add_argument("--fps-tolerance", type=float, default=0.01, help="allowed FPS error")
    parser.add_argument("--aspect", type=parse_positive_ratio, help="expected display aspect ratio")
    parser.add_argument(
        "--aspect-tolerance",
        type=float,
        default=0.005,
        help="allowed absolute display-ratio error",
    )
    parser.add_argument("--video-codec", help="expected ffprobe video codec name")
    parser.add_argument("--audio-codec", help="expected ffprobe audio codec name")
    audio_group = parser.add_mutually_exclusive_group()
    audio_group.add_argument("--expect-audio", action="store_true", help="require an audio stream")
    audio_group.add_argument(
        "--expect-no-audio", action="store_true", help="require that no audio stream exists"
    )
    parser.add_argument(
        "--decode",
        action="store_true",
        help="decode the primary video and optional primary audio streams to a null sink",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="scan for black intervals, silence intervals, and mean/max volume",
    )
    parser.add_argument(
        "--black-min-duration", type=float, default=0.25, help="minimum reported black interval"
    )
    parser.add_argument(
        "--black-picture-threshold",
        type=float,
        default=0.98,
        help="fraction of pixels that must be black",
    )
    parser.add_argument(
        "--silence-min-duration",
        type=float,
        default=0.25,
        help="minimum reported silence interval",
    )
    parser.add_argument(
        "--silence-noise-threshold",
        default="-50dB",
        help="ffmpeg silencedetect noise threshold, such as -50dB or 0.001",
    )
    parser.add_argument("--json", type=Path, help="write a machine-readable report")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing --json file")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable")
    parser.add_argument("--ffprobe", default="ffprobe", help="ffprobe executable")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source = args.video.expanduser().resolve()
    if not source.is_file():
        parser.error(f"input video does not exist or is not a file: {source}")
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("--duration must be finite and greater than 0")
    if args.audio_codec and args.expect_no_audio:
        parser.error("--audio-codec cannot be combined with --expect-no-audio")
    if not math.isfinite(args.duration_tolerance_frames) or args.duration_tolerance_frames < 0:
        parser.error("--duration-tolerance-frames must be finite and non-negative")
    if args.width is not None and args.width <= 0:
        parser.error("--width must be greater than 0")
    if args.height is not None and args.height <= 0:
        parser.error("--height must be greater than 0")
    if not math.isfinite(args.fps_tolerance) or args.fps_tolerance < 0:
        parser.error("--fps-tolerance must be finite and non-negative")
    if not math.isfinite(args.aspect_tolerance) or args.aspect_tolerance < 0:
        parser.error("--aspect-tolerance must be finite and non-negative")
    if (
        not math.isfinite(args.black_min_duration)
        or not math.isfinite(args.silence_min_duration)
        or args.black_min_duration <= 0
        or args.silence_min_duration <= 0
    ):
        parser.error("diagnostic minimum durations must be finite and greater than 0")
    if not math.isfinite(args.black_picture_threshold) or not 0 < args.black_picture_threshold <= 1:
        parser.error("--black-picture-threshold must be finite and in (0, 1]")

    json_path = args.json.expanduser().resolve() if args.json else None
    if json_path and paths_alias(source, json_path):
        print(f"error: JSON output aliases the input video: {json_path}", file=sys.stderr)
        return 2
    if json_path and json_path.exists() and not args.overwrite:
        print(
            f"error: refusing to overwrite {json_path}; pass --overwrite or choose another --json path",
            file=sys.stderr,
        )
        return 2

    try:
        probe = probe_video(source, args.ffprobe)
        video = first_stream(probe, "video")
        audio = first_stream(probe, "audio")
        if video is None:
            raise ToolError("Input contains no video stream")

        duration_source = "video stream"
        video_duration = positive_float(video.get("duration"))
        container_duration = positive_float(probe.get("format", {}).get("duration"))
        audio_duration = positive_float(audio.get("duration")) if audio else None
        duration = video_duration
        if duration is None:
            duration_source = "container format"
            duration = container_duration
        if duration is None:
            raise ToolError("Could not determine a positive video duration")
        fps = rational_float(video.get("avg_frame_rate")) or rational_float(
            video.get("r_frame_rate")
        )
        aspect, aspect_source = display_aspect(video)

        checks: list[dict[str, Any]] = []
        if args.duration is not None:
            fps_basis = args.fps or fps
            if fps_basis is None:
                raise ToolError("Cannot apply frame-based duration tolerance without a frame rate")
            delta_seconds = abs(duration - args.duration)
            delta_frames = delta_seconds * fps_basis
            add_check(
                checks,
                "duration",
                args.duration,
                duration,
                # ffprobe commonly rounds duration strings to six decimal places.
                delta_frames <= args.duration_tolerance_frames + 1e-3,
                (
                    f"absolute error {delta_seconds:.6f}s = {delta_frames:.3f} frames at "
                    f"{fps_basis:.6f} fps; allowed {args.duration_tolerance_frames:.3f} frames; "
                    f"observed from {duration_source}"
                ),
            )
        if args.width is not None:
            add_check(
                checks,
                "width",
                args.width,
                video.get("width"),
                video.get("width") == args.width,
                "coded frame width in pixels",
            )
        if args.height is not None:
            add_check(
                checks,
                "height",
                args.height,
                video.get("height"),
                video.get("height") == args.height,
                "coded frame height in pixels",
            )
        if args.fps is not None:
            add_check(
                checks,
                "average_fps",
                args.fps,
                fps,
                fps is not None and abs(fps - args.fps) <= args.fps_tolerance + 1e-9,
                f"allowed absolute error {args.fps_tolerance:.6f} fps",
            )
        if args.aspect is not None:
            add_check(
                checks,
                "display_aspect_ratio",
                args.aspect,
                aspect,
                aspect is not None and abs(aspect - args.aspect) <= args.aspect_tolerance + 1e-9,
                f"allowed absolute ratio error {args.aspect_tolerance:.6f}; observed from {aspect_source}",
            )
        if args.video_codec:
            expected = args.video_codec.lower()
            observed = str(video.get("codec_name", "")).lower() or None
            add_check(checks, "video_codec", expected, observed, observed == expected, "ffprobe codec_name")
        if args.expect_audio or args.expect_no_audio:
            expected_audio = args.expect_audio
            add_check(
                checks,
                "audio_present",
                expected_audio,
                audio is not None,
                (audio is not None) == expected_audio,
                "presence of a primary audio stream",
            )
        if args.audio_codec:
            expected = args.audio_codec.lower()
            observed = str(audio.get("codec_name", "")).lower() if audio else None
            add_check(
                checks,
                "audio_codec",
                expected,
                observed,
                observed == expected,
                "ffprobe codec_name; this also requires an audio stream",
            )

        decode_result: dict[str, Any] = {"requested": args.decode, "passed": None}
        if args.decode:
            try:
                run_command(
                    [
                        args.ffmpeg,
                        "-hide_banner",
                        "-nostats",
                        "-loglevel",
                        "error",
                        "-xerror",
                        "-i",
                        str(source),
                        "-map",
                        "0:v:0",
                        "-map",
                        "0:a:0?",
                        "-f",
                        "null",
                        "-",
                    ]
                )
                decode_result = {"requested": True, "passed": True, "detail": "primary streams decoded"}
            except ToolError as exc:
                decode_result = {"requested": True, "passed": False, "detail": str(exc)}
                add_check(checks, "decode", "successful decode", "decode error", False, str(exc))

        diagnostics: dict[str, Any] = {"requested": args.diagnostics}
        warnings: list[str] = []
        if args.diagnostics:
            black = black_diagnostics(
                source,
                args.ffmpeg,
                duration,
                args.black_min_duration,
                args.black_picture_threshold,
            )
            diagnostics["black"] = black
            if black["intervals"]:
                warnings.append(
                    f"Review {len(black['intervals'])} detected black interval(s), "
                    f"{black['total_seconds']:.3f}s total; fades and pauses may be intentional."
                )
            if audio is None:
                diagnostics["audio"] = {"status": "not_run", "reason": "no audio stream"}
            else:
                audio_result = audio_diagnostics(
                    source,
                    args.ffmpeg,
                    audio_duration or container_duration or duration,
                    args.silence_min_duration,
                    args.silence_noise_threshold,
                )
                diagnostics["audio"] = audio_result
                if audio_result["silence_intervals"]:
                    warnings.append(
                        f"Review {len(audio_result['silence_intervals'])} detected silence interval(s), "
                        f"{audio_result['silence_total_seconds']:.3f}s total; pauses may be intentional."
                    )

        summary = {
            "duration_seconds": duration,
            "duration_source": duration_source,
            "video_duration_seconds": video_duration,
            "container_duration_seconds": container_duration,
            "audio_duration_seconds": audio_duration,
            "width": video.get("width"),
            "height": video.get("height"),
            "average_fps": fps,
            "display_aspect_ratio": aspect,
            "display_aspect_source": aspect_source,
            "video_codec": video.get("codec_name"),
            "pixel_format": video.get("pix_fmt"),
            "audio_present": audio is not None,
            "audio_codec": audio.get("codec_name") if audio else None,
            "audio_channels": audio.get("channels") if audio else None,
            "audio_sample_rate": audio.get("sample_rate") if audio else None,
        }
        failed = [check for check in checks if not check["passed"]]
        report = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(source),
            "status": "fail" if failed else "pass",
            "summary": summary,
            "checks": checks,
            "decode": decode_result,
            "diagnostics": diagnostics,
            "warnings": warnings,
            "creative_quality_assessed": False,
            "limitations": [
                "A technical pass does not guarantee pacing, legibility, narrative clarity, or creative quality.",
                "Black and silence detectors use thresholds and require human interpretation.",
            ],
        }
        if json_path:
            write_json(json_path, report)
    except (ToolError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Video: {source}")
    print(
        f"Observed: {duration:.3f}s | {summary['width']}x{summary['height']} | "
        f"{format_optional_number(fps)} fps | DAR {format_optional_number(aspect)} | "
        f"video {summary['video_codec']} | "
        f"audio {summary['audio_codec'] or 'none'}"
    )
    print(
        "Durations: "
        f"video {format_optional_duration(summary['video_duration_seconds'])} | "
        f"container {format_optional_duration(summary['container_duration_seconds'])} | "
        f"audio {format_optional_duration(summary['audio_duration_seconds'])}"
    )
    if checks:
        for check in checks:
            marker = "PASS" if check["passed"] else "FAIL"
            print(f"[{marker}] {check['name']}: expected {check['expected']!r}, observed {check['observed']!r}")
            print(f"       {check['detail']}")
    else:
        print("No delivery invariants requested; metadata was inventoried only.")
    if args.diagnostics:
        black = diagnostics["black"]
        print(
            f"Diagnostics: black {len(black['intervals'])} interval(s), "
            f"{black['total_seconds']:.3f}s total"
        )
        audio_result = diagnostics["audio"]
        if audio_result["status"] == "completed":
            print(
                f"             silence {len(audio_result['silence_intervals'])} interval(s), "
                f"{audio_result['silence_total_seconds']:.3f}s total; "
                f"volume mean {audio_result['mean_volume_db']} dB, max {audio_result['max_volume_db']} dB"
            )
        else:
            print("             audio diagnostics not run: no audio stream")
    for warning in warnings:
        print(f"[WARN] {warning}")
    if json_path:
        print(f"JSON report: {json_path}")
    print("Technical verification does not assess creative quality; review the video at playback speed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
