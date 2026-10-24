# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The core unit ships the one build of the tool, with every unit's program in it (TSK-5300, REQ-4500)."""

import json
import platform
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBCOMMANDS = ("verbs", "scm", "git", "record", "github", "licence", "author", "mise", "gotask", "prose",
               "markdown", "rust", "go", "typescript", "python", "csharp", "lua", "godot", "starlark", "scheme", "unattended", "loop")


def target():
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}.get(platform.system(), "pc-windows-msvc")
    cpu = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
    return f"{cpu}-{system}"


class SharedBinary(unittest.TestCase):
    def test_the_core_unit_binary_carries_every_units_program(self):
        """TSK-5300 criterion 1, REQ-4500: `meow` in the core unit names all 15 subcommands as carried."""
        binary = ROOT / "plugins/meow-core/bin" / target() / "paw"
        self.assertTrue(binary.is_file(), f"{binary} was not built")
        done = subprocess.run([str(binary)], capture_output=True, text=True)
        carried = [word.strip(",") for word in (done.stdout + done.stderr).split("carries:")[-1].split()]
        self.assertEqual(sorted(carried), sorted(SUBCOMMANDS))


def launchers():
    """Every launcher a plugin ships: a shell file in a unit's `bin/` that looks for the shared executable."""
    found = []
    for path in sorted(ROOT.glob("plugins/*/bin/*")):
        if path.is_file() and path.read_text(encoding="utf-8", errors="replace").startswith("#!/bin/sh") \
                and "binary=" in path.read_text(encoding="utf-8"):
            found.append(path)
    return found


class ExecutableName(unittest.TestCase):
    def test_every_launcher_and_the_build_name_the_executable_paw(self):
        """TSK-5680 criterion 1, REQ-4610: the build writes `paw` with `.exe` on Windows, and each launcher looks for it."""
        build = (ROOT / "crates/meow/build-units").read_text(encoding="utf-8")
        self.assertIn('paw$exe', build)
        self.assertIn("*-windows-*) exe=.exe", build)
        self.assertNotRegex(build, r"meow-\$target|meow-\$\{target\}")
        paths = launchers()
        self.assertGreaterEqual(len(paths), 15, "the survey found too few launchers to mean anything")
        for path in paths:
            with self.subTest(launcher=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn('/paw$exe', text)
                self.assertIn("system=pc-windows-msvc exe=.exe", text)
                self.assertNotRegex(text, r"meow-\$cpu-\$system|bin/meow-\$")

    def test_a_launcher_renamed_away_from_paw_fails(self):
        """TSK-5680 criterion 1, REQ-4610: the survey would catch a launcher that looks for another name."""
        text = (ROOT / "plugins/meow-git/bin/meow-git").read_text(encoding="utf-8")
        self.assertIn('/paw$exe', text)
        self.assertNotIn('/paw$exe', text.replace('/paw$exe', '/meow$exe'))


class CoreDistribution(unittest.TestCase):
    def test_the_core_build_carries_every_feature_and_no_launcher_resolves_its_own_wrapper(self):
        """TSK-5680 criterion 2, REQ-4612: the core build is all-features, the Pi core extension exports the path,
        and each Pi launcher runs it and never itself."""
        build = (ROOT / "crates/meow/build-units").read_text(encoding="utf-8")
        self.assertGreaterEqual(build.count("--all-features"), 2, "a build path leaves out a feature")
        extension = (ROOT / "packages/meow-core/extensions/kernel.ts").read_text(encoding="utf-8")
        self.assertIn("process.env.MEOWPAW_BINARY", extension)
        for path in sorted(ROOT.glob("packages/*/bin/*")):
            if not path.is_file():
                continue
            with self.subTest(launcher=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn('exec "$MEOWPAW_BINARY"', text)
                self.assertNotIn('exec "$0"', text)
        for path in launchers():
            with self.subTest(launcher=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn('exec "$0"', text)
                self.assertNotIn(f'exec "$here/{path.name}"', text)


class EqualVersions(unittest.TestCase):
    def test_a_plugin_and_its_package_carry_the_same_version(self):
        """TSK-5680 criterion 3, REQ-4614: each unit's plugin manifest and package manifest agree, and so does the
        package page's `describes` line."""
        manifests = sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json"))
        self.assertGreaterEqual(len(manifests), 15)
        for manifest in manifests:
            unit = manifest.parent.parent.name
            package = ROOT / "packages" / unit / "package.json"
            with self.subTest(unit=unit):
                self.assertTrue(package.is_file(), f"{unit} has a plugin and no package")
                plugin_version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
                package_version = json.loads(package.read_text(encoding="utf-8"))["version"]
                self.assertEqual(plugin_version, package_version, unit)
                page = (ROOT / "packages" / unit / "README.md").read_text(encoding="utf-8")
                described = re.search(r"^describes: \[@meowshed/%s@([^\]]+)\]" % re.escape(unit), page, re.M)
                self.assertTrue(described, f"{unit}'s package page names no version")
                self.assertEqual(described.group(1), package_version, unit)


if __name__ == "__main__":
    unittest.main()
