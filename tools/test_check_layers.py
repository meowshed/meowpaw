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
        # A `claude` that records a call, so a model call shows as a marker file.
        self.stub = Path(self.tmp.name) / "stub"
        self.stub.mkdir()
        self.called = Path(self.tmp.name) / "claude-was-called"
        (self.stub / "claude").write_text(f"#!/bin/sh\ntouch {self.called}\nexit 1\n")
        (self.stub / "claude").chmod(0o755)
        (self.path / ".meowpaw").mkdir()
        (self.path / ".meowpaw" / "profile.toml").write_text(PROFILE.format(signatures=signatures))
        (self.path / ".github").mkdir()
        (self.path / ".github" / "allowed_signers").write_text("")
        self.commit("chore: seed\n\nSigned-off-by: Person <person@example.org>\n", committer="Someone <someone@example.org>")

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
        merged = {**os.environ, "CHECK_LAYERS_REPOSITORY": str(ROOT)}
        merged.pop("MEOW_PROSE_GATE_JUDGE", None)
        merged["PATH"] = f"{self.stub}{os.pathsep}{merged['PATH']}"
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
        repository.commit("feat: a squash merge\n\nSigned-off-by: Person <person@example.org>\n", committer="GitHub <noreply@github.com>")
        good = repository.run("--baseline", baseline, "trunk")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        bad_sha = repository.commit("feat: a direct commit\n\nSigned-off-by: Person <person@example.org>\n")
        bad = repository.run("--baseline", baseline, "trunk")
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn(bad_sha[:8], bad.stdout)
        self.assertIn("trunk", bad.stdout)

    def test_a_branch_commit_whose_message_breaks_the_convention_fails(self):
        """BUG-1561, REQ-2712: each commit the branch adds meets `meow-scm check-message`."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        repository.commit("feat: a good one\n\nSigned-off-by: Person <person@example.org>\n")
        self.assertEqual(repository.run("--base", "main", "commits").returncode, 0)
        sha = repository.commit("Did some things\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)

    def test_an_unsigned_branch_commit_fails_where_signatures_are_required(self):
        """BUG-1561, REQ-2712: a signature that doesn't verify against `.github/allowed_signers`."""
        repository = self.repo(signatures="true")
        repository.git("checkout", "-q", "-b", "feat/x")
        sha = repository.commit("feat: unsigned\n\nSigned-off-by: Person <person@example.org>\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)
        self.assertIn("signature", done.stdout)

    def test_a_branch_commit_that_breaks_a_prose_rule_fails(self):
        """BUG-1564, REQ-2712: the exact rules of the prose gate over each message, with no model call."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        sha = repository.commit("feat: leverage a silver bullet to delve into robust synergy\n\nSigned-off-by: Person <person@example.org>\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(sha[:8], done.stdout)

    def test_the_prose_rule_that_failed_is_named_and_no_model_is_called(self):
        """BUG-1564, REQ-2712: the finding names the gate's rule, and the judge's `claude` is never run."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        repository.commit("feat: leverage a silver bullet to delve into robust synergy\n\nSigned-off-by: Person <person@example.org>\n")
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertRegex(done.stdout, r"\b(J\d|P\d)\b")
        self.assertFalse(repository.called.exists(), "the prose gate called a model")

    def test_a_good_signature_passes_where_signatures_are_required(self):
        """BUG-1561: a commit signed by a key in `.github/allowed_signers` is good."""
        repository = self.repo(signatures="true")
        key = Path(repository.tmp.name) / "key"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        signers = repository.path / ".github" / "allowed_signers"
        signers.write_text(f"person@example.org {(key.with_suffix('.pub')).read_text()}")
        repository.git("add", "-A")
        repository.git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "chore: signers\n\nSigned-off-by: Person <person@example.org>\n",
                       env={"GIT_AUTHOR_NAME": "Person", "GIT_AUTHOR_EMAIL": "person@example.org",
                            "GIT_COMMITTER_NAME": "Person", "GIT_COMMITTER_EMAIL": "person@example.org"})
        repository.git("checkout", "-q", "-b", "feat/x")
        (repository.path / "x.txt").write_text("x")
        repository.git("add", "-A")
        repository.git("-c", "gpg.format=ssh", "-c", f"user.signingkey={key}", "commit", "-q", "-S", "-m",
                       "feat: signed\n\nSigned-off-by: Person <person@example.org>\n",
                       env={"GIT_AUTHOR_NAME": "Person", "GIT_AUTHOR_EMAIL": "person@example.org",
                            "GIT_COMMITTER_NAME": "Person", "GIT_COMMITTER_EMAIL": "person@example.org"})
        done = repository.run("--base", "main", "commits")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_all_takes_the_trunk_on_main_and_the_branch_commits_elsewhere(self):
        """The path CI runs: a branch checks the commits it adds, and a detached head is a branch."""
        repository = self.repo()
        baseline = repository.git("rev-parse", "HEAD").stdout.strip()
        repository.commit("feat: a direct commit\n\nSigned-off-by: Person <person@example.org>\n")
        on_trunk = repository.run("--baseline", baseline, "all")
        self.assertEqual(on_trunk.returncode, 1, on_trunk.stdout + on_trunk.stderr)
        self.assertIn("trunk:", on_trunk.stdout)
        repository.git("checkout", "-q", "--detach")
        detached = repository.run("--base", "main", "--baseline", baseline, "all")
        self.assertIn("commits:", detached.stdout)
        self.assertNotIn("trunk:", detached.stdout)

    def test_a_baseline_the_history_lacks_is_unresolved_and_not_a_pass(self):
        """A shallow clone fails closed: exit 3, not 0."""
        repository = self.repo()
        done = repository.run("--baseline", "0" * 40, "trunk")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved", done.stdout)

    def test_a_merge_commit_is_not_a_finding(self):
        """The merge a pull request's checkout makes is no commit of the branch."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        repository.commit("feat: a good one\n\nSigned-off-by: Person <person@example.org>\n")
        repository.git("checkout", "-q", "main")
        repository.git("merge", "-q", "--no-ff", "-m", "Merge branch feat/x", "feat/x",
                       env={"GIT_AUTHOR_NAME": "GitHub", "GIT_AUTHOR_EMAIL": "noreply@github.com",
                            "GIT_COMMITTER_NAME": "GitHub", "GIT_COMMITTER_EMAIL": "noreply@github.com"})
        done = repository.run("--base", "HEAD~1", "commits")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_a_launcher_with_no_binary_is_unresolved_for_each_commit(self):
        """A denial of the launcher is not a finding against the commit."""
        repository = self.repo()
        repository.git("checkout", "-q", "-b", "feat/x")
        repository.commit("feat: a good one\n\nSigned-off-by: Person <person@example.org>\n")
        empty = Path(repository.tmp.name) / "none"
        empty.mkdir()
        shutil.copytree(ROOT / "plugins", empty / "plugins", ignore=shutil.ignore_patterns("tests", "evals"))
        for target in (empty / "plugins").glob("*/bin/*-*"):
            if target.is_dir():
                shutil.rmtree(target)
        done = repository.run("--base", "main", "commits",
                              env={"CHECK_LAYERS_REPOSITORY": str(empty), "CLAUDE_PLUGIN_DATA": str(empty / "d" / "u")})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
