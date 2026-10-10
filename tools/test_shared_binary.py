# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The core unit ships the one build of the tool, with every unit's program in it (TSK-5300, REQ-4500)."""

import platform
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBCOMMANDS = ("verbs", "scm", "git", "record", "github", "licence", "author", "mise", "gotask", "prose",
               "markdown", "unattended", "loop")


def target():
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}.get(platform.system(), "pc-windows-msvc")
    cpu = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
    return f"{cpu}-{system}"


class SharedBinary(unittest.TestCase):
    def test_the_core_unit_binary_carries_every_units_program(self):
        """TSK-5300 criterion 1, REQ-4500: `meow` in the core unit names all 13 subcommands as carried."""
        binary = ROOT / "plugins/meow-core/bin" / target() / "meow"
        self.assertTrue(binary.is_file(), f"{binary} was not built")
        done = subprocess.run([str(binary)], capture_output=True, text=True)
        carried = [word.strip(",") for word in (done.stdout + done.stderr).split("carries:")[-1].split()]
        self.assertEqual(sorted(carried), sorted(SUBCOMMANDS))


if __name__ == "__main__":
    unittest.main()
