# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit that runs a program names the core unit and no other under `dependencies` (TSK-5301, REQ-4502, REQ-4508)."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def manifests():
    for path in sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json")):
        yield path.parent.parent, json.loads(path.read_text())


def has_launcher(unit):
    return any(p.is_file() for p in (unit / "bin").glob("*") if p.name.startswith("meow-") or p.name == "paw")


class Dependencies(unittest.TestCase):
    def test_a_unit_with_a_launcher_depends_on_the_core_unit_alone(self):
        """TSK-5301 criterion 1, REQ-4502: each unit with a launcher lists `meow-core` and nothing else."""
        wrong = []
        for unit, manifest in manifests():
            if unit.name == "meow-core" or not has_launcher(unit):
                continue
            if manifest.get("dependencies") != ["meow-core"]:
                wrong.append(f"{unit.name}: {manifest.get('dependencies')}")
        self.assertEqual(wrong, [])

    def test_no_unit_names_another_unit_but_the_core(self):
        """TSK-5301 criterion 1, REQ-4502: a dependency list never names a unit other than `meow-core`."""
        wrong = []
        for unit, manifest in manifests():
            for entry in manifest.get("dependencies", []):
                name = entry if isinstance(entry, str) else entry.get("name")
                if name != "meow-core":
                    wrong.append(f"{unit.name}: {name}")
        self.assertEqual(wrong, [])

    def test_each_unit_carries_its_own_version_and_no_range_on_another(self):
        """TSK-5301 criterion 4, REQ-4508: each manifest has a version, and a dependency carries no range."""
        wrong = []
        for unit, manifest in manifests():
            if not manifest.get("version"):
                wrong.append(f"{unit.name}: no version")
            for entry in manifest.get("dependencies", []):
                if isinstance(entry, dict) and "version" in entry:
                    wrong.append(f"{unit.name}: a range on {entry.get('name')}")
        self.assertEqual(wrong, [])


if __name__ == "__main__":
    unittest.main()
