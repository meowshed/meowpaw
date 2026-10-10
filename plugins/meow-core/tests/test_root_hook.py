# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The core unit's session start writes where it is installed (TSK-5300, REQ-4504)."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
SCRIPT = UNIT / "hooks" / "write-root"


class RootHook(unittest.TestCase):
    def run_hook(self, **env):
        return subprocess.run([str(SCRIPT)], capture_output=True, text=True,
                              env={"PATH": os.environ["PATH"], **env})

    def test_the_hook_writes_the_installed_root_to_the_data_directory(self):
        """TSK-5300 criterion 2, REQ-4504: `meow-root` in the data directory holds the root, and the hook exits 0."""
        with tempfile.TemporaryDirectory() as data:
            done = self.run_hook(CLAUDE_PLUGIN_ROOT="/installed/meow-core/1.0.0", CLAUDE_PLUGIN_DATA=data)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual((Path(data) / "meow-root").read_text().strip(), "/installed/meow-core/1.0.0")

    def test_the_hook_replaces_a_root_that_an_update_moved(self):
        """TSK-5300 criterion 2, REQ-4504: a later version overwrites the earlier path."""
        with tempfile.TemporaryDirectory() as data:
            self.run_hook(CLAUDE_PLUGIN_ROOT="/installed/meow-core/1.0.0", CLAUDE_PLUGIN_DATA=data)
            self.run_hook(CLAUDE_PLUGIN_ROOT="/installed/meow-core/1.1.0", CLAUDE_PLUGIN_DATA=data)
            self.assertEqual((Path(data) / "meow-root").read_text().strip(), "/installed/meow-core/1.1.0")

    def test_the_hook_never_fails_a_session_without_a_data_directory(self):
        """TSK-5300 criterion 2, REQ-4504: with no data variable the hook writes nothing and exits 0."""
        done = self.run_hook(CLAUDE_PLUGIN_ROOT="/installed/meow-core/1.0.0")
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_the_manifest_of_hooks_runs_it_at_session_start(self):
        """TSK-5300 criterion 2, REQ-4504: `hooks/hooks.json` names the script under SessionStart."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text())["hooks"]
        commands = [h["command"] for entry in hooks["SessionStart"] for h in entry["hooks"]]
        self.assertTrue(any("write-root" in command for command in commands), commands)


if __name__ == "__main__":
    unittest.main()
