# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A launcher resolves its binary once per machine and reuses the path (TSK-5684, REQ-4510).

Each test runs the real launcher of a unit in a scratch layout: a data
directory the platform would provide for the unit, the core unit's data
directory beside it holding the pointer to the shared binary, and a `uname`
stand-in that counts its calls."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNIT = "meow-scm"


def system_cpu():
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}[os.uname().sysname]
    cpu = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}[os.uname().machine]
    return system, cpu


class Cache(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.unit = self.root / "plugins" / UNIT
        (self.unit / "bin").mkdir(parents=True)
        self.launcher = self.unit / "bin" / UNIT
        self.launcher.write_text((ROOT / "plugins" / UNIT / "bin" / UNIT).read_text(encoding="utf-8"))
        self.launcher.chmod(0o755)
        self.data = self.root / "data" / f"{UNIT}-meowpaw"
        self.data.mkdir(parents=True)
        self.core_data = self.root / "data" / "meow-core-meowpaw"
        self.core_data.mkdir()
        stubs = self.root / "stubs"
        stubs.mkdir()
        self.calls = self.root / "uname-calls"
        real = subprocess.run(["which", "uname"], capture_output=True, text=True).stdout.strip()
        stub = stubs / "uname"
        stub.write_text(f'#!/bin/sh\necho x >>"{self.calls}"\nexec {real} "$@"\n')
        stub.chmod(0o755)
        self.env = {
            "PATH": f"{stubs}:{os.environ['PATH']}",
            "HOME": str(self.root / "home"),
            "CLAUDE_PLUGIN_DATA": str(self.data),
        }

    def shared_binary(self, name):
        """A shared binary under a root of its own, which the core unit's pointer names."""
        system, cpu = system_cpu()
        root = self.root / name
        binary = root / "bin" / f"{cpu}-{system}" / "paw"
        binary.parent.mkdir(parents=True)
        binary.write_text(f"#!/bin/sh\necho ran-{name}\n")
        binary.chmod(0o755)
        (self.core_data / "meow-root").write_text(f"{root}\n")
        return binary

    def run_launcher(self):
        return subprocess.run([str(self.launcher), "convention"], capture_output=True, text=True, env=self.env)

    def probes(self):
        return len(self.calls.read_text().splitlines()) if self.calls.exists() else 0

    def test_the_second_run_neither_probes_nor_walks(self):
        """TSK-5684 criterion 1, REQ-4510: the second run reads the cached path, so uname runs only in the first and the pointer is not read."""
        self.shared_binary("first")
        self.assertIn("ran-first", self.run_launcher().stdout)
        first = self.probes()
        self.assertGreater(first, 0)
        # With the core unit's data directory gone, a run that walked it would
        # find nothing and stop; the cached path still runs the binary.
        (self.core_data / "meow-root").unlink()
        self.assertIn("ran-first", self.run_launcher().stdout)
        self.assertEqual(first, self.probes())

    def test_the_cache_is_a_file_under_the_data_directory(self):
        """TSK-5684 criterion 1, REQ-4510: the resolved path is kept under the unit's data directory."""
        binary = self.shared_binary("first")
        self.run_launcher()
        kept = [p for p in self.data.iterdir() if p.is_file()]
        self.assertEqual(1, len(kept), kept)
        self.assertIn(str(binary), kept[0].read_text())

    def test_a_cached_binary_that_is_gone_resolves_again(self):
        """TSK-5684 criterion 2, REQ-4510: with the binary deleted the launcher resolves again, replaces the cache and runs the new one."""
        old = self.shared_binary("first")
        self.run_launcher()
        old.unlink()
        new = self.shared_binary("second")
        self.assertIn("ran-second", self.run_launcher().stdout)
        kept = [p for p in self.data.iterdir() if p.is_file()]
        self.assertIn(str(new), kept[0].read_text())
        self.assertNotIn(str(old), kept[0].read_text())

    def test_a_changed_path_resolves_again(self):
        """TSK-5684 criterion 2, REQ-4510: a cache written under another PATH is not trusted, because the probe's answer depends on the tools PATH finds."""
        self.shared_binary("first")
        self.run_launcher()
        first = self.probes()
        self.env["PATH"] = f"{self.env['PATH']}:{self.root}"
        self.assertIn("ran-first", self.run_launcher().stdout)
        self.assertGreater(self.probes(), first)

    def test_an_unreadable_cache_resolves_again(self):
        """TSK-5684 criterion 2, REQ-4510: a cache that holds nothing useful means resolve again."""
        self.shared_binary("first")
        self.run_launcher()
        for kept in self.data.iterdir():
            kept.write_text("")
        self.assertIn("ran-first", self.run_launcher().stdout)

    def test_no_data_directory_means_no_cache(self):
        """TSK-5684 criterion 1, REQ-4510: outside the platform there is no data directory, and the launcher still runs the binary."""
        self.shared_binary("first")
        del self.env["CLAUDE_PLUGIN_DATA"]
        # The pointer sits under the home directory's plugin data in that case.
        home_data = Path(self.env["HOME"]) / ".claude" / "plugins" / "data" / "meow-core-meowpaw"
        home_data.parent.mkdir(parents=True)
        (self.core_data).rename(home_data)
        self.assertIn("ran-first", self.run_launcher().stdout)


if __name__ == "__main__":
    unittest.main()
