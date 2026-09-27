# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The stub under the old name tells a session where the unit went (ADR-1390)."""
import json
import os
import subprocess
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
NOTICE = Path(os.environ.get("MEOW_METHOD_NOTICE", UNIT / "hooks" / "notice"))


class Stub(unittest.TestCase):
    def test_the_notice_says_where_the_unit_went(self):
        """REQ-3004: the rename is announced by a release under the old name."""
        done = subprocess.run([str(NOTICE)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("meow-method is now meow-flow", done.stdout)
        self.assertIn("claude plugin install meow-flow@meowpaw", done.stdout)
        self.assertIn("claude plugin uninstall meow-method@meowpaw", done.stdout)
        self.assertIn("The release after meow-flow 0.31.0 removes this stub", done.stdout)

    def test_the_session_start_hook_runs_the_notice(self):
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        commands = [hook["command"] for entry in hooks["hooks"]["SessionStart"] for hook in entry["hooks"]]
        self.assertEqual(commands, ['"${CLAUDE_PLUGIN_ROOT}"/hooks/notice'])

    def test_the_stub_ships_no_skill_and_no_program(self):
        self.assertFalse((UNIT / "skills").exists())
        self.assertFalse((UNIT / "bin").exists())


if __name__ == "__main__":
    unittest.main()
