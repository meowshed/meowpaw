# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""No task the gate runs skips silently when its tool is missing (TSK-4925 criterion 5, REQ-1426).

A shell command that names a missing tool exits 127 and says its name. A task skips silently only where it
goes on past that: `|| true`, `|| :`, `|| echo`, `; true`, a `command -v`, `hash`, `which` or `test -x` guard that
falls through, or a `-` prefix that ignores the exit status. The check reads `mise.toml` and runs nothing.
"""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SWALLOW = [
    (re.compile(r"\|\|\s*(?:true\b|:(?:\s|$)|exit\s+0\b|echo\b)"), "ends with `|| true` or another way of going on"),
    (re.compile(r";\s*(?:true|exit\s+0)\s*$"), "ends with `; true`"),
    (re.compile(r"\bcommand\s+-v\b|\bhash\s+\w+|\btype\s+-p\b|\bwhich\s+\w+|\btest\s+-x\b|\[\s+-x\b"),
     "tests whether a tool exists and may skip"),
    (re.compile(r"2>\s*/dev/null\s*\|\|"), "hides a failure and falls through"),
    (re.compile(r"^\s*-\s*\w"), "has a `-` prefix that ignores the exit status"),
]


def gate_tasks():
    mise = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))["tasks"]
    return {name: task for name, task in mise.items() if "run" in task}


def swallowed(command):
    return [why for pattern, why in SWALLOW if pattern.search(command)]


class GateTasks(unittest.TestCase):
    def test_a_command_that_swallows_a_missing_tool_is_found(self):
        """TSK-4925 criterion 5: the check can fail."""
        self.assertEqual(swallowed("prettier --check . || true"), ["ends with `|| true` or another way of going on"])
        self.assertTrue(swallowed("lychee . || :"))
        self.assertTrue(swallowed("lychee . || echo skipped"))
        self.assertTrue(swallowed("hash lychee && lychee ."))
        self.assertTrue(swallowed("- lychee ."))
        self.assertTrue(swallowed("command -v lychee && lychee ."))
        self.assertEqual(swallowed("prettier --check ."), [])

    def test_no_gate_task_swallows_a_missing_tool(self):
        found = {}
        tasks = gate_tasks()
        self.assertGreater(len(tasks), 10, "the check read no gate task")
        for name, task in tasks.items():
            run = task["run"]
            for line in (run if isinstance(run, list) else str(run).splitlines()):
                reasons = swallowed(line)
                if reasons:
                    found[name] = reasons
        self.assertEqual(found, {}, "a gate task skips silently where its tool is missing")


if __name__ == "__main__":
    unittest.main()
