#!/usr/bin/env python3
"""discord-readability-gate tests (nominal/deep/boundary).

Run: python3 hooks/tests/test_discord_readability_gate.py
Deny contract = stdout JSON hookSpecificOutput.permissionDecision == "deny".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1]
GATE = HOOKS / "discord-readability-gate.py"


def run_hook(payload: dict, state_dir: str, args: list[str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["DISCORD_READABILITY_STATE_DIR"] = state_dir
    env["DISCORD_STATE_DIR"] = "/x/discord-testbot"
    return subprocess.run(
        [sys.executable, str(GATE)] + (args or []),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def denied(proc: subprocess.CompletedProcess) -> tuple[bool, str]:
    if not proc.stdout.strip():
        return False, ""
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, ""
    hso = out.get("hookSpecificOutput", {})
    return hso.get("permissionDecision") == "deny", hso.get("permissionDecisionReason", "")


class DiscordReadabilityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state_dir = tempfile.mkdtemp(prefix="rd-gate-")

    def payload(self, tool_name: str, text: str) -> dict:
        return {"tool_name": tool_name, "tool_input": {"chat_id": "1", "text": text}}

    def test_dense_denied(self) -> None:
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", "x" * 360), self.state_dir)
        is_denied, reason = denied(proc)
        self.assertTrue(is_denied, proc.stdout)
        self.assertIn("①", reason)

    def test_formatted_allowed(self) -> None:
        text = "Conclusion.\n\n1. one\n2. two\n3. three\n\nrefs: abc123\n— bot"
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", text), self.state_dir)
        is_denied, _ = denied(proc)
        self.assertFalse(is_denied, proc.stdout)

    def test_short_dense_allowed(self) -> None:
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", "x" * 340), self.state_dir)
        is_denied, _ = denied(proc)
        self.assertFalse(is_denied, proc.stdout)

    def test_dotlist_denied(self) -> None:
        text = "c.\n" + " · ".join(f"item {i} text" for i in range(30)) + "\nend"
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", text), self.state_dir)
        is_denied, reason = denied(proc)
        self.assertTrue(is_denied, proc.stdout)
        self.assertIn("②", reason)

    def test_long_paragraph_denied(self) -> None:
        text = "c.\n" + ("word " * 130) + "\nend"
        proc = run_hook(self.payload("mcp__plugin_discord_discord__edit_message", text), self.state_dir)
        is_denied, reason = denied(proc)
        self.assertTrue(is_denied, proc.stdout)
        self.assertIn("③", reason)

    def test_code_block_excluded(self) -> None:
        text = "c.\n```\n" + ("x" * 700) + "\n```\nend"
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", text), self.state_dir)
        is_denied, _ = denied(proc)
        self.assertFalse(is_denied, proc.stdout)

    def test_other_tool_allowed(self) -> None:
        proc = run_hook({"tool_name": "Bash", "tool_input": {"command": "x" * 400}}, self.state_dir)
        is_denied, _ = denied(proc)
        self.assertFalse(is_denied, proc.stdout)

    def test_allow_once_bypass(self) -> None:
        issue = run_hook({}, self.state_dir, args=["--allow-once", "table"])
        self.assertEqual(issue.returncode, 0, issue.stderr)
        proc = run_hook(self.payload("mcp__plugin_discord_discord__reply", "x" * 360), self.state_dir)
        is_denied, _ = denied(proc)
        self.assertFalse(is_denied, proc.stdout)
        log_path = os.path.join(self.state_dir, "log.jsonl")
        with open(log_path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(r.get("event") == "bypass" for r in rows), rows)


if __name__ == "__main__":
    unittest.main(verbosity=2)
