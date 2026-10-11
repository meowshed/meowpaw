# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The hooks `meow-checks` ships advance the revision counter (TSK-4910, SPC-1240 "The revision counter")."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
TOOLS = "Bash|Edit|Write|NotebookEdit"


class Hooks(unittest.TestCase):
    def test_both_events_run_revision_on_the_four_tools(self):
        """TSK-4910 criterion 2, REQ-2728: PostToolUse and PostToolUseFailure, each on Bash, Edit, Write and
        NotebookEdit, run the `revision` subcommand of the launcher."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(sorted(hooks), ["PostToolUse", "PostToolUseFailure"])
        for event, groups in hooks.items():
            self.assertEqual(len(groups), 1, event)
            group = groups[0]
            self.assertEqual(sorted(group["matcher"].split("|")), sorted(TOOLS.split("|")), event)
            commands = [h["command"] for h in group["hooks"]]
            self.assertEqual(commands, ['"${CLAUDE_PLUGIN_ROOT}"/bin/meow-checks revision'], event)


class Launcher(unittest.TestCase):
    def test_with_no_binary_it_says_so_and_exits_zero(self):
        """SPC-1240 "A hook whose program is missing": a PostToolUse hook can't stop a call that already ran."""
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-checks"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-checks").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            env = {"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}
            done = subprocess.run(["sh", str(launcher), "revision"], cwd=tmp, env=env,
                                  capture_output=True, text=True, input="{}")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("revision", done.stdout)
            self.assertIn("install meow-core", done.stdout)


if __name__ == "__main__":
    unittest.main()
