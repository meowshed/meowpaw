# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1140 states `meow-mise` reports.

Most fixtures run the real mise in a scratch repository, with its home, state
and parent directories isolated, because what the pack reads is what mise
prints, and a stand-in would only test the stand-in (RES-0126). A few put a
stand-in `mise` first on the path, for output real mise won't produce on
demand. `MEOW_MISE_BIN` names the launcher to test, so the fixtures can first
run against a program that reports nothing and be seen failing (REQ-2072).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_MISE_BIN", UNIT / "bin" / "meow-mise"))
MISE = shutil.which("mise") or "mise"

TASKS = '''[tasks.test]
run = "echo test"

[tasks.deploy]
run = "echo deploy"
confirm = "Deploy now?"

[tasks.secret]
run = "echo secret"
hide = true

[tasks.greet]
usage = 'arg "<name>"'
run = "echo hello"

[tasks.build]
run = "echo build"
sources = ["src.txt"]
outputs = ["out.txt"]

[tasks.mine]
run = "echo committed"
'''
SHIP = '#!/bin/sh\n#MISE confirm="Ship it?"\necho ship\n'
PLAIN = "#!/bin/sh\necho plain\n"
EXEC = '[tasks.t]\nrun = "echo {{exec(command=\'echo x\')}}"\n'


class Repository:
    """A git repository at `<tmp>/parent/repo`, with mise stopped at `<tmp>`."""

    def __init__(self, files, untracked=None, parent=None, trusted=False, stand_in=None, path=None):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.parent = base / "parent"
        self.root = self.parent / "repo"
        self.home = base / "home"
        for directory in (self.root, self.home):
            directory.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("MISE_", "__MISE_"))}
        self.env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / ".config"),
                        XDG_STATE_HOME=str(self.home / ".state"), XDG_CACHE_HOME=str(self.home / ".cache"),
                        XDG_DATA_HOME=str(self.home / ".data"), MISE_CEILING_PATHS=str(base),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        if trusted:
            self.env["MISE_TRUSTED_CONFIG_PATHS"] = str(self.root)
        if stand_in is not None:
            tools = base / "tools"
            tools.mkdir()
            script = tools / "mise"
            script.write_text("#!/bin/sh\n" + stand_in, encoding="utf-8")
            script.chmod(0o755)
            self.env["PATH"] = f"{tools}{os.pathsep}{self.env['PATH']}"
        if path is not None:
            self.env["PATH"] = path(base)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        self.write(self.root, files)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=self.env)
        self.write(self.root, untracked or {})
        self.write(self.parent, parent or {})

    @staticmethod
    def write(where, files):
        for name, text in files.items():
            path = where / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            if text.startswith("#!"):
                path.chmod(0o755)

    def run(self, *args):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)

    def mise(self, *args):
        return subprocess.run([MISE, *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)


class Fixture(unittest.TestCase):
    def repo(self, files, **options):
        repository = Repository(files, **options)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    @staticmethod
    def task(output, name):
        """The lines `status` prints for one task: its own line and those indented under it."""
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"  {name}: "):
                block = [line]
                for rest in lines[i + 1:]:
                    if not rest.startswith("    "):
                        break
                    block.append(rest)
                return "\n".join(block)
        raise AssertionError(f"no task {name} in:\n{output}")


class Status(Fixture):
    def setUp(self):
        self.repository = self.repo(
            {"mise.toml": TASKS, "mise-tasks/ship": SHIP, "mise-tasks/plain": PLAIN},
            untracked={"mise.local.toml": '[tasks.mine]\nrun = "echo local"\n'},
            parent={"mise.toml": '[tasks.extra]\nrun = "echo extra"\n'})
        self.done = self.repository.run("status")

    def test_it_reports_and_exits_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stdout + self.done.stderr)

    def test_the_tasks_are_what_this_work_tree_resolves(self):
        """REQ-2460, REQ-2464: listed through mise, and reported as resolved, never as declared."""
        self.assertIn("tasks resolved in this work tree", self.done.stdout)
        self.assertNotIn("declared tasks", self.done.stdout)
        self.assertIn("  plain: repository mise-tasks/plain", self.done.stdout)

    def test_the_version_is_reported(self):
        """REQ-2496: the runner's version."""
        version = self.repository.mise("--version").stdout.split()[0]
        self.assertIn(f"mise: {version}", self.done.stdout)

    def test_a_committed_task_carries_no_block(self):
        self.assertEqual(self.task(self.done.stdout, "test"), "  test: repository mise.toml")

    def test_a_hidden_task_is_blocked(self):
        """REQ-2479: a private task is never bound."""
        self.assertIn("blocked: hidden", self.task(self.done.stdout, "secret"))

    def test_a_confirm_task_is_blocked_in_either_form(self):
        """REQ-2478: a TOML key and a file task's header both ask for a person."""
        self.assertIn("blocked: asks for a person", self.task(self.done.stdout, "deploy"))
        self.assertIn("blocked: asks for a person", self.task(self.done.stdout, "ship"))

    def test_a_required_argument_is_read_not_discovered(self):
        """REQ-2476: the argument comes from the enumeration, and nothing ran."""
        self.assertIn("blocked: needs <name>", self.task(self.done.stdout, "greet"))

    def test_a_task_that_can_skip_says_so(self):
        """REQ-2470: freshness is decided by a method mise doesn't report."""
        block = self.task(self.done.stdout, "build")
        self.assertIn("can skip as fresh: freshness decided by mise, by a method it doesn't report", block)
        self.assertNotIn("blocked", block)

    def test_a_task_from_outside_is_named_so(self):
        """REQ-2465: a task from outside the repository doesn't reproduce elsewhere."""
        block = self.task(self.done.stdout, "extra")
        self.assertIn("extra: outside ", block)
        self.assertIn("blocked: not committed", block)

    def test_a_replaced_task_is_reported(self):
        """REQ-2500: mise.local.toml replaces a committed task silently."""
        block = self.task(self.done.stdout, "mine")
        self.assertIn("mine: work tree only mise.local.toml", block)
        self.assertIn("replaced by mise.local.toml; mise.toml declares it", block)
        self.assertIn("blocked: not committed", block)

    def test_the_listing_says_it_ran_mise(self):
        """REQ-2473: the listing ran mise over the configuration."""
        self.assertIn("listing ran mise over the configuration", self.done.stdout)
        self.assertIn("no committed configuration file calls exec", self.done.stdout)


class Trust(Fixture):
    def test_an_untrusted_template_is_unresolved_and_stays_untrusted(self):
        """REQ-2466, REQ-2467: reported as untrusted, never as empty, and never trusted."""
        repository = self.repo({"mise.toml": EXEC})
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn(f"unresolved: untrusted {repository.root}; a person runs mise trust {repository.root} after reading it",
                      done.stdout)
        self.assertIn("untrusted", repository.mise("trust", "--show").stdout)
        self.assertNotIn(": trusted", repository.mise("trust", "--show").stdout)

    def test_a_trusted_template_is_named_as_run(self):
        """REQ-2473: listing a trusted file evaluates its templates, and the file is named."""
        done = self.repo({"mise.toml": EXEC}, trusted=True).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("templates calling exec, evaluated by the listing: mise.toml", done.stdout)


class Unresolved(Fixture):
    def test_no_marker_runs_no_mise(self):
        """REQ-2472: detection is a static read, and mise never starts."""
        repository = self.repo({"README.md": "# r\n"}, stand_in='touch "$HOME/ran"\n')
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: not a mise repository", done.stdout)
        self.assertFalse((repository.home / "ran").exists(), "mise ran")

    def test_a_file_task_directory_is_a_marker(self):
        """REQ-2472: a repository holding only file tasks is still a mise repository."""
        repository = self.repo({".mise/tasks/t": PLAIN}, stand_in='touch "$HOME/ran"; echo "2026.9.11 x"; echo "[]"\n')
        repository.run("status")
        self.assertTrue((repository.home / "ran").exists())

    def test_mise_missing_is_unresolved(self):
        def without_mise(base):
            tools = base / "git-only"
            tools.mkdir()
            (tools / "git").symlink_to(shutil.which("git"))
            return f"{tools}{os.pathsep}/usr/bin{os.pathsep}/bin"
        done = self.repo({"mise.toml": ""}, path=without_mise).run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: mise not found", done.stdout)

    def test_an_unrecognised_listing_is_never_empty(self):
        """REQ-2462: another shape is unresolved, never an empty task list."""
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo \'{"tasks": []}\';; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn('unresolved: unrecognised shape: {"tasks": []}', done.stdout)

    def test_an_entry_without_a_name_is_unrecognised(self):
        """REQ-2462: an array whose entries lack a string name is not a listing."""
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo \'[{"source": "x"}]\';; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: unrecognised shape", done.stdout)

    def test_an_older_mise_is_an_environment_failure(self):
        """REQ-2496: a flag an older version lacks is the environment's, not the repository's."""
        stand_in = ('case "$1" in --version) echo "2025.1.0 macos-arm64";; '
                    "tasks) echo \"error: unexpected argument '--hidden' found\" >&2; exit 2;; *) echo '[]';; esac\n")
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: environment: mise 2025.1.0 predates --hidden", done.stdout)

    def test_a_current_mise_rejecting_a_flag_is_the_packs_defect(self):
        stand_in = ('case "$1" in --version) echo "2026.9.11 macos-arm64";; '
                    "tasks) echo \"error: unexpected argument '--hidden' found\" >&2; exit 2;; *) echo '[]';; esac\n")
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: meow-mise defect: --hidden", done.stdout)

    def test_another_failure_is_never_empty(self):
        stand_in = 'case "$1" in --version) echo "2026.9.11 macos-arm64";; tasks) echo boom >&2; exit 5;; *) echo "[]";; esac\n'
        done = self.repo({"mise.toml": ""}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: mise failed with exit status 5: boom", done.stdout)


if __name__ == "__main__":
    unittest.main()
