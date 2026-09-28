# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that the crate passes clippy's default set with warnings denied, as
TSK-2500 asks and ADR-1610 decides. TSK-2500 closes no requirement: the
linter passing is the precondition REQ-1186 needs before TSK-2510 binds `lint`
to it."""

import os
import re
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "crates/meow/Cargo.toml"
BASE_VARIABLE = "TSK_2500_BASE"
FIX_VARIABLE = "TSK_2500_FIX"
TARGET = ROOT / "target" / "tsk-2500"
ATTRIBUTE = re.compile(r"^\+\s*#!?\[\s*(allow|expect)\s*\(")


def run(*command, cwd=ROOT, env=None):
    return subprocess.run(list(command), cwd=cwd, capture_output=True, text=True, env=env)


def export(revision, scratch):
    archive = Path(scratch) / "tree.tar"
    exported = run("git", "archive", "--output", str(archive), revision, "crates/meow")
    if exported.returncode != 0:
        raise AssertionError(exported.stderr)
    with tarfile.open(archive) as tar:
        tar.extractall(scratch, filter="data")
    archive.unlink()
    return Path(scratch)


def sources(root):
    return {path.relative_to(root): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


class ClippyCheck(unittest.TestCase):
    """TSK-2500 criterion 1: clippy with warnings denied exits 0 with no output."""

    def test_clippy_denying_warnings_exits_0_with_no_output(self):
        """Criterion 1 (ADR-1610, towards REQ-1186): clippy's default set finds nothing in the crate.

        With TSK_2500_BASE set, it also holds the task's rule that no lint is
        allowed by an attribute, because an allowed finding passes the lint
        and still ships: the change adds no `allow` or `expect` attribute."""
        result = run(
            "cargo", "clippy", "--quiet", "--manifest-path", MANIFEST,
            "--all-features", "--all-targets", "--", "-D", "warnings",
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, f"{output.count('error:')} error: lines\n{output[-2000:]}")
        self.assertEqual(output.strip(), "")

        base = os.environ.get(BASE_VARIABLE, "").strip()
        if base:
            diff = run("git", "diff", "--unified=0", base, "--", "crates/meow/src")
            self.assertEqual(diff.returncode, 0, diff.stderr)
            added = [line for line in diff.stdout.splitlines() if ATTRIBUTE.match(line)]
            self.assertEqual(added, [], "lint attributes the change adds")


class FirstCommitIsClippyFix(unittest.TestCase):
    """TSK-2500 criterion 4, its checkable half: the first commit holds only what `cargo clippy --fix` wrote.

    The criterion is about one change's commits, so it reads the parent from
    TSK_2500_BASE and the first branch commit from TSK_2500_FIX, and is
    skipped without them, which reports that it didn't run rather than that
    it passed. The second commit's hand edits are judgement, as the task's
    record says."""

    def setUp(self):
        self.base = os.environ.get(BASE_VARIABLE, "").strip()
        self.fix = os.environ.get(FIX_VARIABLE, "").strip()
        if not (self.base and self.fix):
            self.skipTest(f"{BASE_VARIABLE} and {FIX_VARIABLE} name no revisions")

    def test_clippy_fix_on_the_parent_gives_the_first_commit(self):
        """Criterion 4 (ADR-1610, towards REQ-1186): `cargo clippy --fix` and `cargo fmt` on the parent give the first commit's crate sources, and it touches nothing outside them."""
        env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET))
        with tempfile.TemporaryDirectory() as parent, tempfile.TemporaryDirectory() as first:
            manifest = str(export(self.base, parent) / MANIFEST)
            fixed = run(
                "cargo", "clippy", "--quiet", "--fix", "--allow-dirty", "--allow-no-vcs",
                "--manifest-path", manifest, "--all-features", "--all-targets", env=env,
            )
            self.assertEqual(fixed.returncode, 0, fixed.stderr[-2000:])
            formatted = run("cargo", "fmt", "--manifest-path", manifest)
            self.assertEqual(formatted.returncode, 0, formatted.stderr)
            expected = sources(Path(parent) / "crates/meow/src")
            actual = sources(export(self.fix, first) / "crates/meow/src")
        differing = sorted(str(path) for path in expected.keys() | actual.keys() if expected.get(path) != actual.get(path))
        self.assertEqual(differing, [], "files where the first commit differs from clippy's fixes")

        changed = run("git", "diff", "--name-only", self.base, self.fix)
        self.assertEqual(changed.returncode, 0, changed.stderr)
        outside = [path for path in changed.stdout.split() if not path.startswith("crates/meow/src/")]
        self.assertEqual(outside, [], "paths the first commit changes beside crates/meow/src")


if __name__ == "__main__":
    unittest.main()
