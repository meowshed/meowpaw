# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that the marketplace ships no unit the chain no longer uses, as
TSK-3870 asks for `meow-method` (REQ-3654, ADR-2300)."""

import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETIRED = ("meow-method",)


class RetiredUnits(unittest.TestCase):
    def test_the_marketplace_lists_no_retired_unit(self):
        """TSK-3870 criterion 1: `.claude-plugin/marketplace.json` has no entry for a retired unit."""
        listed = {p["name"] for p in json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"]}
        for unit in RETIRED:
            self.assertNotIn(unit, listed)

    def test_no_retired_unit_is_in_the_tree(self):
        """TSK-3870 criterion 2: `plugins/<unit>` doesn't exist for a retired unit."""
        for unit in RETIRED:
            self.assertFalse((ROOT / "plugins" / unit).exists(), unit)

    def test_the_test_verb_runs_no_retired_unit(self):
        """TSK-3870 criterion 3: the profile's `test` verb names no retired unit's tests."""
        with open(ROOT / ".meowpaw/profile.toml", "rb") as handle:
            test = tomllib.load(handle)["verbs"]["test"]
        for unit in RETIRED:
            self.assertNotIn(f"plugins/{unit}", test)


if __name__ == "__main__":
    unittest.main()
