#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fal-client"]
# ///
"""Generic Fal queue client: upload @paths, submit, poll, download media, log spend.

    uv run scripts/fal_run.py ENDPOINT_ID --input input.json|'{"json":...}' --out DIR
        [--label S08] [--est-usd 0.4] [--spend-log spend.jsonl] [--cap-usd 25] [--timeout 1800]

Any string value in the input that starts with "@" is a local path: it is uploaded
and replaced with the hosted URL. Writes DIR/result.json, downloads every media URL
found in the result into DIR, appends one line to the spend log, and prints a JSON
summary to stdout. Reads FAL_KEY from the environment (never printed).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import mimetypes
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRICES_PATH = Path(__file__).resolve().parent.parent / "references" / "prices.json"
MEDIA_EXT = {"audio/wav": ".wav", "audio/x-wav": ".wav", "audio/mpeg": ".mp3",
             "video/mp4": ".mp4", "image/png": ".png", "image/jpeg": ".jpg",
             "image/webp": ".webp"}


class FalRunError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- pricing
def _to_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        m = re.search(r"\d+(?:\.\d+)?", value)
        return float(m.group()) if m else None
    return None


def _price_entry(endpoint: str, prices: dict) -> dict | None:
    if endpoint in prices and not endpoint.startswith("_"):
        return prices[endpoint]
    matches = [k for k in prices if not k.startswith("_") and "*" in k and fnmatch.fnmatch(endpoint, k)]
    return prices[max(matches, key=len)] if matches else None


def _variant_matches(when: dict, payload: dict) -> bool:
    return all(k in payload and str(payload[k]).lower() == str(v).lower() for k, v in when.items())


def estimate_usd(endpoint: str, payload: dict, prices_path: Path = PRICES_PATH) -> float | None:
    """Cost estimate from references/prices.json, or None when not computable."""
    try:
        prices = json.loads(prices_path.read_text())
    except (OSError, ValueError) as exc:
        log(f"warning: cannot read {prices_path}: {exc}")
        return None
    entry = _price_entry(endpoint, prices)
    if not entry or entry.get("usd") is None:
        return None
    rate = entry["usd"]
    for variant in entry.get("variants", []):
        if _variant_matches(variant.get("when", {}), payload):
            rate = variant["usd"]
    unit = entry.get("unit")
    if unit == "per_second":
        qty = _to_number(payload.get("duration"))
    elif unit == "per_image":
        qty = _to_number(payload.get("num_images")) or 1.0
    elif unit == "per_1k_chars":
        text = payload.get("prompt")
        qty = len(text) / 1000 if isinstance(text, str) else None
        if qty is None and isinstance(payload.get("turns"), list):
            qty = sum(len(str(t.get("text", ""))) for t in payload["turns"] if isinstance(t, dict)) / 1000
    else:
        qty = None
    return None if qty is None else round(rate * qty, 5)


def spent_so_far(spend_log: Path) -> float:
    total = 0.0
    if not spend_log.exists():
        return total
    for line in spend_log.read_text().splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line).get("est_usd")
        except ValueError:
            raise FalRunError(f"{spend_log} has a line that is not JSON: {line[:80]}")
        if isinstance(value, (int, float)):
            total += value
    return total


def append_spend(spend_log: Path, row: dict) -> None:
    spend_log.parent.mkdir(parents=True, exist_ok=True)
    with spend_log.open("a") as fh:
        fh.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------- input / output
def resolve_uploads(node: Any, fal_client: Any) -> Any:
    if isinstance(node, str) and node.startswith("@"):
        path = Path(node[1:]).expanduser()
        if not path.is_file():
            raise FalRunError(f"input path does not exist: {path}")
        log(f"uploading {path}")
        return fal_client.upload_file(str(path))
    if isinstance(node, list):
        return [resolve_uploads(v, fal_client) for v in node]
    if isinstance(node, dict):
        return {k: resolve_uploads(v, fal_client) for k, v in node.items()}
    return node


def find_media(node: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], dict]]:
    found = []
    if isinstance(node, dict):
        if isinstance(node.get("url"), str) and node["url"].startswith("http"):
            found.append((path, node))
        else:
            for k, v in node.items():
                found += find_media(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += find_media(v, path + (str(i),))
    return found


def _extension(info: dict) -> str:
    name = info.get("file_name") or info["url"].split("?")[0]
    ext = Path(name).suffix
    if ext:
        return ext
    ctype = info.get("content_type") or mimetypes.guess_type(info["url"])[0] or ""
    return MEDIA_EXT.get(ctype, ".bin")


def download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "motion-video/fal_run"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp, tmp.open("wb") as fh:
            while chunk := resp.read(1 << 20):
                fh.write(chunk)
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        raise FalRunError(f"download failed for {url.split('?')[0]}: {exc}") from exc
    tmp.replace(dest)


def download_media(result: Any, out_dir: Path) -> list[str]:
    files = []
    for path, info in find_media(result):
        stem = "_".join(path) or "file"
        dest = out_dir / f"{stem}{_extension(info)}"
        download(info["url"], dest)
        files.append(str(dest))
    return files


# ---------------------------------------------------------------- main entry
def run(endpoint: str, payload: dict, out_dir: Path, label: str | None = None,
        est_usd: float | None = None, spend_log: Path = Path("spend.jsonl"),
        timeout: float = 1800, cap_usd: float | None = None) -> dict:
    """Run one Fal call. Returns {endpoint, request_id, files, est_usd, result}."""
    if not os.environ.get("FAL_KEY"):
        raise FalRunError("FAL_KEY is not set")
    import fal_client  # local import so --help works without the dependency

    if est_usd is None:
        est_usd = estimate_usd(endpoint, payload)
    if est_usd is None:
        log("warning: no cost estimate (no --est-usd and no matching price); logging est_usd null")
    spent = spent_so_far(spend_log)
    if cap_usd is not None and spent + (est_usd or 0) > cap_usd:
        raise FalRunError(f"cap exceeded: spent ${spent:.4f} + this call ${est_usd or 0:.4f} > cap ${cap_usd:.2f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    payload = resolve_uploads(payload, fal_client)
    handle = fal_client.submit(endpoint, arguments=payload)
    request_id = handle.request_id
    log(f"submitted {endpoint} request_id={request_id}")
    row = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), "endpoint": endpoint,
           "label": label, "request_id": request_id, "est_usd": est_usd, "status": "ok"}
    try:
        deadline = time.monotonic() + timeout
        seen_logs = 0
        last = None
        while True:
            status = handle.status(with_logs=True)
            if isinstance(status, fal_client.Queued):
                if last != ("q", status.position):
                    log(f"queued, position {status.position}")
                    last = ("q", status.position)
            elif isinstance(status, fal_client.InProgress):
                for entry in (status.logs or [])[seen_logs:]:
                    log(f"log: {entry.get('message', entry)}")
                seen_logs = len(status.logs or [])
                if last != ("p",):
                    log("in progress")
                    last = ("p",)
            elif isinstance(status, fal_client.Completed):
                break
            if time.monotonic() > deadline:
                raise FalRunError(f"timed out after {timeout}s (request_id={request_id}; it may still be billed)")
            time.sleep(2)
        result = handle.get()
        (out_dir / "result.json").write_text(json.dumps(result, indent=2))
        files = download_media(result, out_dir)
    except BaseException as exc:
        row["status"] = "failed"
        row["error"] = str(exc)[:300]
        append_spend(spend_log, row)
        if isinstance(exc, (FalRunError, KeyboardInterrupt)):
            raise
        raise FalRunError(f"{endpoint} failed: {str(exc)[:400]}") from exc
    append_spend(spend_log, row)
    return {"endpoint": endpoint, "request_id": request_id, "files": files, "est_usd": est_usd, "result": result}


def load_input(arg: str) -> dict:
    text = arg.strip()
    try:
        data = json.loads(text) if text.startswith("{") else json.loads(Path(arg).expanduser().read_text())
    except (OSError, ValueError) as exc:
        raise FalRunError(f"cannot read --input: {exc}") from exc
    if not isinstance(data, dict):
        raise FalRunError("--input must be a JSON object")
    return data


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("endpoint")
    p.add_argument("--input", required=True, help="path to a JSON file, or an inline JSON object")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--label")
    p.add_argument("--est-usd", type=float)
    p.add_argument("--spend-log", type=Path, default=Path("spend.jsonl"))
    p.add_argument("--cap-usd", type=float, help="refuse if logged spend plus this call would exceed the cap")
    p.add_argument("--timeout", type=float, default=1800)
    args = p.parse_args()
    try:
        res = run(args.endpoint, load_input(args.input), args.out, args.label, args.est_usd,
                  args.spend_log, args.timeout, args.cap_usd)
    except FalRunError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # fal_client errors: fail noisily, without echoing the payload
        print(f"error: {type(exc).__name__}: {str(exc)[:500]}", file=sys.stderr)
        return 1
    res.pop("result")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
