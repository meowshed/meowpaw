# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that the tasks behind `format`, `lint` and `fmt` catch, or fix, a defect
planted in the crate, as TSK-2510 asks and ADR-1610 decides (REQ-1186).

Each check plants its defect in a copy of `crates/meow` and runs the task's
own command from `mise.toml` against the copy's manifest, so the working tree
is never edited. `tools/test_verb_bindings.py` holds that `format` and `lint`
end with these tasks, and together they cover the verbs' exit status."""

import os
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "crates/meow/Cargo.toml"
PLANTED_FILE = "src/main.rs"
TARGET = ROOT / "target" / "tsk-2510"
UNFORMATTED = "\nfn   planted_by_tsk_2510 ( )->u8{ 1 }\n"
COLLAPSIBLE_IF = """
#[allow(dead_code)]
fn planted_by_tsk_2510(first: bool, second: bool) {
    if first {
        if second {
            println!("planted");
        }
    }
}
"""


def mise_task(name):
    with open(ROOT / "mise.toml", "rb") as handle:
        run = tomllib.load(handle)["tasks"].get(name, {}).get("run")
    if not run:
        raise AssertionError(f"mise.toml has no `{name}` task with a run command")
    return run


def copy_crate(scratch, planted=""):
    crate = Path(scratch) / "crates" / "meow"
    shutil.copytree(ROOT / "crates" / "meow", crate, ignore=shutil.ignore_patterns("target"))
    if planted:
        with open(crate / PLANTED_FILE, "a") as handle:
            handle.write(planted)
    return crate


def against(command, crate):
    """The command with the repository's manifest swapped for the copy's."""
    if MANIFEST not in command:
        raise AssertionError(f"`{command}` names no {MANIFEST}")
    return command.replace(MANIFEST, str(crate / "Cargo.toml"))


def shell(command):
    env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
    return subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, env=env)


class FormatCatchesAnUnformattedLine(unittest.TestCase):
    """TSK-2510 criterion 3: an unformatted line in `crates/meow/src` makes `format` exit 1."""

    def test_crate_fmt_passes_the_clean_copy_and_fails_the_planted_one(self):
        """Criterion 3 (REQ-1186): `crate-fmt` exits 0 on the crate as it is and 1 once a line is left unformatted."""
        command = mise_task("crate-fmt")
        with tempfile.TemporaryDirectory() as clean, tempfile.TemporaryDirectory() as planted:
            passed = shell(against(command, copy_crate(clean)))
            failed = shell(against(command, copy_crate(planted, UNFORMATTED)))
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertIn("main.rs", failed.stdout + failed.stderr)


class LintCatchesACollapsibleIf(unittest.TestCase):
    """TSK-2510 criterion 4: a collapsible `if` in `crates/meow/src` makes `lint` fail naming `collapsible_if`."""

    def test_crate_lint_fails_naming_collapsible_if(self):
        """Criterion 4 (REQ-1186): `crate-lint` exits non-zero on the planted `if` and names `collapsible_if`.

        clippy itself exits 101; the 1 the criterion states is `meow-verbs`
        reporting that failure, which that task's pull request showed."""
        command = mise_task("crate-lint")
        with tempfile.TemporaryDirectory() as planted:
            failed = shell(against(command, copy_crate(planted, COLLAPSIBLE_IF)))
        output = failed.stdout + failed.stderr
        self.assertNotEqual(failed.returncode, 0, output[-2000:])
        self.assertIn("collapsible_if", output)


class FmtFormatsThePlantedLine(unittest.TestCase):
    """TSK-2510 criterion 5: `mise run fmt` gives an unformatted line the formatter's form."""

    def test_fmt_step_formats_the_line_and_crate_fmt_then_passes(self):
        """Criterion 5 (REQ-1186): the `cargo fmt` step of `fmt` rewrites the planted line, and `crate-fmt` then exits 0."""
        fmt_steps = [step.strip() for step in mise_task("fmt").split("&&")]
        cargo_fmt = [step for step in fmt_steps if step.startswith("cargo fmt ") and "--check" not in step]
        self.assertEqual(len(cargo_fmt), 1, f"`fmt` runs {fmt_steps}, with no `cargo fmt` step that writes")
        check = mise_task("crate-fmt")
        with tempfile.TemporaryDirectory() as planted:
            crate = copy_crate(planted, UNFORMATTED)
            before = (crate / PLANTED_FILE).read_text()
            formatted = shell(against(cargo_fmt[0], crate))
            after = (crate / PLANTED_FILE).read_text()
            checked = shell(against(check, crate))
        self.assertEqual(formatted.returncode, 0, formatted.stderr)
        self.assertNotEqual(after, before)
        self.assertIn("fn planted_by_tsk_2510() -> u8 {", after)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
