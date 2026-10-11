# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""No task the gate runs skips silently when its tool is missing (TSK-4925 criterion 5, REQ-1426).

A shell command that names a missing tool exits 127 and says its name. A task skips silently only where it
swallows that: `|| true`, `; true`, a `command -v` guard that falls through, or a `-` prefix that ignores the exit.
"""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SWALLOW = [
    (re.compile(r"\|\|\s*(true|:|exit\s+0)\b"), "ends with `|| true`"),
    (re.compile(r";\s*(true|exit\s+0)\s*$"), "ends with `; true`"),
    (re.compile(r"\bcommand\s+-v\b|\bwhich\s+\w+\s*(&&|\|\|)|\btype\s+-p\b"), "tests whether a tool exists and skips"),
    (re.compile(r"2>\s*/dev/null\s*\|\|"), "hides a failure and falls through"),
]


def gate_tasks():
    mise = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))["tasks"]
    return {name: task for name, task in mise.items() if "run" in task}


def swallowed(command):
    return [why for pattern, why in SWALLOW if pattern.search(command)]


class GateTasks(unittest.TestCase):
    def test_a_command_that_swallows_a_missing_tool_is_found(self):
        """TSK-4925 criterion 5: the check can fail."""
        self.assertEqual(swallowed("prettier --check . || true"), ["ends with `|| true`"])
        self.assertTrue(swallowed("command -v lychee && lychee ."))
        self.assertEqual(swallowed("prettier --check ."), [])

    def test_no_gate_task_swallows_a_missing_tool(self):
        found = {}
        for name, task in gate_tasks().items():
            for line in str(task["run"]).splitlines():
                reasons = swallowed(line)
                if reasons:
                    found[name] = reasons
        self.assertEqual(found, {}, "a gate task skips silently where its tool is missing")


if __name__ == "__main__":
    unittest.main()
