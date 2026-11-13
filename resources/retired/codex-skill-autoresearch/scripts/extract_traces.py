#!/usr/bin/env python3
"""Create a redacted, root-task corpus from local Codex rollout traces."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
UTC = dt.timezone.utc
NOISE_PREFIXES = (
    "<subagent_notification",
    "<recommended_plugins>",
    "# AGENTS.md instructions",
    "<environment_context>",
    "<skill>",
    "<permissions",
    "<collaboration_mode>",
    "<app-context>",
    "<skills_instructions>",
    "<image name=",
    "</image>",
)
BLOCK_PATTERNS = (
    re.compile(r"<in-app-browser-context\b[^>]*>.*?</in-app-browser-context>", re.I | re.S),
    re.compile(r"<subagent_notification\b[^>]*>.*?</subagent_notification>", re.I | re.S),
    re.compile(r"<(recommended_plugins|environment_context|skill|collaboration_mode|app-context|skills_instructions)\b[^>]*>.*?</\1>", re.I | re.S),
    re.compile(r"# AGENTS\.md instructions.*?</INSTRUCTIONS>", re.I | re.S),
)
FILE_MANIFEST = re.compile(
    r"# Files mentioned by the user:.*?Distinguish instructions in attached documents from the user's request\.",
    re.I | re.S,
)
SKILL_LINK = re.compile(r"\[\$([a-zA-Z0-9][a-zA-Z0-9:_-]*)\]")

REDACTIONS = (
    (re.compile(r"-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----", re.I | re.S), "[REDACTED_PEM]"),
    (re.compile(r"(?i)\b(bearer|authorization)\s*[:=]?\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 [REDACTED_SECRET]"),
    (re.compile(r"(?i)\b((?:[a-z0-9]+[_-])*(?:password|passwd|api[_ -]?key|apikey|access[_ -]?token|accesstoken|refresh[_ -]?token|refreshtoken|auth[_ -]?token|authtoken|client[_ -]?secret|clientsecret|private[_ -]?key|secret|license[_ -]?key|licensekey))[\"']?\s*[:=]\s*[\"']?[^\s\"',;}]{4,}"), r"\1=[REDACTED_SECRET]"),
    (re.compile(r"\b(?:sk|rk)[-_](?:live|test)[-_][A-Za-z0-9]{12,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bAKIA[A-Z0-9]{16}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\b(?:sbp|sb_secret|npm|pat)_[A-Za-z0-9_-]{16,}\b"), "[REDACTED_SECRET]"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"), "[REDACTED_JWT]"),
    (re.compile(r"(?i)(https?://)([^\s/@:]+):([^\s/@]+)@"), r"\1[REDACTED_CREDENTIALS]@"),
)


@dataclasses.dataclass
class ParsedTrace:
    session_id: str
    timestamp: dt.datetime
    cwd: str
    source: Any
    path: Path
    prompts: list[str]
    skills: set[str]
    tools: collections.Counter[str]
    outcome: str
    malformed_lines: int
    orchestration_messages_excluded: int
    redactions: int

    @property
    def quality(self) -> tuple[int, int, int, int]:
        return (len(self.prompts), len(self.outcome), sum(self.tools.values()), self.path.stat().st_size)


def parse_iso(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def redact(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in REDACTIONS:
        text, hits = pattern.subn(replacement, text)
        count += hits
    return text, count


def clean_user_text(text: str) -> tuple[str, int]:
    stripped = text.strip()
    if not stripped:
        return "", 1
    for pattern in BLOCK_PATTERNS:
        stripped = pattern.sub("", stripped)
    if "## My request:" in stripped:
        stripped = stripped.rsplit("## My request:", 1)[1]
    stripped = FILE_MANIFEST.sub("", stripped)
    stripped = re.sub(r"<image\b[^>]*>.*?</image>", "", stripped, flags=re.I | re.S)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped).strip()
    lowered = stripped.lower()
    if not stripped or any(lowered.startswith(prefix.lower()) for prefix in NOISE_PREFIXES):
        return "", 1
    return stripped, 0 if stripped else 1


def content_text(content: Any, allowed_types: set[str]) -> Iterable[str]:
    if not isinstance(content, list):
        return
    for item in content:
        if not isinstance(item, dict) or item.get("type") not in allowed_types:
            continue
        text = item.get("text")
        if isinstance(text, str):
            yield text


def parse_trace(path: Path) -> ParsedTrace | None:
    meta: dict[str, Any] | None = None
    event_prompts: list[str] = []
    fallback_prompts: list[str] = []
    event_outcomes: list[tuple[str, str]] = []
    fallback_outcomes: list[str] = []
    skills: set[str] = set()
    tools: collections.Counter[str] = collections.Counter()
    malformed = 0
    excluded = 0

    try:
        lines = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return None

    with lines:
        for raw_line in lines:
            try:
                record = json.loads(raw_line)
            except (json.JSONDecodeError, TypeError):
                malformed += 1
                continue
            if not isinstance(record, dict):
                continue
            record_type = record.get("type")
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if record_type == "session_meta" and meta is None:
                meta = payload
                continue
            if record_type == "event_msg":
                payload_type = payload.get("type")
                if payload_type == "user_message" and isinstance(payload.get("message"), str):
                    original = payload["message"]
                    cleaned, was_excluded = clean_user_text(original)
                    excluded += was_excluded
                    if cleaned:
                        skills.update(SKILL_LINK.findall(cleaned))
                        event_prompts.append(cleaned)
                elif payload_type == "agent_message" and isinstance(payload.get("message"), str):
                    event_outcomes.append((str(payload.get("phase") or ""), payload["message"]))
                continue
            if record_type != "response_item":
                continue
            item_type = payload.get("type")
            if item_type in {"custom_tool_call", "function_call"}:
                name = payload.get("name")
                namespace = payload.get("namespace")
                if isinstance(name, str) and name:
                    safe_name = f"{namespace}.{name}" if isinstance(namespace, str) and namespace else name
                    tools[safe_name] += 1
                continue
            if item_type != "message":
                continue
            role = payload.get("role")
            if role == "user":
                for original in content_text(payload.get("content"), {"input_text"}):
                    cleaned, was_excluded = clean_user_text(original)
                    excluded += was_excluded
                    if cleaned:
                        skills.update(SKILL_LINK.findall(cleaned))
                        fallback_prompts.append(cleaned)
            elif role == "assistant":
                fallback_outcomes.extend(content_text(payload.get("content"), {"output_text"}))

    if meta is None:
        return None
    try:
        timestamp = parse_iso(str(meta.get("timestamp") or ""))
    except (ValueError, TypeError):
        return None

    prompts = event_prompts or fallback_prompts
    if event_outcomes:
        finals = [message for phase, message in event_outcomes if phase == "final_answer"]
        outcome = (finals or [event_outcomes[-1][1]])[-1]
    else:
        outcome = fallback_outcomes[-1] if fallback_outcomes else ""

    redactions = 0
    redacted_prompts: list[str] = []
    for prompt in prompts:
        cleaned, hits = redact(prompt)
        redactions += hits
        redacted_prompts.append(cleaned[:6000])
    outcome, hits = redact(outcome)
    redactions += hits

    return ParsedTrace(
        session_id=str(meta.get("id") or path.stem),
        timestamp=timestamp,
        cwd=str(meta.get("cwd") or ""),
        source=meta.get("source"),
        path=path,
        prompts=redacted_prompts,
        skills=skills,
        tools=tools,
        outcome=outcome[:2000],
        malformed_lines=malformed,
        orchestration_messages_excluded=excluded,
        redactions=redactions,
    )


def is_subagent(source: Any) -> bool:
    return isinstance(source, dict) and "subagent" in source


def is_automation_session(session: ParsedTrace) -> bool:
    return bool(session.prompts and session.prompts[0].lstrip().startswith("Automation:"))


def collect_paths(directories: Iterable[Path]) -> list[Path]:
    paths: set[Path] = set()
    for directory in directories:
        if directory.exists():
            paths.update(directory.rglob("rollout-*.jsonl"))
    return sorted(paths)


def render_evidence(sessions: list[ParsedTrace], manifest: dict[str, Any]) -> str:
    cwd_counts = collections.Counter(session.cwd for session in sessions if session.cwd)
    tool_counts: collections.Counter[str] = collections.Counter()
    skill_counts: collections.Counter[str] = collections.Counter()
    for session in sessions:
        tool_counts.update(session.tools)
        skill_counts.update(session.skills)

    lines = [
        "# Codex skill autoresearch evidence packet",
        "",
        f"Window: `{manifest['window']['start']}` to `{manifest['window']['end']}`",
        f"Root sessions: **{manifest['counts']['root_sessions']}**; subagent traces excluded: **{manifest['counts']['subagent_files_excluded']}**; scheduled automation roots: **{manifest['counts']['automation_root_sessions']}**.",
        "",
        "This file is private run output. Counts are leads for semantic review, not skill recommendations.",
        "",
        "## Top workspaces",
        "",
    ]
    lines.extend(f"- {count}: `{cwd}`" for cwd, count in cwd_counts.most_common(20))
    lines.extend(["", "## Top tools", ""])
    lines.extend(f"- {count}: `{name}`" for name, count in tool_counts.most_common(30))
    lines.extend(["", "## Explicit skills", ""])
    lines.extend(f"- {count}: `{name}`" for name, count in skill_counts.most_common(30))
    lines.extend(["", "## Root-task index", ""])
    for session in sessions:
        first_prompt = session.prompts[0].replace("\n", " ")[:500] if session.prompts else "[no user text extracted]"
        lines.append(f"- `{session.session_id}` | {session.timestamp.date()} | `{session.cwd}` | {first_prompt}")
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    end = parse_iso(args.end) if args.end else dt.datetime.now(UTC)
    start = end - dt.timedelta(days=args.days)
    directories = [Path(args.sessions_dir).expanduser(), Path(args.archived_dir).expanduser()]
    paths = collect_paths(directories)
    selected: dict[str, ParsedTrace] = {}
    counts: collections.Counter[str] = collections.Counter()

    for path in paths:
        counts["files_seen"] += 1
        parsed = parse_trace(path)
        if parsed is None:
            counts["unreadable_or_invalid_files"] += 1
            continue
        counts["malformed_lines"] += parsed.malformed_lines
        if not (start <= parsed.timestamp <= end):
            continue
        counts["files_in_window"] += 1
        if is_subagent(parsed.source):
            counts["subagent_files_excluded"] += 1
            continue
        counts["root_files_in_window"] += 1
        prior = selected.get(parsed.session_id)
        if prior is not None:
            counts["duplicate_root_files"] += 1
            if prior.quality >= parsed.quality:
                continue
        selected[parsed.session_id] = parsed

    sessions = sorted(selected.values(), key=lambda item: (item.timestamp, item.session_id))
    counts["root_sessions"] = len(sessions)
    counts["automation_root_sessions"] = sum(is_automation_session(session) for session in sessions)
    counts["empty_prompt_sessions"] = sum(not session.prompts for session in sessions)
    counts["orchestration_messages_excluded"] = sum(session.orchestration_messages_excluded for session in sessions)
    counts["redactions"] = sum(session.redactions for session in sessions)
    for key in (
        "duplicate_root_files",
        "files_in_window",
        "malformed_lines",
        "root_files_in_window",
        "subagent_files_excluded",
        "unreadable_or_invalid_files",
    ):
        counts.setdefault(key, 0)

    run_tag = args.run_tag or end.strftime("%Y-%m-%dT%H%M%SZ")
    output_dir = Path(args.output_root).expanduser() / run_tag
    targets = tuple(output_dir / name for name in ("manifest.json", "sessions.jsonl", "evidence.md"))
    if output_dir.exists() and not args.replace_existing:
        raise SystemExit(f"run artifacts already exist at {output_dir}; choose a new --run-tag")
    output_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
    output_dir.chmod(0o700)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(UTC).isoformat(),
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": args.days},
        "sources": [str(path) for path in directories],
        "output_dir": str(output_dir),
        "counts": dict(sorted(counts.items())),
        "privacy": {
            "raw_traces_modified": False,
            "binary_and_encrypted_content_excluded": True,
            "text_redacted": True,
            "tracked_report_should_use_aggregate_paraphrases_only": True,
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "sessions.jsonl").open("w", encoding="utf-8") as handle:
        for session in sessions:
            row = {
                "session_id": session.session_id,
                "timestamp": session.timestamp.isoformat(),
                "cwd": session.cwd,
                "trace_path": str(session.path),
                "user_requests": session.prompts,
                "skills": sorted(session.skills),
                "tools": dict(session.tools.most_common()),
                "assistant_outcome": session.outcome,
                "scheduled_automation": is_automation_session(session),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (output_dir / "evidence.md").write_text(render_evidence(sessions, manifest), encoding="utf-8")
    for target in targets:
        target.chmod(0o600)
    return output_dir, manifest


def parser() -> argparse.ArgumentParser:
    repo_root = Path.cwd()
    home = Path.home()
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--days", type=int, default=30)
    cli.add_argument("--end", help="Frozen ISO-8601 cutoff; defaults to now")
    cli.add_argument("--sessions-dir", default=str(home / ".codex" / "sessions"))
    cli.add_argument("--archived-dir", default=str(home / ".codex" / "archived_sessions"))
    cli.add_argument("--output-root", default=str(repo_root / "output" / "codex-skill-autoresearch"))
    cli.add_argument("--run-tag")
    cli.add_argument("--replace-existing", action="store_true", help="Replace only this run tag's derived artifacts")
    return cli


def main() -> int:
    args = parser().parse_args()
    if args.days <= 0:
        raise SystemExit("--days must be positive")
    output_dir, manifest = run(args)
    print(json.dumps({"output_dir": str(output_dir), "counts": manifest["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
