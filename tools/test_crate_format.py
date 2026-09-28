# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that the crate takes the form `cargo fmt` gives it, as TSK-2490 asks
and ADR-1610 decides. TSK-2490 closes no requirement: the formatter's check is
the precondition REQ-1186 needs before TSK-2510 binds `format` to it."""

import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "crates/meow/Cargo.toml"
BASE_VARIABLE = "TSK_2490_BASE"


def run(*command, cwd=ROOT):
    return subprocess.run(list(command), cwd=cwd, capture_output=True, text=True)


def sources(root):
    return {path.relative_to(root): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


class FormatterCheck(unittest.TestCase):
    """TSK-2490 criterion 1: `cargo fmt --check` exits 0 with no output."""

    def test_cargo_fmt_check_exits_0_with_no_output(self):
        """Criterion 1 (ADR-1610, towards REQ-1186): the formatter finds nothing to change in the crate."""
        result = run("cargo", "fmt", "--manifest-path", MANIFEST, "--check")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, f"{output.count('Diff in')} Diff in blocks")
        self.assertEqual(output.strip(), "")


class NothingButTheFormatter(unittest.TestCase):
    """TSK-2490 criterion 3: `cargo fmt` on the parent revision leaves this change's tree.

    The criterion is about one change, so it needs that change's parent, and
    a default would go wrong the moment a later change edits the crate. It
    reads the parent from TSK_2490_BASE and is skipped without it, which
    reports that it didn't run rather than that it passed."""

    def setUp(self):
        self.base = os.environ.get(BASE_VARIABLE, "").strip()
        if not self.base:
            self.skipTest(f"{BASE_VARIABLE} names no parent revision")

    def test_formatting_the_parent_gives_this_tree(self):
        """Criterion 3 (ADR-1610, towards REQ-1186): the crate's sources equal the parent's after `cargo fmt`, and the change touches nothing else in the crate."""
        with tempfile.TemporaryDirectory() as scratch:
            archive = Path(scratch) / "base.tar"
            exported = run("git", "archive", "--output", str(archive), self.base, "crates/meow")
            self.assertEqual(exported.returncode, 0, exported.stderr)
            with tarfile.open(archive) as tar:
                tar.extractall(scratch, filter="data")
            formatted = run("cargo", "fmt", "--manifest-path", str(Path(scratch) / MANIFEST))
            self.assertEqual(formatted.returncode, 0, formatted.stderr)
            expected = sources(Path(scratch) / "crates/meow/src")
        actual = sources(ROOT / "crates/meow/src")
        differing = sorted(str(path) for path in expected.keys() | actual.keys() if expected.get(path) != actual.get(path))
        self.assertEqual(differing, [], "files that differ from the formatter's output")

        changed = run("git", "diff", "--name-only", self.base, "--", "crates/meow", "rustfmt.toml", ".rustfmt.toml")
        self.assertEqual(changed.returncode, 0, changed.stderr)
        outside = [path for path in changed.stdout.split() if not path.startswith("crates/meow/src/")]
        self.assertEqual(outside, [], "changed paths beside crates/meow/src")


if __name__ == "__main__":
    unittest.main()
