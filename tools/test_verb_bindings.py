# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that this repository binds its five verbs to the crate, as TSK-2480
asks for check, test and build, TSK-2510 asks for format and lint, and
ADR-1610 decides (REQ-1186, SPC-1080)."""

import json
import re
import subprocess
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRATE_CHECK = "cargo check --quiet --manifest-path crates/meow/Cargo.toml --all-features --all-targets"
CRATE_FMT = "cargo fmt --manifest-path crates/meow/Cargo.toml --check"
CRATE_LINT = (
    "cargo clippy --quiet --manifest-path crates/meow/Cargo.toml"
    " --all-features --all-targets -- -D warnings"
)
CARGO_FMT = "cargo fmt --manifest-path crates/meow/Cargo.toml"


def mise_tasks():
    with open(ROOT / "mise.toml", "rb") as handle:
        return tomllib.load(handle)["tasks"]


def verbs():
    run = subprocess.run(
        [str(ROOT / "plugins/meow-checks/bin/meow-checks"), "status", "--json"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return json.loads(run.stdout)["verbs"]


class CrateCheckTask(unittest.TestCase):
    """TSK-2480 criterion 1: `mise run crate-check` exits 0 with no warning."""

    def test_task_runs_the_type_check_adr_1610_states(self):
        """Criterion 1 (REQ-1186): the task exists and runs the command ADR-1610 names."""
        self.assertEqual(mise_tasks().get("crate-check", {}).get("run"), CRATE_CHECK)

    def test_task_exits_0_with_no_warning(self):
        """Criterion 1 (REQ-1186): the run exits 0 and prints no warning."""
        run = subprocess.run(["mise", "run", "crate-check"], cwd=ROOT, capture_output=True, text=True)
        output = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, output)
        self.assertNotRegex(output, re.compile(r"^\s*warning", re.MULTILINE | re.IGNORECASE))


class VerbBindings(unittest.TestCase):
    """TSK-2480 criterion 2: check, test and build resolve to the crate's tasks."""

    def test_check_runs_crate_check(self):
        """Criterion 2 (REQ-1186): `check` resolves to `mise run crate-check`."""
        check = verbs()["check"]
        self.assertEqual(check.get("state"), "resolved", check)
        self.assertEqual(check.get("command"), "mise run crate-check")

    def test_build_runs_mise_build(self):
        """Criterion 2 (REQ-1186): `build` resolves to `mise run build`."""
        build = verbs()["build"]
        self.assertEqual(build.get("state"), "resolved", build)
        self.assertEqual(build.get("command"), "mise run build")

    def test_test_runs_the_crate_after_build_units(self):
        """Criterion 2 (REQ-1186): `test` names the task that runs `mise run crate` right after `crates/meow/build-units`."""
        test = verbs()["test"]
        self.assertEqual(test.get("state"), "resolved", test)
        self.assertEqual(test.get("command"), "mise run test")
        steps = [step.strip() for step in mise_tasks()["test"].get("run", "").split("&&")]
        self.assertEqual(steps[:2], ["crates/meow/build-units", "mise run crate"])

    def test_none_of_the_three_is_unresolved(self):
        """Criterion 2 (REQ-1186): each of check, test and build has a non-empty command."""
        resolved = verbs()
        for verb in ("check", "test", "build"):
            with self.subTest(verb=verb):
                self.assertEqual(resolved[verb].get("state"), "resolved", resolved[verb])
                self.assertTrue(resolved[verb].get("command", "").strip())


def named_through_the_verbs():
    """Each task the verbs name directly or through the task a verb composes."""
    named = set()
    for verb in verbs().values():
        named.update(re.findall(r"\bmise run ([\w-]+)", verb.get("command") or ""))
    for name in list(named):
        named.update(re.findall(r"\bmise run ([\w-]+)", mise_tasks().get(name, {}).get("run", "")))
    return named


class MiseCheck(unittest.TestCase):
    """TSK-2480 criterion 3: `meow-mise check` reports 0 findings over the new runs."""

    def test_meow_mise_check_passes_over_the_crate_tasks(self):
        """Criterion 3 (REQ-1186): 0 findings, over task runs that include crate-check, crate and build.

        `meow-mise check` prints a count and not the names, so the names come
        from the task runs the profile's verbs name, which are what it reads."""
        run = subprocess.run(
            [str(ROOT / "plugins/meow-mise/bin/meow-mise"), "check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        output = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, output)
        self.assertRegex(output, r"\b0 findings in [1-9]\d* task runs")
        for task in ("crate-check", "crate", "build"):
            with self.subTest(task=task):
                self.assertIn(task, named_through_the_verbs())


class Gate(unittest.TestCase):
    """TSK-2480 criterion 4: the gate runs `crate-check`."""

    def test_all_depends_on_crate_check(self):
        """Criterion 4 (REQ-1186): `crate-check` is among the tasks `mise run all` runs."""
        self.assertIn("crate-check", mise_tasks()["all"].get("depends", []))


def steps(command):
    return [step.strip() for step in (command or "").split("&&")]


class FormatAndLintTasks(unittest.TestCase):
    """TSK-2510, the tasks its criteria 1, 3 and 4 run: `crate-fmt` and `crate-lint` in `mise.toml`."""

    def test_crate_fmt_runs_the_formatter_check(self):
        """Criteria 1 and 3 (REQ-1186): `crate-fmt` runs the formatter's check TSK-2510 states."""
        self.assertEqual(mise_tasks().get("crate-fmt", {}).get("run"), CRATE_FMT)

    def test_crate_lint_runs_clippy_denying_warnings(self):
        """Criteria 1 and 4 (REQ-1186): `crate-lint` runs clippy with `-D warnings` on the command line."""
        self.assertEqual(mise_tasks().get("crate-lint", {}).get("run"), CRATE_LINT)


class FormatAndLintBindings(unittest.TestCase):
    """TSK-2510 criterion 1: `format` ends with crate-fmt and `lint` with crate-lint.

    Running the five verbs from here would run this file again through
    `test`, so the pass half of the criterion was seen in that task's pull
    request, and this holds the half that a program reads from the bindings.
    `VerbBindings` already holds that check, test and build resolve."""

    def test_format_ends_with_crate_fmt(self):
        """Criterion 1 (REQ-1186): `format` still checks the Markdown first and ends with `mise run crate-fmt`."""
        format_verb = verbs()["format"]
        self.assertEqual(format_verb.get("state"), "resolved", format_verb)
        command = steps(format_verb.get("command"))
        self.assertEqual(command[0], "mise run fmt-check")
        self.assertEqual(command[-1], "mise run crate-fmt")

    def test_lint_ends_with_crate_lint(self):
        """Criterion 1 (REQ-1186): `lint` ends with `mise run crate-lint`, after the steps it already ran."""
        lint = verbs()["lint"]
        self.assertEqual(lint.get("state"), "resolved", lint)
        command = steps(lint.get("command"))
        self.assertEqual(command[-1], "mise run crate-lint")
        self.assertIn("plugins/meow-mise/bin/meow-mise check", command[:-1])


class MiseCheckWithFormatAndLint(unittest.TestCase):
    """TSK-2510 criterion 2: `meow-mise check` reports 0 findings over runs that include the five crate tasks."""

    def test_meow_mise_check_passes_over_all_five_crate_tasks(self):
        """Criterion 2 (REQ-1186): 0 findings, over task runs that include crate-fmt, crate-lint, crate-check, crate and build."""
        run = subprocess.run(
            [str(ROOT / "plugins/meow-mise/bin/meow-mise"), "check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        output = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, output)
        self.assertRegex(output, r"\b0 findings in [1-9]\d* task runs")
        for task in ("crate-fmt", "crate-lint", "crate-check", "crate", "build"):
            with self.subTest(task=task):
                self.assertIn(task, named_through_the_verbs())

    def test_the_test_task_names_declared_tasks(self):
        """BUG-1510: every task the test chain names is declared in `mise.toml`."""
        for name in re.findall(r"\bmise run ([\w-]+)", mise_tasks()["test"].get("run", "")):
            with self.subTest(task=name):
                self.assertIn(name, mise_tasks())


class FmtFormatsTheCrate(unittest.TestCase):
    """TSK-2510 criterion 5, the half read from `mise.toml`: `mise run fmt` also runs `cargo fmt` on the crate."""

    def test_fmt_runs_cargo_fmt_without_check(self):
        """Criterion 5 (REQ-1186): the `fmt` task keeps its Markdown step and adds `cargo fmt` on the crate's manifest."""
        command = steps(mise_tasks()["fmt"].get("run"))
        self.assertIn("prettier --write '**/*.md'", command)
        self.assertIn(CARGO_FMT, command)


class GateWithFormatAndLint(unittest.TestCase):
    """TSK-2510 criterion 6, the half read from `mise.toml`: `mise run all` runs the three crate tasks."""

    def test_all_depends_on_the_three_crate_tasks(self):
        """Criterion 6 (REQ-1186): crate-fmt, crate-lint and crate-check are among the tasks `mise run all` runs."""
        depends = mise_tasks()["all"].get("depends", [])
        for task in ("crate-fmt", "crate-lint", "crate-check"):
            with self.subTest(task=task):
                self.assertIn(task, depends)


if __name__ == "__main__":
    unittest.main()
