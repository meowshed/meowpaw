# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that `format` and `lint` reach the shell every unit ships, as
TSK-2520 asks to restore REQ-1186 after BUG-1240.

The shell is each unit's launcher in `plugins/<unit>/bin/`, a hook script in
`plugins/<unit>/hooks/` and `crates/meow/build-units`. The planted checks copy
those files into a scratch tree and run the task's own command from
`mise.toml` there, so the working tree is never edited."""

import json
import os
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL_FMT = 'files=$(shfmt -f plugins crates/meow) && test -n "$files" && shfmt -i 2 -d $files'
SHELL_LINT = 'files=$(shfmt -f plugins crates/meow) && test -n "$files" && shellcheck $files'
SHFMT_WRITE = 'shfmt -i 2 -w $(shfmt -f plugins crates/meow)'
UNFORMATTED = "\nif true; then\n      echo planted\nfi\n"
SPACE_AFTER_EQUALS = "\nplanted= value\n"


def mise_tasks():
    with open(ROOT / "mise.toml", "rb") as handle:
        return tomllib.load(handle)["tasks"]


def verbs():
    run = subprocess.run(
        [str(ROOT / "plugins/meow-verbs/bin/meow-verbs"), "status", "--json"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return json.loads(run.stdout)["verbs"]


def steps(command):
    return [step.strip() for step in (command or "").split("&&")]


def shipped_shell():
    """Every shell file a unit ships, found from the tree and not from shfmt."""
    found = {"crates/meow/build-units"}
    for path in ROOT.glob("plugins/*/bin/*"):
        if path.is_file():
            found.add(path.relative_to(ROOT).as_posix())
    for path in ROOT.glob("plugins/*/hooks/*"):
        if path.is_file() and path.read_bytes().startswith(b"#!"):
            found.add(path.relative_to(ROOT).as_posix())
    return found


def scratch_tree(scratch, planted=""):
    """A copy of one launcher and of build-units, with `planted` appended to the launcher."""
    base = Path(scratch)
    launcher = base / "plugins" / "meow-mise" / "bin" / "meow-mise"
    launcher.parent.mkdir(parents=True)
    shutil.copy(ROOT / "plugins/meow-mise/bin/meow-mise", launcher)
    (base / "crates" / "meow").mkdir(parents=True)
    shutil.copy(ROOT / "crates/meow/build-units", base / "crates/meow/build-units")
    if planted:
        with open(launcher, "a") as handle:
            handle.write(planted)
    return base


def tool_path():
    """PATH with the tools `mise.toml` pins first, since mise's shims resolve nothing in a scratch tree."""
    directories = []
    for tool in ("shfmt", "shellcheck"):
        found = subprocess.run(["mise", "which", tool], cwd=ROOT, capture_output=True, text=True)
        if found.returncode == 0 and found.stdout.strip():
            directories.append(str(Path(found.stdout.strip()).parent))
    return os.pathsep.join(directories + [os.environ.get("PATH", "")])


def shell(command, cwd):
    env = dict(os.environ, PATH=tool_path())
    return subprocess.run(["sh", "-c", command], cwd=cwd, capture_output=True, text=True, env=env)


class ShellFiles(unittest.TestCase):
    """TSK-2520 criterion 1: the file list both tasks read holds every shipped shell file."""

    def test_shfmt_finds_every_launcher_hook_script_and_build_units(self):
        """Criterion 1 (REQ-1186): nothing a unit ships as shell is missing from `shfmt -f plugins crates/meow`."""
        run = subprocess.run(["shfmt", "-f", "plugins", "crates/meow"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        expected = shipped_shell()
        self.assertGreaterEqual(len(expected), 12, expected)
        self.assertLessEqual(expected, set(run.stdout.split()))


class ShellTasks(unittest.TestCase):
    """TSK-2520 criteria 2 and 3: `shell-fmt` and `shell-lint` exist, `all` runs them, and `fmt` writes the shell."""

    def test_shell_fmt_runs_shfmt_in_diff_mode(self):
        """Criterion 2 (REQ-1186): `shell-fmt` runs the command TSK-2520 states."""
        self.assertEqual(mise_tasks().get("shell-fmt", {}).get("run"), SHELL_FMT)

    def test_shell_lint_runs_shellcheck(self):
        """Criterion 2 (REQ-1186): `shell-lint` runs the command TSK-2520 states."""
        self.assertEqual(mise_tasks().get("shell-lint", {}).get("run"), SHELL_LINT)

    def test_all_depends_on_both(self):
        """Criterion 2 (REQ-1186): the gate runs both tasks."""
        depends = mise_tasks()["all"].get("depends", [])
        for task in ("shell-fmt", "shell-lint"):
            with self.subTest(task=task):
                self.assertIn(task, depends)

    def test_fmt_writes_the_shell(self):
        """Criterion 3 (REQ-1186): `fmt` keeps its other steps and adds shfmt writing in place."""
        command = steps(mise_tasks()["fmt"].get("run"))
        self.assertIn("prettier --write '**/*.md'", command)
        self.assertIn(SHFMT_WRITE, command)

    def test_the_tools_are_pinned(self):
        """Criterion 2 (REQ-1186): `mise.toml` pins both tools, so CI and a laptop run the same versions."""
        with open(ROOT / "mise.toml", "rb") as handle:
            tools = tomllib.load(handle)["tools"]
        for tool in ("shellcheck", "shfmt"):
            with self.subTest(tool=tool):
                self.assertRegex(str(tools.get(tool, "")), r"^\d+\.\d+\.\d+$")


class ShellBindings(unittest.TestCase):
    """TSK-2520 criterion 4: `format` runs `shell-fmt` and `lint` runs `shell-lint`."""

    def test_format_runs_shell_fmt(self):
        """Criterion 4 (REQ-1186): `format` runs `mise run shell-fmt` and still ends with the crate's check."""
        command = steps(verbs()["format"].get("command"))
        self.assertIn("mise run shell-fmt", command)
        self.assertEqual(command[-1], "mise run crate-fmt")

    def test_lint_runs_shell_lint(self):
        """Criterion 4 (REQ-1186): `lint` runs `mise run shell-lint` and still ends with the crate's lint."""
        command = steps(verbs()["lint"].get("command"))
        self.assertIn("mise run shell-lint", command)
        self.assertEqual(command[-1], "mise run crate-lint")


class PlantedDefects(unittest.TestCase):
    """TSK-2520 criteria 5 and 6: each task passes the shipped shell and fails a planted defect."""

    def test_shell_fmt_fails_an_unformatted_launcher(self):
        """Criterion 5 (REQ-1186): `shell-fmt` exits 0 on the files as shipped and 1 on a badly indented block."""
        command = mise_tasks().get("shell-fmt", {}).get("run")
        self.assertTrue(command, "mise.toml has no `shell-fmt` task")
        with tempfile.TemporaryDirectory() as clean, tempfile.TemporaryDirectory() as planted:
            passed = shell(command, scratch_tree(clean))
            failed = shell(command, scratch_tree(planted, UNFORMATTED))
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertIn("meow-mise", failed.stdout)

    def test_shell_lint_fails_a_space_after_equals(self):
        """Criterion 6 (REQ-1186): `shell-lint` exits 0 on the files as shipped and fails naming SC1007 on the plant."""
        command = mise_tasks().get("shell-lint", {}).get("run")
        self.assertTrue(command, "mise.toml has no `shell-lint` task")
        with tempfile.TemporaryDirectory() as clean, tempfile.TemporaryDirectory() as planted:
            passed = shell(command, scratch_tree(clean))
            failed = shell(command, scratch_tree(planted, SPACE_AFTER_EQUALS))
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertNotEqual(failed.returncode, 0, failed.stdout + failed.stderr)
        self.assertIn("SC1007", failed.stdout)

    def test_an_empty_tree_is_no_pass(self):
        """Criterion 7 (REQ-1186): with no shell file to read, each task fails and never passes on nothing."""
        tasks = mise_tasks()
        for name in ("shell-fmt", "shell-lint"):
            with self.subTest(task=name), tempfile.TemporaryDirectory() as empty:
                command = tasks.get(name, {}).get("run")
                self.assertTrue(command, f"mise.toml has no `{name}` task")
                (Path(empty) / "plugins").mkdir()
                (Path(empty) / "crates" / "meow").mkdir(parents=True)
                done = shell(command, empty)
                # Exit 1 with nothing printed is the empty list refused; a missing tool exits 127 and says so.
                self.assertEqual((done.returncode, done.stdout + done.stderr), (1, ""))


if __name__ == "__main__":
    unittest.main()
