# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1050 states, and ADR-1080's checks.

Each fixture builds a repository in a temporary directory and runs the launcher
there. `MEOW_SCM_BIN` names the launcher to test, so the same fixtures can
first run against a program that returns nothing and be seen failing
(REQ-2072).
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_SCM_BIN", UNIT / "bin" / "meow-scm"))

CONVENTION = """[commits]
subject_limit = 72
trailers = ["Signed-off-by"]

[commits.types]
feat = "minor"
fix = "patch"
spec = "none"
"""
SIGNED = "Signed-off-by: A Person <a@example.org>"
GOOD = f"fix: read a link whose target sits in angle brackets\n\nThe check cut a target at its first parenthesis.\n\n{SIGNED}\n"
# Built from parts, so this file itself carries no attribution a search would find.
CO_AUTHOR = "Co-Authored-" + "By: Claude <noreply@" + "anthropic.com>"
FOOTER = "Generated " + "with [Claude Code](https://claude.com)"


class Repository:
    def __init__(self, profile=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")

    def check(self, message, env=None):
        return subprocess.run([str(BIN), "check-message"], cwd=self.root, input=message,
                              capture_output=True, text=True, env=env)

    def run(self, *args, env=None):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True,
                              text=True, env=env)


class Convention(unittest.TestCase):
    def repo(self, profile=CONVENTION):
        repository = Repository(profile)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_message_in_the_convention_passes(self):
        done = self.repo().check(GOOD)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_each_break_is_named(self):
        message = ("chore: " + "x" * 70 + ".\nno blank line here\n")
        done = self.repo().check(message)
        self.assertEqual(done.returncode, 1)
        for rule in ("declared type", "subject length", "subject ending", "blank line", "trailer"):
            self.assertIn(rule, done.stdout)

    def test_a_subject_not_in_the_form_is_named(self):
        done = self.repo().check(f"Fixed the thing\n\n{SIGNED}\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("line 1: subject form", done.stdout)

    def test_a_scope_and_a_breaking_marker_are_accepted(self):
        done = self.repo().check(f"feat(verbs)!: drop the old table\n\n{SIGNED}\n")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_attribution_fails_with_a_convention(self):
        for line in (CO_AUTHOR, FOOTER):
            done = self.repo().check(f"fix: a change\n\n{SIGNED}\n{line}\n")
            self.assertEqual(done.returncode, 1)
            self.assertIn("attribution", done.stdout)

    def test_attribution_fails_without_a_convention(self):
        done = self.repo(profile=None).check(f"anything at all\n\n{CO_AUTHOR}\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("attribution", done.stdout)

    def test_a_path_or_a_product_name_is_not_attribution(self):
        message = f"fix: route the reply shape in plugins/meow-core/ for Claude Code\n\n{SIGNED}\n"
        done = self.repo().check(message)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_no_commits_table_leaves_the_convention_undeclared(self):
        done = self.repo(profile='[verbs]\ntest = "true"\n').check("Whatever I like\n")
        self.assertEqual(done.returncode, 3)
        self.assertIn("convention undeclared", done.stdout)
        self.assertNotIn("meets the declared convention", done.stdout)

    def test_no_profile_leaves_the_convention_undeclared(self):
        done = self.repo(profile=None).check(GOOD)
        self.assertEqual(done.returncode, 3)
        self.assertIn("undeclared", done.stdout)

    def test_an_unparseable_profile_checks_no_convention(self):
        done = self.repo(profile="[commits\n").check(GOOD)
        self.assertEqual(done.returncode, 3)
        self.assertIn("convention unparseable", done.stdout)

    def test_a_malformed_types_table_is_reported(self):
        profile = '[commits]\ntrailers = []\n[commits.types]\nfeat = "big"\n'
        done = self.repo(profile=profile).run("convention")
        self.assertIn("malformed", done.stdout)
        self.assertIn("feat", done.stdout)

    def test_an_empty_message_fails(self):
        done = self.repo().check("\n# a comment only\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("empty message", done.stdout)

    def test_convention_reports_what_is_declared(self):
        done = self.repo().run("convention")
        self.assertEqual(done.returncode, 0)
        self.assertIn("release: minor", done.stdout)
        self.assertIn("72 characters", done.stdout)
        self.assertIn("Signed-off-by", done.stdout)

    def test_no_interpreter_leaves_the_message_unchecked(self):
        repo = self.repo()
        fake = repo.root / "bin"
        fake.mkdir()
        old = fake / "python3"
        old.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        old.chmod(0o755)
        done = repo.check(GOOD, env={"PATH": str(fake), "HOME": str(repo.root)})
        self.assertEqual(done.returncode, 3)
        self.assertIn("unchecked", done.stdout)
        self.assertNotIn("meets", done.stdout)


if __name__ == "__main__":
    unittest.main()
