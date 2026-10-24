# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Each pack's README states its toolchain's versions and how it prints its tool's configuration (TSK-5025, SPC-1190).

The five packs the task names are read. The language packs state their toolchains in their own words, and a
later task would bring them under the same sentence.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
# A sentence of the README that says what the pack is current as of, with a version number in it.
CURRENT = re.compile(r"current as of[^.]*?\d+\.\d+", re.IGNORECASE | re.DOTALL)
# A pack that prints a stages table with `bind` says the repository commits what it prints.
PRINTS = re.compile(r"`bind`|\bbind\b` prints|meow-[a-z]+ bind")
COMMITS = re.compile(r"\bcommit\b[^.]*\bprints\b|\bprints\b[^.]*\bcommit\b|commit what (?:it|`bind`) prints", re.IGNORECASE)


NAMED = ("meow-git", "meow-github", "meow-mise", "meow-gotask", "meow-markdown")


def packs():
    return [PLUGINS / name for name in NAMED]


def readme(unit):
    return " ".join((unit / "README.md").read_text(encoding="utf-8").split())


class PackReadmes(unittest.TestCase):
    def test_the_fixture_finds_the_packs(self):
        """TSK-5025: each named unit is a pack by its own declaration."""
        for unit in packs():
            requires = (unit / "requires.toml").read_text(encoding="utf-8")
            self.assertRegex(requires, r'(?m)^layer *= *"pack"')

    def test_every_pack_readme_states_the_versions_it_is_current_as_of(self):
        """TSK-5025 criterion 1, REQ-0085: a line names each tool it drives and the version it was observed against."""
        missing = [unit.name for unit in packs() if not CURRENT.search(readme(unit))]
        self.assertEqual(missing, [])

    def test_a_pack_that_prints_configuration_says_the_repository_commits_it(self):
        """TSK-5025 criterion 2, REQ-0082: the README names the command that prints and says to commit what it prints."""
        printing = [unit for unit in packs() if PRINTS.search(readme(unit))]
        self.assertTrue(printing)
        missing = [unit.name for unit in printing if not COMMITS.search(readme(unit))]
        self.assertEqual(missing, [])

    def test_the_rules_can_fail(self):
        """TSK-5025, REQ-0085: a README without the sentence fails both rules."""
        self.assertIsNone(CURRENT.search("It needs mise on the machine."))
        self.assertIsNone(COMMITS.search("`meow-mise bind` prints a table."))
        self.assertIsNotNone(CURRENT.search("The pack is current as of mise 2026.10.7."))
        self.assertIsNotNone(COMMITS.search("Commit what `bind` prints."))


if __name__ == "__main__":
    unittest.main()
