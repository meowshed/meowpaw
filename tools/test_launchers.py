# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the launcher's platform stop (REQ-1738): a unit's launcher
compares the platform version it runs under with the `claude_code` its
`requires.toml` names, and on an older one prints both versions and exits 3
without running the binary."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def system_cpu():
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}.get(os.uname().sysname)
    cpu = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}.get(os.uname().machine)
    return system, cpu


class Launcher:
    """A scratch unit carrying the real launcher of `source`, a fake binary,
    a requires.toml and a `claude` stub that reports the version asked for."""

    def __init__(self, source="meow-scm", claude_code="2.1.283", reported=None, no_claude=False):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.unit = root / "plugins" / "meow-demo"
        (self.unit / "bin").mkdir(parents=True)
        for name in os.listdir(ROOT / "plugins" / source / "bin"):
            if name.startswith("meow-"):
                launcher = ROOT / "plugins" / source / "bin" / name
                self.launcher = self.unit / "bin" / name
                self.launcher.write_text(launcher.read_text(encoding="utf-8"))
                self.launcher.chmod(0o755)
                break
        self.write_requires(claude_code)
        system, cpu = system_cpu()
        self.bin_dir = self.unit / "bin" / f"{cpu}-{system}"
        self.bin_dir.mkdir()
        self.binary = self.bin_dir / "paw"
        self.binary.write_text("#!/bin/sh\necho the-binary-ran\n")
        self.binary.chmod(0o755)
        stubs = root / "stubs"
        stubs.mkdir()
        if reported is not None:
            claude = stubs / "claude"
            claude.write_text(f"#!/bin/sh\necho '{reported} (Claude Code)'\n")
            claude.chmod(0o755)
        if no_claude:
            # A stub that fails, so the machine's own claude, if any, never
            # answers and the version the launcher reads stays unknown.
            claude = stubs / "claude"
            claude.write_text("#!/bin/sh\nexit 1\n")
            claude.chmod(0o755)
        self.env = {**ENV, "PATH": f"{stubs}:{os.environ['PATH']}" if reported is not None or no_claude else ENV["PATH"]}

    def write_requires(self, claude_code):
        (self.unit / "requires.toml").write_text(f'claude_code = "{claude_code}"\n', encoding="utf-8")

    def run(self, *args):
        return subprocess.run([str(self.launcher), *args], capture_output=True, text=True, env=self.env)


class Stop(unittest.TestCase):
    def launcher(self, **kwargs):
        done = Launcher(**kwargs)
        self.addCleanup(done.tmp.cleanup)
        return done

    def test_an_older_platform_stops_the_launcher(self):
        """REQ-1738: on a platform older than requires.toml names, the launcher prints both versions and exits 3."""
        done = self.launcher(reported="2.1.200")
        self.assertEqual(done.run("check").returncode, 3)
        # The binary never ran, so its output is absent from both streams.
        self.assertNotIn("the-binary-ran", done.run("check").stdout)

    def test_an_older_platform_names_both_versions(self):
        """REQ-1738: the stop names the version the platform reports and the one the unit was tested on."""
        done = self.launcher(reported="2.1.200")
        finished = done.run("check")
        self.assertIn("2.1.200", finished.stderr + finished.stdout)
        self.assertIn("2.1.283", finished.stderr + finished.stdout)

    def test_the_tested_platform_runs_the_binary(self):
        """REQ-1738: on the tested version the launcher runs the binary as before."""
        done = self.launcher(reported="2.1.283")
        self.assertIn("the-binary-ran", done.run("check").stdout)

    def test_a_newer_platform_runs_the_binary(self):
        """REQ-1738: a platform newer than the one tested runs the binary too."""
        done = self.launcher(reported="2.2.0")
        self.assertIn("the-binary-ran", done.run("check").stdout)

    def test_an_unknown_version_runs_the_binary(self):
        """REQ-1738: where the platform's version can't be read, the launcher says so and runs the binary."""
        done = self.launcher(no_claude=True)
        finished = done.run("check")
        self.assertIn("the-binary-ran", finished.stdout)
        self.assertIn("unknown", finished.stderr + finished.stdout)

    def test_every_binary_unit_ships_the_stop(self):
        """REQ-1738: every unit with a launcher reads the platform version its requires.toml names."""
        for launcher in sorted((ROOT / "plugins").glob("*/bin/meow-*")) + sorted((ROOT / "plugins").glob("*/bin/paw")):
            if not launcher.is_file():
                continue
            unit = launcher.parent.parent
            with self.subTest(unit=unit.name):
                text = launcher.read_text(encoding="utf-8")
                self.assertIn("requires.toml", text, f"{unit.name}'s launcher reads no requires.toml")
                self.assertIn("claude --version", text, f"{unit.name}'s launcher reads no platform version")


if __name__ == "__main__":
    unittest.main()
