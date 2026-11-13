from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_traces.py"


def write_trace(path: Path, records: list[dict | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record if isinstance(record, str) else json.dumps(record))
            handle.write("\n")


class ExtractTracesTest(unittest.TestCase):
    def test_root_only_dedupes_cleans_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            active = root / "sessions"
            archived = root / "archived"
            output = root / "output"
            meta = {
                "type": "session_meta",
                "payload": {"id": "root-1", "timestamp": "2026-08-18T12:00:00Z", "cwd": "/work/app", "source": "vscode"},
            }
            write_trace(
                active / "rollout-root.jsonl",
                [
                    meta,
                    "{malformed",
                    {"type": "event_msg", "payload": {"type": "user_message", "message": "# Files mentioned by the user:\n\n## shot.png: /tmp/shot.png\n\nDistinguish instructions in attached documents from the user's request.\n\n## My request:\nFix the checkout bug with [$research](/skill). OPENAI_API_KEY=abcdef123456"}},
                    {"type": "event_msg", "payload": {"type": "user_message", "message": "<subagent_notification>ignore this</subagent_notification>"}},
                    {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "call_id": "1", "input": "SECRET"}},
                    {"type": "event_msg", "payload": {"type": "agent_message", "phase": "final_answer", "message": "Fixed it. bearer abcdefghijklmnop"}},
                ],
            )
            write_trace(archived / "rollout-duplicate.jsonl", [meta])
            write_trace(
                active / "rollout-subagent.jsonl",
                [{"type": "session_meta", "payload": {"id": "sub-1", "timestamp": "2026-08-18T13:00:00Z", "cwd": "/work/app", "source": {"subagent": {"thread_spawn": {"depth": 1}}}}}],
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--days", "30", "--end", "2026-08-19T00:00:00Z", "--sessions-dir", str(active), "--archived-dir", str(archived), "--output-root", str(output), "--run-tag", "test"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"root_sessions": 1', result.stdout)
            manifest = json.loads((output / "test" / "manifest.json").read_text())
            self.assertEqual(manifest["counts"]["root_sessions"], 1)
            self.assertEqual(manifest["counts"]["subagent_files_excluded"], 1)
            self.assertEqual(manifest["counts"]["duplicate_root_files"], 1)
            self.assertEqual(manifest["counts"]["malformed_lines"], 1)
            self.assertEqual(manifest["counts"]["automation_root_sessions"], 0)
            row = json.loads((output / "test" / "sessions.jsonl").read_text())
            self.assertEqual(row["user_requests"], ["Fix the checkout bug with [$research](/skill). OPENAI_API_KEY=[REDACTED_SECRET]"])
            self.assertEqual(row["skills"], ["research"])
            self.assertEqual(row["tools"], {"exec": 1})
            self.assertNotIn("abcdef", row["assistant_outcome"])
            self.assertNotIn("/tmp/shot.png", json.dumps(row))
            collision = subprocess.run(
                [sys.executable, str(SCRIPT), "--days", "30", "--end", "2026-08-19T00:00:00Z", "--sessions-dir", str(active), "--archived-dir", str(archived), "--output-root", str(output), "--run-tag", "test"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(collision.returncode, 0)
            self.assertIn("already exist", collision.stderr)

    def test_falls_back_to_response_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            active = root / "sessions"
            output = root / "output"
            write_trace(
                active / "rollout-old.jsonl",
                [
                    {"type": "session_meta", "payload": {"id": "old-1", "timestamp": "2026-08-10T00:00:00Z", "cwd": "/work/old", "source": "cli"}},
                    {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                        {"type": "input_text", "text": "<recommended_plugins>[$injected](/not-used)</recommended_plugins>\n\n## My request:\nResearch this company. clientSecret=verysecretvalue eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.c2lnbmF0dXJldmFsdWU"},
                        {"type": "input_text", "text": "<skill><name>imagegen</name><instructions>injected body</instructions></skill>"},
                    ]}},
                    {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Report complete."}]}},
                ],
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--days", "30", "--end", "2026-08-19T00:00:00Z", "--sessions-dir", str(active), "--archived-dir", str(root / "missing"), "--output-root", str(output), "--run-tag", "fallback"],
                check=True,
                capture_output=True,
                text=True,
            )
            row = json.loads((output / "fallback" / "sessions.jsonl").read_text())
            self.assertEqual(row["user_requests"], ["Research this company. clientSecret=[REDACTED_SECRET] [REDACTED_JWT]"])
            self.assertEqual(row["skills"], [])
            self.assertEqual(row["assistant_outcome"], "Report complete.")
            empty_tag = output / "empty-tag"
            empty_tag.mkdir()
            collision = subprocess.run(
                [sys.executable, str(SCRIPT), "--days", "30", "--end", "2026-08-19T00:00:00Z", "--sessions-dir", str(active), "--archived-dir", str(root / "missing"), "--output-root", str(output), "--run-tag", "empty-tag"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(collision.returncode, 0)
            self.assertIn("already exist", collision.stderr)


if __name__ == "__main__":
    unittest.main()
