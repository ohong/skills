#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Find and download Creative Commons footage with yt-dlp.

  find_clips.py search "Tacoma Narrows bridge collapse" --n 20 --out footage/candidates.json
  find_clips.py get URL --section 12.5-18.0 --out footage/x.mp4 [--max-height 1080] [--ledger assets.md]

`search` keeps only results whose yt-dlp `license` field contains "Creative Commons".
`get` refuses any video without that license unless --license-override "reason" is given
(for cleared material); the override reason is recorded in the ledger.
The uploader's license claim is not proof: check for re-uploads of broadcast/film/music content.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def need_ytdlp():
    if not shutil.which("yt-dlp"):
        die("yt-dlp not found on PATH (brew install yt-dlp)")


def is_cc(info):
    return "creative commons" in (info.get("license") or "").lower()


def fmt_dur(s):
    if not s:
        return "?"
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


def cmd_search(a):
    need_ytdlp()
    # Not --flat-playlist: flat results omit the `license` field.
    p = subprocess.run(["yt-dlp", f"ytsearch{a.n}:{a.query}", "--dump-json", "--no-download",
                        "--ignore-errors", "--no-warnings"], capture_output=True, text=True)
    entries = []
    for line in p.stdout.splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not entries:
        die(f"yt-dlp returned no results (exit {p.returncode}): {p.stderr.strip()[:300]}")
    keep = [{
        "title": e.get("title"), "channel": e.get("channel") or e.get("uploader"),
        "url": e.get("webpage_url") or e.get("url"), "duration": e.get("duration"),
        "license": e.get("license"), "upload_date": e.get("upload_date"),
        "thumbnail": e.get("thumbnail"),
    } for e in entries if is_cc(e)]
    out_dir = os.path.dirname(a.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(keep, f, indent=2)
    for i, c in enumerate(keep, 1):
        print(f"{i:>2}  {fmt_dur(c['duration']):>6}  {(c['upload_date'] or ''):8}  "
              f"{(c['channel'] or '')[:24]:24}  {(c['title'] or '')[:60]}\n      {c['url']}")
    print(f"\n{len(keep)} CC kept, {len(entries) - len(keep)} filtered out of {len(entries)} results -> {a.out}")


def parse_section(s):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*", s)
    if not m or float(m.group(2)) <= float(m.group(1)):
        die(f"--section must look like START-END in seconds with END > START, got {s!r}")
    return m.group(1), m.group(2)


def cell(x):
    return str(x if x is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def append_ledger(path, row):
    header = ("| date | file | title | channel | url | license | section | attribution |\n"
              "|---|---|---|---|---|---|---|---|\n")
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a") as f:
        if new:
            f.write(header)
        elif not open(path).read().endswith("\n"):
            f.write("\n")
        f.write("| " + " | ".join(cell(x) for x in row) + " |\n")


def cmd_get(a):
    need_ytdlp()
    start, end = parse_section(a.section)
    p = subprocess.run(["yt-dlp", "--dump-single-json", "--no-download", "--no-playlist", a.url],
                       capture_output=True, text=True)
    if p.returncode != 0:
        die(f"could not fetch metadata: {p.stderr.strip()[:300]}")
    info = json.loads(p.stdout)
    lic = info.get("license") or "none listed"
    if not is_cc(info):
        if not a.license_override:
            die(f"license is {lic!r}, not Creative Commons. Refusing. "
                "For cleared material pass --license-override \"reason\".")
        lic = f"OVERRIDE: {a.license_override} (page: {lic})"
    out_dir = os.path.dirname(a.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    h = a.max_height
    tmp_base = a.out + ".part"
    # yt-dlp appends nothing when the -o template has the extension; --merge-output-format keeps mp4.
    tmp_out = tmp_base + ".mp4"
    cmd = ["yt-dlp", "--no-playlist", "--download-sections", f"*{start}-{end}", "--force-keyframes-at-cuts",
           "-f", f"bv*[height<={h}]+ba/b[height<={h}]", "--merge-output-format", "mp4", "-o", tmp_out, a.url]
    print("+ " + " ".join(cmd), file=sys.stderr)
    r = subprocess.run(cmd)
    if r.returncode != 0 or not os.path.exists(tmp_out) or os.path.getsize(tmp_out) == 0:
        if os.path.exists(tmp_out):
            os.remove(tmp_out)
        die(f"yt-dlp download failed (exit {r.returncode})")
    os.replace(tmp_out, a.out)
    title, channel = info.get("title"), info.get("channel") or info.get("uploader")
    url = info.get("webpage_url") or a.url
    attribution = f"{title} by {channel} (CC BY) \u2014 {url}"
    if a.ledger:
        append_ledger(a.ledger, [dt.date.today().isoformat(), a.out, title, channel, url, lic,
                                 f"{start}-{end}", attribution])
        print(f"ledger row appended: {a.ledger}")
    print(f"downloaded: {os.path.abspath(a.out)}")
    print(f"attribution: {attribution}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--n", type=int, default=20)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_search)
    g = sub.add_parser("get")
    g.add_argument("url")
    g.add_argument("--section", required=True, help="START-END in seconds, e.g. 12.5-18.0")
    g.add_argument("--out", required=True)
    g.add_argument("--max-height", type=int, default=1080)
    g.add_argument("--ledger", help="markdown file to append a provenance row to (e.g. assets.md)")
    g.add_argument("--license-override", help="reason string for cleared non-CC material")
    g.set_defaults(fn=cmd_get)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
