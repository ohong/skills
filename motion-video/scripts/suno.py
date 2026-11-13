#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Generate a music bed through a sunoapi.org-compatible API.

There is no official Suno API. This targets the third-party sunoapi.org service.
Env: SUNO_API_KEY (required), SUNO_API_BASE (default https://api.sunoapi.org).

Verified against docs.sunoapi.org: POST /api/v1/generate returns
{code, msg, data:{taskId}}; GET /api/v1/generate/record-info?taskId=... returns
data.status (PENDING, TEXT_SUCCESS, FIRST_SUCCESS, SUCCESS, or a *_FAILED/*_ERROR
state) and data.response.sunoData[] with id, audio_url, duration. Not verified
against a live account (no key was available when this was written).

Usage:
  uv run scripts/suno.py --prompt "sparse felt piano, 84 bpm" --instrumental \
      --duration 90 --out music/bed --spend-log spend.jsonl
Writes music/bed-1.mp3, music/bed-2.mp3 and music/bed.result.json.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

FALLBACK = (
    "SUNO_API_KEY is not set, so no Suno request was made.\n"
    "Use the Fal music model instead:\n"
    "  uv run scripts/fal_run.py fal-ai/elevenlabs/music --input "
    "'{\"prompt\":\"...\",\"music_length_ms\":90000,\"force_instrumental\":true}' --out music/bed\n"
    "or use a cleared library track."
)
DUMMY_CALLBACK = "https://example.com/noop"  # required by the API; we poll instead
FAILED = {"CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED", "CALLBACK_EXCEPTION", "SENSITIVE_WORD_ERROR"}


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def request(method, url, key, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "motion-video-skill/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        die(f"{method} {url} -> HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
    except (urllib.error.URLError, TimeoutError) as e:
        die(f"{method} {url} failed: {e}")
    if isinstance(payload, dict) and payload.get("code") not in (None, 200):
        die(f"API error {payload.get('code')}: {payload.get('msg')}")
    return payload


def build_payload(a):
    custom = bool(a.style or a.title or a.duration)
    p = {"customMode": custom, "instrumental": a.instrumental, "model": a.model,
         "callBackUrl": DUMMY_CALLBACK}
    if custom:
        # In custom mode `prompt` is used as lyrics, so an instrumental brief goes into `style`.
        if a.instrumental:
            style = ". ".join(x for x in (a.style, a.prompt) if x)
            p["style"] = style[:1000]
            if len(style) > 1000:
                print("warning: style+prompt truncated to 1000 chars", file=sys.stderr)
        else:
            p["prompt"] = a.prompt
            if a.style:
                p["style"] = a.style[:1000]
        if a.title:
            p["title"] = a.title[:80]
        if a.duration:
            p["duration"] = int(a.duration)
    else:
        p["prompt"] = a.prompt[:3000]
    return p


def download(url, dest):
    tmp = dest + ".part"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "motion-video-skill/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 16):
                f.write(chunk)
        if os.path.getsize(tmp) == 0:
            die(f"downloaded 0 bytes from {url}")
        os.replace(tmp, dest)
    except (urllib.error.URLError, TimeoutError) as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        die(f"download failed for {dest}: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--style")
    ap.add_argument("--title")
    ap.add_argument("--instrumental", action="store_true")
    ap.add_argument("--model", default="V6")
    ap.add_argument("--duration", type=int, help="seconds, 10-360; forces custom mode")
    ap.add_argument("--out", required=True, help="output prefix, e.g. music/bed")
    ap.add_argument("--spend-log", help="append a JSON line to this file (e.g. spend.jsonl)")
    ap.add_argument("--timeout", type=int, default=600, help="poll timeout in seconds")
    a = ap.parse_args()

    key = os.environ.get("SUNO_API_KEY")
    if not key:
        print(FALLBACK, file=sys.stderr)
        sys.exit(2)
    if a.duration is not None and not 10 <= a.duration <= 360:
        die("--duration must be 10-360 seconds")
    base = os.environ.get("SUNO_API_BASE", "https://api.sunoapi.org").rstrip("/")

    payload = build_payload(a)
    resp = request("POST", f"{base}/api/v1/generate", key, payload)
    task_id = (resp.get("data") or {}).get("taskId")
    if not task_id:
        die(f"no taskId in response: {json.dumps(resp)[:300]}")
    print(f"task {task_id} submitted; polling (timeout {a.timeout}s)", file=sys.stderr)

    if a.spend_log:  # log at submit time: the credits are spent even if polling later fails
        with open(a.spend_log, "a") as f:
            f.write(json.dumps({
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "endpoint": "suno", "label": a.title or a.prompt[:60],
                "task_id": task_id, "est_usd": None}) + "\n")

    deadline = time.time() + a.timeout
    while True:
        r = request("GET", f"{base}/api/v1/generate/record-info?taskId={task_id}", key)
        data = r.get("data") or {}
        status = data.get("status")
        if status == "SUCCESS":
            break
        if status in FAILED:
            die(f"task {task_id} failed: {status} {data.get('errorMessage') or ''}")
        if time.time() > deadline:
            die(f"timed out after {a.timeout}s (last status {status}); task_id {task_id} may still finish, "
                f"re-check it with GET /api/v1/generate/record-info?taskId={task_id}")
        time.sleep(10)

    tracks = ((data.get("response") or {}).get("sunoData")) or []
    tracks = [t for t in tracks if t.get("audio_url")]
    if not tracks:
        die(f"task {task_id} succeeded but returned no audio_url: {json.dumps(data)[:300]}")

    out_dir = os.path.dirname(a.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    files = []
    for i, t in enumerate(tracks, 1):
        dest = f"{a.out}-{i}.mp3"
        download(t["audio_url"], dest)
        files.append(dest)
        print(f"{dest}  {t.get('duration')}s  id={t.get('id')}")
    with open(f"{a.out}.result.json", "w") as f:
        json.dump({"task_id": task_id, "request": payload, "files": files, "response": data}, f, indent=2)
    print(f"result: {a.out}.result.json")


if __name__ == "__main__":
    main()
