# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1150 states `meow-gotask` reports.

Most fixtures run the real Task in a scratch repository with its home
isolated, because what the pack reads is what Task prints (RES-0127). A few
put a stand-in `task` first on the path, for output real Task won't produce on
demand. `MEOW_GOTASK_BIN` names the launcher to test, so the fixtures can
first run against a program that reports nothing and be seen failing
(REQ-2072).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_GOTASK_BIN", UNIT / "bin" / "meow-gotask"))
TASK = shutil.which("task") or "task"

TASKFILE = """version: '3'
includes:
  sub: ./sub
vars:
  TOKEN:
    value: never-printed-value
    secret: true
tasks:
  test:
    cmds: [echo test]
  priv:
    internal: true
    cmds: [echo priv]
  ask:
    prompt: Are you sure?
    cmds: [echo ask]
  deploy:
    requires:
      vars: [ENV]
    cmds: [echo deploy]
  lint:
    cmds:
      - cmd: exit 1
        ignore_error: true
  all:
    deps: [lint]
    cmds: [echo all]
  cond:
    if: 'false'
    cmds: [echo cond]
  plat:
    platforms: [windows]
    cmds: [echo plat]
  fresh:
    status: ['true']
    cmds: [echo fresh]
  build:
    method: timestamp
    sources: [src.txt]
    generates: [out.txt]
    cmds: [echo build]
  sums:
    sources: [src.txt]
    generates: [out.txt]
    cmds: [echo ran-sums]
"""
SUB = "version: '3'\ntasks:\n  inner:\n    cmds: [echo inner]\n"
REMOTE = "version: '3'\nincludes:\n  far: https://example.org/Taskfile.yml\ntasks:\n  test:\n    cmds: [echo test]\n"


class Repository:
    def __init__(self, files, stand_in=None, path=None):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.root = base / "repo"
        self.home = base / "home"
        for directory in (self.root, self.home):
            directory.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("TASK_", "MISE_", "__MISE_"))}
        self.env.update(HOME=str(self.home), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        if stand_in is not None:
            tools = base / "tools"
            tools.mkdir()
            script = tools / "task"
            script.write_text("#!/bin/sh\necho \"$@\" >> \"$HOME/calls\"\n" + stand_in, encoding="utf-8")
            script.chmod(0o755)
            self.env["PATH"] = f"{tools}{os.pathsep}{self.env['PATH']}"
        if path is not None:
            self.env["PATH"] = path(base)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        for name, text in files.items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=self.env)

    def run(self, *args):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)

    def calls(self):
        calls = self.home / "calls"
        return calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []

    def tree(self):
        return subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"], cwd=self.root,
                              capture_output=True, text=True, env=self.env).stdout


class Fixture(unittest.TestCase):
    def repo(self, files, **options):
        repository = Repository(files, **options)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    @staticmethod
    def task(output, name):
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
        self.repository = self.repo({"Taskfile.yml": TASKFILE, "sub/Taskfile.yml": SUB, "src.txt": "a\n",
                                     "out.txt": ""})
        self.before = self.repository.tree()
        self.done = self.repository.run("status")

    def test_it_reports_and_exits_zero(self):
        self.assertEqual(self.done.returncode, 0, self.done.stdout + self.done.stderr)
        self.assertIn("tasks resolved in this work tree", self.done.stdout)

    def test_the_version_is_reported(self):
        version = subprocess.run([TASK, "--version"], capture_output=True, text=True).stdout.split()[-1]
        self.assertIn(f"task: {version}", self.done.stdout)

    def test_a_committed_task_carries_no_block(self):
        self.assertEqual(self.task(self.done.stdout, "test"), "  test: repository Taskfile.yml")

    def test_an_included_task_keeps_its_namespace(self):
        self.assertEqual(self.task(self.done.stdout, "sub:inner"), "  sub:inner: repository sub/Taskfile.yml")

    def test_a_prompt_asks_for_a_person(self):
        self.assertIn("blocked: asks for a person", self.task(self.done.stdout, "ask"))

    def test_a_required_variable_is_read_before_anything_runs(self):
        """REQ-2508: the input is read from the definition, and nothing ran."""
        self.assertIn("blocked: needs variables ENV", self.task(self.done.stdout, "deploy"))

    def test_an_ignored_error_is_reported(self):
        """REQ-2480: a stage bound to it can't report the failure it ignores."""
        block = self.task(self.done.stdout, "lint")
        self.assertIn("blocked: ignores errors", block)
        self.assertIn("a stage bound to it can't report the failure it ignores", block)

    def test_a_dependency_carries_its_block_up(self):
        """REQ-2480: a task depending on one that ignores errors passes that failure on."""
        block = self.task(self.done.stdout, "all")
        self.assertIn("blocked: ignores errors, through lint", block)
        self.assertIn("a stage bound to it can't report the failure it ignores", block)

    def test_if_and_platforms_are_blocks(self):
        self.assertIn("blocked: runs only if false", self.task(self.done.stdout, "cond"))
        self.assertIn("blocked: runs only on windows", self.task(self.done.stdout, "plat"))

    def test_what_decides_a_skip_is_named(self):
        self.assertIn("can skip as up to date: decided by its status commands", self.task(self.done.stdout, "fresh"))
        self.assertIn("can skip as up to date: decided by the timestamp of its sources",
                      self.task(self.done.stdout, "build"))

    def test_a_secret_is_named_as_masked_and_never_shown(self):
        """REQ-2510: masking is not protection, and the value is never printed."""
        self.assertIn("  TOKEN (Taskfile.yml): masked in Task's output, not protected", self.done.stdout)
        self.assertNotIn("never-printed-value", self.done.stdout)

    def test_listing_leaves_the_tree_and_freshness_alone(self):
        """RES-0127: a listing that wrote a checksum would make this run skip."""
        self.assertEqual(self.repository.tree(), self.before)
        ran = subprocess.run([TASK, "sums"], cwd=self.repository.root, capture_output=True, text=True,
                             env=self.repository.env, stdin=subprocess.DEVNULL)
        self.assertIn("ran-sums", ran.stdout, ran.stderr)


BINDABLE = """version: '3'
tasks:
  test:
    cmds: [echo test]
  tests:
    cmds: [echo tests]
  lint:
    cmds:
      - cmd: exit 1
        ignore_error: true
  build:
    sources: [src.txt]
    cmds: [echo build]
  priv:
    internal: true
    cmds: [echo priv]
  ask:
    prompt: Sure?
    cmds: [echo ask]
  deploy:
    requires:
      vars: [ENV]
    cmds: [echo deploy]
"""


def profile(verbs):
    return "[verbs]\n" + "".join(f'{verb} = "{command}"\n' for verb, command in verbs.items())


class Bind(Fixture):
    def setUp(self):
        self.done = self.repo({"Taskfile.yml": BINDABLE, "src.txt": "a\n"}).run("bind")

    def test_a_verb_binds_to_its_exact_task_with_force(self):
        self.assertEqual(self.done.returncode, 0, self.done.stdout + self.done.stderr)
        self.assertIn('test = "task --force test"', self.done.stdout)
        self.assertIn('build = "task --force build"', self.done.stdout)
        self.assertNotIn("--force tests", self.done.stdout)

    def test_a_blocked_task_is_left_unbound_with_its_reason(self):
        self.assertIn("# lint: task lint is blocked: ignores errors", self.done.stdout)
        self.assertIn("# format: no task named format", self.done.stdout)


class Check(Fixture):
    def check(self, verbs, files=None):
        return self.repo({"Taskfile.yml": BINDABLE, "src.txt": "a\n", ".meowpaw/profile.toml": profile(verbs),
                          **(files or {})}).run("check")

    def test_a_skippable_task_without_force_is_a_finding(self):
        done = self.check({"build": "task build"})
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  build: task build can skip as up to date and runs without --force", done.stdout)

    def test_a_forced_task_is_clean(self):
        done = self.check({"build": "task --force build", "test": "task test"})
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 findings in 2 task runs", done.stdout)

    def test_hand_written_bindings_report_their_blocks_never_missing(self):
        """REQ-2508: a task needing a variable is reported before it runs, and an internal one as internal."""
        done = self.check({"test": "task priv", "lint": "task --force ask", "build": "task --force deploy"})
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  test: task priv is internal", done.stdout)
        self.assertIn("  lint: task ask is blocked: asks for a person", done.stdout)
        self.assertIn("  build: task deploy is blocked: needs variables ENV", done.stdout)
        self.assertNotIn("no task named", done.stdout)

    def test_a_remote_include_is_a_finding(self):
        """REQ-2487: an include from outside the repository fails the gate, whether or not a verb uses it."""
        repository = self.repo({"Taskfile.yml": REMOTE, ".meowpaw/profile.toml": profile({"test": "task test"})},
                               stand_in='echo "3.53.1"\n')
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  remote include far: https://example.org/Taskfile.yml (Taskfile.yml)", done.stdout)
        self.assertFalse(any("--list-all" in call for call in repository.calls()), repository.calls())

    def test_the_skill_forbids_writing_a_remote_include(self):
        """REQ-2487: the harness never authors one."""
        skill = (UNIT / "skills" / "gotask" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never write an include whose `taskfile` names a URL", skill)


class Remote(Fixture):
    def test_a_remote_include_is_named_and_nothing_listed(self):
        """REQ-2486: the include is reported before any task from it is used."""
        repository = self.repo({"Taskfile.yml": REMOTE}, stand_in='echo "3.53.1"\n')
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("remote include far: https://example.org/Taskfile.yml (Taskfile.yml)", done.stdout)
        self.assertIn("unresolved: remote include", done.stdout)
        self.assertFalse(any("--list-all" in call for call in repository.calls()), repository.calls())

    def test_a_remote_include_behind_a_local_one_is_found(self):
        repository = self.repo({"Taskfile.yml": "version: '3'\nincludes:\n  sub: ./sub\n", "sub/Taskfile.yml": REMOTE},
                               stand_in='echo "3.53.1"\n')
        done = repository.run("status")
        self.assertIn("remote include far: https://example.org/Taskfile.yml (sub/Taskfile.yml)", done.stdout)


class Unresolved(Fixture):
    def stand_in(self, listing):
        return f'case "$1" in --version) echo "3.53.1";; *) {listing};; esac\n'

    def test_no_taskfile_runs_no_task(self):
        repository = self.repo({"README.md": "# r\n"}, stand_in="true\n")
        done = repository.run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: not a Task repository", done.stdout)
        self.assertEqual(repository.calls(), [])

    def test_task_missing_is_unresolved(self):
        def without_task(base):
            tools = base / "git-only"
            tools.mkdir()
            (tools / "git").symlink_to(shutil.which("git"))
            return f"{tools}{os.pathsep}/usr/bin{os.pathsep}/bin"
        done = self.repo({"Taskfile.yml": SUB}, path=without_task).run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: task not found", done.stdout)

    def test_104_is_never_untrusted(self):
        done = self.repo({"Taskfile.yml": SUB}, stand_in=self.stand_in("echo 'not trusted by user' >&2; exit 104")).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: a remote Taskfile this listing can't see, since it reads no trust or cache", done.stdout)
        self.assertNotIn("untrusted", done.stdout)

    def test_106_is_unresolved(self):
        done = self.repo({"Taskfile.yml": SUB}, stand_in=self.stand_in("exit 106")).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("a remote Taskfile this listing can't see", done.stdout)

    def test_an_older_task_is_an_environment_failure(self):
        stand_in = 'case "$1" in --version) echo "3.40.0";; *) echo "unknown flag: --json" >&2; exit 2;; esac\n'
        done = self.repo({"Taskfile.yml": SUB}, stand_in=stand_in).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: environment: task 3.40.0 predates --json", done.stdout)

    def test_a_current_task_rejecting_a_flag_is_the_packs_defect(self):
        done = self.repo({"Taskfile.yml": SUB}, stand_in=self.stand_in('echo "unknown flag: --json" >&2; exit 2')).run("status")
        self.assertIn("unresolved: meow-gotask defect: --json", done.stdout)

    def test_an_unrecognised_listing_is_never_empty(self):
        done = self.repo({"Taskfile.yml": SUB}, stand_in=self.stand_in("echo '[]'")).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: unrecognised shape: []", done.stdout)

    def test_a_taskfile_that_doesnt_parse_is_unresolved(self):
        done = self.repo({"Taskfile.yml": "version: '3'\ntasks: [\n"}, stand_in=self.stand_in("echo '{}'")).run("status")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unresolved: Taskfile.yml doesn't parse", done.stdout)


class Launcher(unittest.TestCase):
    """SPC-1080, BUG-1240: a launcher with no binary beside it reports each subcommand unresolved, never passed."""

    def test_a_missing_binary_is_unresolved_and_names_the_machine_and_the_reinstall(self):
        machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
        for subcommand in ["status", "bind", "check"]:
            with self.subTest(subcommand=subcommand), tempfile.TemporaryDirectory() as tmp:
                launcher = Path(tmp) / "bin" / "meow-gotask"
                launcher.parent.mkdir()
                launcher.write_text(BIN.read_text(encoding="utf-8"), encoding="utf-8")
                launcher.chmod(0o755)
                done = subprocess.run(["sh", str(launcher), subcommand], cwd=tmp, capture_output=True, text=True, input="")
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn(f"meow-gotask {subcommand}: unresolved: ", done.stdout)
                self.assertIn(machine, done.stdout)
                self.assertIn("install meow-core", done.stdout)


if __name__ == "__main__":
    unittest.main()
