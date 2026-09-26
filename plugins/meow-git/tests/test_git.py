# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every failure path SPC-1060 states, and ADR-1090's checks.

Each fixture builds a scratch repository with a bare remote, so the push guard
has published commits to compare against, and runs a guard with the hook's
input on standard input. `MEOW_GIT_BIN` names the launcher to test, so the same
fixtures can first run against a program that returns nothing and be seen
failing (REQ-2072). The signature cases sign with throwaway keys.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_GIT_BIN", UNIT / "bin" / "meow-git"))
SCM = UNIT.parent / "meow-scm" / "bin" / "meow-scm"
SIGNED_OFF = "Signed-off-by: A Person <a@example.org>"
CONVENTION = '[commits]\nsubject_limit = 72\ntrailers = ["Signed-off-by"]\n[commits.types]\nfix = "patch"\n'


def run(cwd, *args, **kwargs):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=True, **kwargs)


class Repository:
    def __init__(self, profile=None):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.keys = base / "keys"
        self.keys.mkdir()
        run(base, "git", "init", "-q", "--bare", "-b", "main", "origin.git")
        self.root = base / "work"
        run(base, "git", "clone", "-q", str(base / "origin.git"), "work")
        for key, value in (("user.name", "A Person"), ("user.email", "a@example.org"),
                           ("commit.gpgsign", "false"), ("gpg.format", "ssh")):
            run(self.root, "git", "config", key, value)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")
        self.commit(f"fix: start\n\n{SIGNED_OFF}")
        run(self.root, "git", "push", "-q", "-u", "origin", "HEAD:main")
        run(self.root, "git", "checkout", "-q", "-b", "work")

    def commit(self, message, sign_with=None):
        args = ["git", "commit", "-q", "--allow-empty", "-m", message]
        if sign_with:
            args = ["git", "-c", f"user.signingkey={sign_with}", "commit", "-q", "-S",
                    "--allow-empty", "-m", message]
        run(self.root, *args)

    def key(self, name, trusted):
        path = self.keys / name
        run(self.keys, "ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(path))
        if trusted:
            with open(self.keys / "allowed", "a", encoding="utf-8") as allowed:
                allowed.write(f"a@example.org {path.with_suffix('.pub').read_text()}")
        return path

    def trust(self):
        run(self.root, "git", "config", "gpg.ssh.allowedSignersFile", str(self.keys / "allowed"))

    def guard(self, name, scm=SCM, env=None, command=None):
        environment = {**os.environ, "MEOW_SCM": str(scm)} if env is None else env
        event = {"cwd": str(self.root)}
        if command is not None:
            event["tool_input"] = {"command": command}
        return subprocess.run([str(BIN), name], input=json.dumps(event),
                              capture_output=True, text=True, env=environment)


@unittest.skipUnless(shutil.which("ssh-keygen"), "the signature cases need ssh-keygen")
class GitPack(unittest.TestCase):
    def repo(self, profile='[git]\ntrunk = "main"\n' + CONVENTION):
        repository = Repository(profile)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_commit_on_the_trunk_is_refused(self):
        repo = self.repo()
        run(repo.root, "git", "checkout", "-q", "main")
        done = repo.guard("commit-guard")
        self.assertEqual(done.returncode, 2)
        self.assertIn("refused a commit on `main`", done.stderr)

    def test_a_command_that_does_not_commit_runs_on_the_trunk(self):
        # Claude Code runs the hook whenever it can't parse the command, so the
        # guard reads the command itself.
        repo = self.repo()
        run(repo.root, "git", "checkout", "-q", "main")
        for command in ('echo "$(git log --oneline -1)"', "git status && ls $HOME", "gh pr list | tr a b"):
            done = repo.guard("commit-guard", command=command)
            self.assertEqual(done.returncode, 0, command + done.stderr)
            self.assertEqual(done.stderr, "", command)
            self.assertIn("doesn't commit", done.stdout, command)

    def test_every_form_of_a_commit_is_refused_on_the_trunk(self):
        repo = self.repo()
        run(repo.root, "git", "checkout", "-q", "main")
        for command in ("git commit -m x", "cd a && git commit -am x", "git -C /tmp/r commit -m x",
                        'x=$(git commit -m "y")', "git -c user.name=a commit"):
            done = repo.guard("commit-guard", command=command)
            self.assertEqual(done.returncode, 2, command)
            self.assertIn("refused a commit on `main`", done.stderr, command)

    def test_a_commit_in_another_directory_is_judged_there(self):
        # The session sits on the trunk; the command commits in a worktree on a branch.
        repo = self.repo()
        other = repo.root.parent / "elsewhere"
        run(repo.root, "git", "checkout", "-q", "main")
        run(repo.root, "git", "worktree", "add", "-q", str(other), "work")
        # A real repository commits its profile; the fixture's is only on disk.
        (other / ".meowpaw").mkdir(exist_ok=True)
        (other / ".meowpaw" / "profile.toml").write_text(
            (repo.root / ".meowpaw" / "profile.toml").read_text(encoding="utf-8"), encoding="utf-8")
        for command in (f"cd {other} && git commit -m x", f"git -C {other} commit -m x"):
            done = repo.guard("commit-guard", command=command)
            self.assertEqual(done.returncode, 0, command + done.stderr)
            self.assertIn("`work` isn't the trunk `main`", done.stdout, command)

    def test_a_command_that_does_not_push_checks_nothing(self):
        repo = self.repo()
        repo.commit("not a conventional subject")
        done = repo.guard("push-guard", command='echo "$(git log -1)"')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("doesn't push", done.stdout)

    def test_a_commit_on_a_branch_runs(self):
        done = self.repo().guard("commit-guard")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(done.stderr, "")
        self.assertIn("`work` isn't the trunk `main`", done.stdout)

    def test_a_push_with_a_failing_message_is_refused(self):
        repo = self.repo()
        repo.commit(f"fix: {'x' * 80}\n\n{SIGNED_OFF}")
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 2)
        self.assertIn("refused the push", done.stderr)
        self.assertIn("subject length", done.stderr)

    def test_a_push_of_good_commits_goes_through(self):
        repo = self.repo()
        repo.commit(f"fix: read the trunk from the profile\n\n{SIGNED_OFF}")
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("1 commit checked", done.stdout)

    def test_without_meow_scm_the_message_check_is_unrun(self):
        repo = self.repo()
        repo.commit("anything at all")
        done = repo.guard("push-guard", scm="/nowhere/meow-scm")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("message check is unrun", done.stdout)

    def test_signatures_required_refuses_an_unsigned_commit(self):
        repo = self.repo('[git]\ntrunk = "main"\nrequire_signatures = true\n')
        repo.commit("fix: unsigned")
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 2)
        self.assertIn("is unsigned", done.stderr)

    def test_a_signature_nobody_can_verify_is_unverifiable(self):
        repo = self.repo('[git]\ntrunk = "main"\nrequire_signatures = true\n')
        repo.commit("fix: signed", sign_with=repo.key("orphan", trusted=False))
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 2)
        self.assertIn("unverifiable", done.stderr)
        self.assertNotIn("is unsigned", done.stderr)

    def test_an_untrusted_key_is_refused(self):
        repo = self.repo('[git]\ntrunk = "main"\nrequire_signatures = true\n')
        repo.key("trusted", trusted=True)
        repo.trust()
        repo.commit("fix: signed", sign_with=repo.key("stranger", trusted=False))
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 2)
        self.assertIn("doesn't trust", done.stderr)

    def test_a_good_signature_from_a_trusted_key_passes(self):
        repo = self.repo('[git]\ntrunk = "main"\nrequire_signatures = true\n')
        key = repo.key("trusted", trusted=True)
        repo.trust()
        repo.commit("fix: signed", sign_with=key)
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("1 commit checked", done.stdout)

    def test_no_git_table_refuses_nothing_and_says_so(self):
        repo = self.repo(profile=CONVENTION)
        run(repo.root, "git", "checkout", "-q", "main")
        self.assertEqual(repo.guard("commit-guard").returncode, 0)
        run(repo.root, "git", "checkout", "-q", "work")
        repo.commit(f"fix: a change\n\n{SIGNED_OFF}")
        done = repo.guard("push-guard")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("undeclared", done.stdout)

    def test_nothing_to_publish_checks_nothing(self):
        done = self.repo().guard("push-guard")
        self.assertEqual(done.returncode, 0)
        self.assertIn("checked nothing", done.stdout)

    def test_no_interpreter_checks_nothing_and_blocks_nothing(self):
        repo = self.repo()
        run(repo.root, "git", "checkout", "-q", "main")
        fake = Path(repo.tmp.name) / "bin"
        fake.mkdir()
        old = fake / "python3"
        old.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        old.chmod(0o755)
        done = repo.guard("commit-guard", env={"PATH": str(fake), "HOME": repo.tmp.name})
        self.assertEqual(done.returncode, 0)
        self.assertIn("unrun", done.stdout)



class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-git"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-git").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "commit-guard"], cwd=tmp, capture_output=True, text=True, input="")
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("unrun", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("reinstall the unit", done.stdout)


if __name__ == "__main__":
    unittest.main()
