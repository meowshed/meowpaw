# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every failure path SPC-1040 states, and for ADR-1070's checks.

Each fixture builds a repository in a temporary directory and runs the
launcher there. `MEOW_VERBS_BIN` names the launcher to test, so the same
fixtures can first run against a program that returns nothing and be seen
failing (REQ-2072).
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_VERBS_BIN", UNIT / "bin" / "meow-verbs"))
VERBS = ["fmt", "lint", "typecheck", "test", "build"]


class Repository:
    """A scratch repository with an optional profile."""

    def __init__(self, profile=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")

    def run(self, *args, env=None):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True,
                              text=True, env=env)

    def status(self):
        done = self.run("status", "--json")
        return json.loads(done.stdout)

    def close(self):
        self.tmp.cleanup()


class Verbs(unittest.TestCase):
    def repo(self, profile=None):
        repository = Repository(profile)
        self.addCleanup(repository.close)
        return repository

    def test_no_profile_leaves_every_verb_unresolved(self):
        repo = self.repo()
        verbs = repo.status()["verbs"]
        self.assertEqual(sorted(verbs), sorted(VERBS))
        for entry in verbs.values():
            self.assertEqual((entry["state"], entry["kind"]), ("unresolved", "no profile"))

    def test_run_without_a_profile_runs_nothing_and_fails(self):
        done = self.repo().run("run", "lint")
        self.assertEqual(done.returncode, 3)
        self.assertIn("lint: unresolved (no profile", done.stdout)
        self.assertIn("not run", done.stdout)
        self.assertNotIn("passed", done.stdout)

    def test_an_unparseable_profile_resolves_nothing_and_runs_nothing(self):
        repo = self.repo('[verbs\nlint = "touch ran"\n')
        report = repo.status()
        self.assertEqual(report["profile_state"], "unparseable")
        self.assertTrue(report["error"])
        for entry in report["verbs"].values():
            self.assertEqual(entry["kind"], "profile unparseable")
        done = repo.run("run", "lint")
        self.assertEqual(done.returncode, 3)
        self.assertFalse((repo.root / "ran").exists())

    def test_a_value_that_is_not_one_command_is_malformed(self):
        report = self.repo('[verbs]\nlint = ["a", "b"]\ntest = ""\n').status()
        self.assertEqual(report["verbs"]["lint"]["kind"], "malformed declaration")
        self.assertEqual(report["verbs"]["test"]["kind"], "malformed declaration")
        self.assertEqual(report["verbs"]["fmt"]["kind"], "undeclared")

    def test_a_declared_verb_resolves_and_status_runs_nothing(self):
        repo = self.repo('[verbs]\nlint = "touch ran"\n')
        entry = repo.status()["verbs"]["lint"]
        self.assertEqual((entry["state"], entry["command"]), ("resolved", "touch ran"))
        self.assertEqual(entry["source"], ".meowpaw/profile.toml")
        repo.run("status")
        self.assertFalse((repo.root / "ran").exists())

    def test_an_unknown_key_is_reported_and_the_rest_still_resolve(self):
        report = self.repo('[verbs]\nlint = "true"\ndeploy = "true"\n[prose]\n'
                           'language = "en-US"\n').status()
        self.assertIn("verbs.deploy", report["ignored"])
        self.assertIn("[prose]", report["ignored"])
        self.assertEqual(report["verbs"]["lint"]["state"], "resolved")

    def test_a_failing_verb_reports_its_command_status_and_whole_output(self):
        lines = "; ".join(f"echo line{n}" for n in range(1, 31))
        repo = self.repo(f'[verbs]\nlint = "{lines}; echo boom >&2; exit 4"\n')
        done = repo.run("run", "lint")
        self.assertEqual(done.returncode, 1)
        self.assertIn(f"== lint: `{lines}; echo boom >&2; exit 4`", done.stdout)
        self.assertIn("failed, exit status 4", done.stdout)
        head, whole = done.stdout.split("-- whole output of lint:")
        self.assertIn("boom", head)
        self.assertNotIn("line1\n", head)
        self.assertIn("line1\n", whole)
        self.assertIn("line30\n", whole)
        self.assertIn("summary: lint failed", done.stdout)

    def test_a_command_the_shell_cannot_find_is_a_failure(self):
        done = self.repo('[verbs]\ntest = "no-such-tool-anywhere"\n').run("run", "test")
        self.assertEqual(done.returncode, 1)
        self.assertIn("failed, exit status 127", done.stdout)

    def test_a_passing_verb_passes_and_an_unresolved_one_never_does(self):
        done = self.repo('[verbs]\nfmt = "true"\n').run("run", "fmt", "build")
        self.assertEqual(done.returncode, 3)
        self.assertIn("summary: fmt passed, build unresolved", done.stdout)

    def test_run_with_no_verb_is_an_error_and_runs_nothing(self):
        repo = self.repo('[verbs]\nlint = "touch ran"\n')
        done = repo.run("run")
        self.assertEqual(done.returncode, 2)
        self.assertIn("name the verbs to run", done.stderr)
        self.assertFalse((repo.root / "ran").exists())

    def test_a_sixth_verb_is_refused(self):
        done = self.repo('[verbs]\ndeploy = "true"\n').run("run", "deploy")
        self.assertEqual(done.returncode, 2)
        self.assertIn("isn't a verb", done.stderr)

    def test_no_interpreter_leaves_every_verb_unresolved(self):
        repo = self.repo('[verbs]\nlint = "true"\n')
        fake = repo.root / "bin"
        fake.mkdir()
        old = fake / "python3"
        old.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        old.chmod(0o755)
        env = {"PATH": str(fake), "HOME": str(repo.root)}
        report = json.loads(repo.run("status", "--json", env=env).stdout)
        for entry in report["verbs"].values():
            self.assertEqual((entry["state"], entry["kind"]), ("unresolved", "no interpreter"))
        done = repo.run("run", "lint", env=env)
        self.assertEqual(done.returncode, 3)
        self.assertNotIn("passed", done.stdout)


if __name__ == "__main__":
    unittest.main()
