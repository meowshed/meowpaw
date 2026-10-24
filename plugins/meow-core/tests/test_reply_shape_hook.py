# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The core unit's session start hands the model the reply shape (TSK-5690, ADR-3050, REQ-0930, REQ-0932)."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
SCRIPT = UNIT / "hooks" / "reply-shape"
STYLE = UNIT / "output-styles" / "meow.md"
ROLE = re.compile(r"<role>\n.*?</role>", re.S)
RULES = re.compile(r'<rules name="the reply shape">\n.*?</rules>', re.S)


def blocks(text):
    return ROLE.search(text).group(0) + "\n\n" + RULES.search(text).group(0)


class ReplyShapeHook(unittest.TestCase):
    def run_hook(self, root):
        return subprocess.run([str(SCRIPT)], capture_output=True, text=True,
                              env={"PATH": os.environ["PATH"], "CLAUDE_PLUGIN_ROOT": str(root)})

    def unit_with_style(self, text):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        (Path(root) / "output-styles").mkdir()
        (Path(root) / "output-styles" / "meow.md").write_text(text, encoding="utf-8")
        return root

    def test_the_hook_prints_the_styles_role_and_rules_as_additional_context(self):
        """TSK-5690 criterion 1, REQ-0930, REQ-0932: one JSON object carries both blocks, byte for byte."""
        done = self.run_hook(UNIT)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual(out["hookEventName"], "SessionStart")
        self.assertEqual(out["additionalContext"], blocks(STYLE.read_text(encoding="utf-8")))
        for rule in range(1, 12):
            self.assertIn(f"- R{rule}. ", out["additionalContext"])

    def test_quotes_backslashes_and_tabs_survive_the_encoding(self):
        """TSK-5690 criterion 2, REQ-0930: the JSON parses and the text comes back unchanged."""
        text = ('---\nname: x\n---\n\n<role>\nSay "this" and C:\\dir\\file\tthen stop.\n</role>\n\n'
                '<rules name="the reply shape">\n- R1. A \\n is not a newline, and a "quote" is not a string end.\n</rules>\n')
        done = self.run_hook(self.unit_with_style(text))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"], blocks(text))

    def test_a_missing_style_file_prints_nothing_and_exits_zero(self):
        """TSK-5690 criterion 3, REQ-0930: the hook abstains where it has nothing to print."""
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        done = self.run_hook(root)
        self.assertEqual((done.returncode, done.stdout), (0, ""), done.stderr)

    def test_a_style_without_a_rules_block_prints_nothing_and_exits_zero(self):
        """TSK-5690 criterion 3, REQ-0930: a style that carries no rules block gives the model nothing to hold."""
        done = self.run_hook(self.unit_with_style("---\nname: x\n---\n\n<role>\nOnly a role.\n</role>\n"))
        self.assertEqual((done.returncode, done.stdout), (0, ""), done.stderr)

    def test_an_unset_plugin_root_prints_nothing_and_exits_zero(self):
        """TSK-5690 criterion 3, REQ-0930: with no root the hook never fails the session."""
        done = subprocess.run([str(SCRIPT)], capture_output=True, text=True, env={"PATH": os.environ["PATH"]})
        self.assertEqual((done.returncode, done.stdout), (0, ""), done.stderr)

    def test_the_manifest_of_hooks_runs_it_beside_write_root(self):
        """TSK-5690 criterion 4, REQ-0932: `SessionStart` lists both hooks."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text())["hooks"]
        commands = [h["command"] for entry in hooks["SessionStart"] for h in entry["hooks"]]
        self.assertTrue(any("write-root" in c for c in commands), commands)
        self.assertTrue(any("reply-shape" in c for c in commands), commands)


if __name__ == "__main__":
    unittest.main()
