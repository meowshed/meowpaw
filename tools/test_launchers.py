# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit's launcher finds the shared binary through the core unit's data directory (TSK-5301, REQ-4504, REQ-4506)."""

import os
import platform
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHERS = sorted(p for p in (ROOT / "plugins").glob("*/bin/*")
                   if p.is_file() and p.name in (f"meow-{n}" for n in (
                       "author", "checks", "git", "github", "gotask", "licence", "loop", "markdown", "mise",
                       "prose-gate", "scm", "unattended")) or p == ROOT / "plugins/meow-flow/bin/paw")


def target():
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}.get(platform.system(), "pc-windows-msvc")
    cpu = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
    return f"{cpu}-{system}"


class Launchers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def unit_with(self, launcher):
        """The launcher alone in a unit directory, with no binary of its own beside it."""
        shutil.rmtree(self.base, ignore_errors=True)
        unit = self.base / "unit"
        (unit / "bin").mkdir(parents=True)
        copy = unit / "bin" / launcher.name
        shutil.copy(launcher, copy)
        copy.chmod(0o755)
        return copy

    def subcommands(self, launcher):
        """The subcommands the launcher's own `case "$1"` names, in order."""
        text = launcher.read_text()
        found = []
        for label in re.findall(r"^([a-z][a-z-]*(?: \| [a-z][a-z-]*)*)\)", text, re.M):
            found += label.split(" | ")
        found += re.findall(r'"\$1" = "([a-z][a-z-]*)"', text)
        return found or ["status"]

    def run_launcher(self, launcher, shared=False, sub="status"):
        copy = self.unit_with(launcher)
        data = self.base / "data"
        env = {"PATH": os.environ["PATH"], "HOME": str(self.base / "home"),
               "CLAUDE_PLUGIN_DATA": str(data / "unit-test")}
        if shared:
            root = self.base / "core"
            binary = root / "bin" / target() / "meow"
            binary.parent.mkdir(parents=True)
            binary.write_text('#!/bin/sh\necho "shared: $*"\n')
            binary.chmod(0o755)
            (data / "meow-core-test").mkdir(parents=True)
            (data / "meow-core-test" / "meow-root").write_text(f"{root}\n")
        return subprocess.run([str(copy), sub], input="", capture_output=True, text=True, env=env)

    def test_every_unit_has_a_launcher_to_test(self):
        """TSK-5301 criterion 2, REQ-4504: the fixture finds the 12 units' launchers and the record's."""
        self.assertEqual(len(LAUNCHERS), 13, [p.name for p in LAUNCHERS])

    def test_a_launcher_runs_the_binary_the_data_file_names(self):
        """TSK-5301 criterion 2, REQ-4504: with the core unit's data file, each launcher runs the shared binary."""
        for launcher in LAUNCHERS:
            with self.subTest(launcher=launcher.name):
                done = self.run_launcher(launcher, shared=True)
                self.assertIn("shared:", done.stdout + done.stderr, done.stdout + done.stderr)

    def test_a_launcher_finds_the_core_unit_beside_it_in_a_checkout(self):
        """TSK-5302, REQ-4504: loaded in place, a unit finds `plugins/meow-core` beside it with no data file."""
        for launcher in LAUNCHERS:
            with self.subTest(launcher=launcher.name):
                shutil.rmtree(self.base, ignore_errors=True)
                plugins = self.base / "plugins"
                (plugins / launcher.parent.parent.name / "bin").mkdir(parents=True)
                copy = plugins / launcher.parent.parent.name / "bin" / launcher.name
                shutil.copy(launcher, copy)
                copy.chmod(0o755)
                binary = plugins / "meow-core" / "bin" / target() / "meow"
                binary.parent.mkdir(parents=True)
                binary.write_text('#!/bin/sh\necho "shared: $*"\n')
                binary.chmod(0o755)
                sub = self.subcommands(launcher)[0]
                env = {"PATH": os.environ["PATH"], "HOME": str(self.base / "home")}
                done = subprocess.run([str(copy), sub], input="", capture_output=True, text=True, env=env)
                self.assertIn("shared:", done.stdout + done.stderr, done.stdout + done.stderr)

    def test_a_launcher_with_no_binary_names_the_core_unit(self):
        """TSK-5301 criterion 3, REQ-4506: with no data file and no binary, each reports and names meow-core."""
        for launcher in LAUNCHERS:
            with self.subTest(launcher=launcher.name):
                said = []
                for sub in self.subcommands(launcher):
                    done = self.run_launcher(launcher, shared=False, sub=sub)
                    self.assertNotIn("shared:", done.stdout + done.stderr)
                    said.append(done.stdout + done.stderr)
                self.assertTrue(any("meow-core" in text for text in said), said)


if __name__ == "__main__":
    unittest.main()
