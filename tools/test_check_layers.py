# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The gate checks that hold what the hooks stop (SPC-1240 "How a rule is layered", REQ-2712).

Each fixture is a repository in a temporary directory, with the unit launchers of this repository's own `plugins/`
and a profile of its own, and `tools/check_layers.py` runs in it.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "check_layers.py"

PROFILE = """[git]
trunk = "main"
require_signatures = {signatures}

[commits]
subject_limit = 72
trailers = ["Signed-off-by"]

[commits.types]
feat = "minor"
fix = "patch"
chore = "none"
"""


class Repository:
    def __init__(self, signatures="false"):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "repository"
        self.path.mkdir()
        self.git("init", "-q", "--template=", "-b", "main")
        (self.path / ".meowpaw").mkdir()
        (self.path / ".meowpaw" / "profile.toml").write_text(PROFILE.format(signatures=signatures))
        (self.path / ".github").mkdir()
        (self.path / ".github" / "allowed_signers").write_text("")
        self.commit("chore: seed\n\nSigned-off-by: A <a@b>\n", committer="Someone <someone@example.org>")

    def git(self, *args, env=None):
        base = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
        base.update(env or {})
        return subprocess.run(["git", *args], cwd=self.path, env=base, capture_output=True, text=True, check=True)

    def commit(self, message, committer="Person <person@example.org>", files=None):
        for name, text in (files or {}).items():
            target = self.path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        (self.path / "note.txt").write_text(message + str(len(list(self.path.iterdir()))))
        self.git("add", "-A")
        name, email = committer.rstrip(">").split(" <")
        env = {"GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email, "GIT_AUTHOR_NAME": "Person",
               "GIT_AUTHOR_EMAIL": "person@example.org"}
        self.git("-c", "commit.gpgsign=false", "commit", "-q", "-m", message, env=env)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def run(self, *args, env=None):
        merged = {**os.environ, "CHECK_LAYERS_REPOSITORY": str(ROOT), "MEOW_PROSE_GATE_JUDGE": "/nonexistent"}
        merged.update(env or {})
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.path), *args], cwd=self.path,
                              env=merged, capture_output=True, text=True)


class Layers(unittest.TestCase):
    def repo(self, **kwargs):
        repository = Repository(**kwargs)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_commit_on_the_trunk_that_github_did_not_make_fails(self):
        """BUG-1560, REQ-2712: after the baseline, each commit on the trunk's own line is a merge GitHub made."""
        repository = self.repo()
        baseline = repository.git("rev-parse", "HEAD").stdout.strip()
        repository.commit("feat: a squash merge\n\nSigned-off-by: A <a@b>\n", committer="GitHub <noreply@github.com>")
        good = repository.run("--baseline", baseline, "trunk")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        bad_sha = repository.commit("feat: a direct commit\n\nSigned-off-by: A <a@b>\n")
        bad = repository.run("--baseline", baseline, "trunk")
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn(bad_sha[:8], bad.stdout)
        self.assertIn("trunk", bad.stdout)

    def test_a_branch_commit_whose_message_breaks_the_convention_fails(self):
        """BUG-1561, REQ-2712: each commit the branch adds meets `meow-scm check-message`."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        repository.commit("feat: a good one\n\nSigned-off-by: A <a@b>\n")
        self.assertEqual(repository.run("--base", "main", "commits").returncode, 0)
        sha = repository.commit("Did some things\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)

    def test_an_unsigned_branch_commit_fails_where_signatures_are_required(self):
        """BUG-1561, REQ-2712: a signature that doesn't verify against `.github/allowed_signers`."""
        repository = self.repo(signatures="true")
        repository.git("checkout", "-q", "-b", "feat/x")
        sha = repository.commit("feat: unsigned\n\nSigned-off-by: A <a@b>\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)
        self.assertIn("signature", done.stdout)

    def test_a_branch_commit_that_breaks_a_prose_rule_fails(self):
        """BUG-1564, REQ-2712: the exact rules of the prose gate over each message, with no model call."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        sha = repository.commit("feat: leverage a silver bullet to delve into robust synergy\n\nSigned-off-by: A <a@b>\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)

    def test_a_tracked_run_state_file_fails(self):
        """BUG-1563, REQ-2712: a run's own state lives outside the repository."""
        repository = self.repo()
        self.assertEqual(repository.run("run-state").returncode, 0)
        repository.commit("chore: oops\n\nSigned-off-by: A <a@b>\n", files={"runs/abc/run.toml": "x = 1\n"})
        done = repository.run("run-state")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("runs/abc/run.toml", done.stdout)

    def test_this_repository_passes_its_own_run_state_check(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "--root", str(ROOT), "run-state"], capture_output=True,
                              text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
