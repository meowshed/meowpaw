# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that this repository binds check, test and build to the crate, as
TSK-2480 asks and ADR-1610 decides (REQ-1186, SPC-1080)."""

import json
import re
import subprocess
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRATE_CHECK = "cargo check --quiet --manifest-path crates/meow/Cargo.toml --all-features --all-targets"


def mise_tasks():
    with open(ROOT / "mise.toml", "rb") as handle:
        return tomllib.load(handle)["tasks"]


def verbs():
    run = subprocess.run(
        [str(ROOT / "plugins/meow-verbs/bin/meow-verbs"), "status", "--json"],
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
        """Criterion 2 (REQ-1186): `test` runs `mise run crate` right after `crates/meow/build-units`."""
        test = verbs()["test"]
        self.assertEqual(test.get("state"), "resolved", test)
        steps = [step.strip() for step in test.get("command", "").split("&&")]
        self.assertEqual(steps[:2], ["crates/meow/build-units", "mise run crate"])

    def test_none_of_the_three_is_unresolved(self):
        """Criterion 2 (REQ-1186): each of check, test and build has a non-empty command."""
        resolved = verbs()
        for verb in ("check", "test", "build"):
            with self.subTest(verb=verb):
                self.assertEqual(resolved[verb].get("state"), "resolved", resolved[verb])
                self.assertTrue(resolved[verb].get("command", "").strip())


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
        named = set()
        for verb in verbs().values():
            named.update(re.findall(r"\bmise run ([\w-]+)", verb.get("command") or ""))
        for task in ("crate-check", "crate", "build"):
            with self.subTest(task=task):
                self.assertIn(task, named)


class Gate(unittest.TestCase):
    """TSK-2480 criterion 4: the gate runs `crate-check`."""

    def test_all_depends_on_crate_check(self):
        """Criterion 4 (REQ-1186): `crate-check` is among the tasks `mise run all` runs."""
        self.assertIn("crate-check", mise_tasks()["all"].get("depends", []))


if __name__ == "__main__":
    unittest.main()
