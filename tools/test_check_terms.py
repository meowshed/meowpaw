# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the term check: living and shipped text calls the five stages stages (REQ-4200, TSK-5272)."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b"}


class Terms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import check_terms
        cls.tool = check_terms

    def tree(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True, env=ENV)
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=ENV)
        return root

    def run_check(self, root):
        out = io.StringIO()
        with redirect_stdout(out):
            status = self.tool.main(root)
        return status, out.getvalue().splitlines()

    def test_a_living_file_that_says_verbs_fails_naming_its_line(self):
        """TSK-5272 criterion 1, REQ-4200: the word in a specification is reported with its file and line."""
        root = self.tree({"project/specs/SPC-9999-a.md": "# A\n\nThe five verbs resolve from the profile.\n"})
        status, out = self.run_check(root)
        self.assertEqual(status, 1, out)
        self.assertEqual(out[0], "project/specs/SPC-9999-a.md:3: says verbs, where the text says stages")

    def test_a_frozen_record_that_says_verb_is_not_reported(self):
        """TSK-5272 criterion 2, REQ-4200: an approved record keeps the word it was written with."""
        root = self.tree({"project/adrs/ADR-9999-a.md": "A verb resolves.\n",
                          "project/requirements/REQ-9999-a.md": "A verb MUST resolve.\n"})
        status, out = self.run_check(root)
        self.assertEqual(status, 0, out)

    def test_an_allow_listed_file_is_not_reported(self):
        """TSK-5272 criterion 3, REQ-4200: the writing standard uses the grammatical term."""
        root = self.tree({"plugins/meow-prose/skills/writing/SKILL.md": "Turn the action back into a verb.\n"})
        status, out = self.run_check(root)
        self.assertEqual(status, 0, out)

    def test_a_line_naming_a_retired_unit_or_the_loop_argument_is_not_reported(self):
        """TSK-5272 criterion 3, REQ-4200: names that keep their spelling aren't the word."""
        root = self.tree({"docs/troubleshooting.md": "Uninstall `meow-verbs` first.\n\nPass `--until verbs=test`.\n"})
        status, out = self.run_check(root)
        self.assertEqual(status, 0, out)

    def test_this_repository_passes(self):
        """TSK-5272 criterion 4, REQ-4200: the tracked living and shipped files hold the word."""
        status, out = self.run_check(Path(__file__).resolve().parent.parent)
        self.assertEqual(status, 0, out)


if __name__ == "__main__":
    unittest.main()
