# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The `SessionStart` hook puts a pending gate in front of the model (TSK-4915, SPC-1240 "A pending gate").

The test reads the hook's command from `hooks.json` and runs it against a fixture record, so a change to the
declaration breaks it.
"""

import json
import subprocess
import unittest
from pathlib import Path

from test_record import Repository

UNIT = Path(__file__).resolve().parent.parent


def session_start_command():
    hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    commands = [h["command"] for group in hooks["SessionStart"] for h in group["hooks"]]
    assert len(commands) == 1, commands
    return commands[0].replace("${CLAUDE_PLUGIN_ROOT}", str(UNIT))


class SessionStart(unittest.TestCase):
    def run_hook(self, repository):
        return subprocess.run(session_start_command(), shell=True, cwd=repository.path, capture_output=True, text=True)

    def test_a_pending_gate_reaches_the_model_through_the_hooks_output(self):
        """TSK-4915 criterion 1, REQ-2730: the output names the decision and the gate it waits at."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = self.run_hook(repository)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ADR-0001 decision, at the design gate", done.stdout)

    def test_nothing_waiting_prints_nothing(self):
        """TSK-4915 criterion 2, REQ-2730: silence and exit 0."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = self.run_hook(repository)
        self.assertEqual((done.returncode, done.stdout), (0, ""), done.stderr)


if __name__ == "__main__":
    unittest.main()
