# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The method skill tells a step that lacks a capability to record a defect or a postponement (TSK-5040, REQ-1670).

The skill is text a model follows, so the fixture reads it for the rule. Whether a session follows the rule rests on
judgement, and the repository's hand-run cases are where that is measured.
"""

import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
SKILLS = (UNIT / "skills" / "method" / "SKILL.md",
          UNIT.parent.parent / "packages" / "meow-flow" / "skills" / "method" / "SKILL.md")


def rules(text):
    """The numbered rules of the skill, each on one line."""
    return [" ".join(part.split()) for part in re.split(r"\n(?=- [A-Z]\d+\. )", text)]


def missing_capability_rule(text):
    return [r for r in rules(text) if re.search(r"capabilit", r) and "defect" in r and "postponement" in r]


class MissingCapability(unittest.TestCase):
    def test_a_skill_without_the_rule_is_found_missing(self):
        """TSK-5040 criterion 1: the fixture can fail."""
        self.assertEqual(missing_capability_rule("- M1. Do the step.\n- M2. Ask, because it helps.\n"), [])

    def test_the_method_skill_records_a_missing_capability(self):
        """TSK-5040 criterion 1, REQ-1670: a missing capability is a defect or a postponement, with its reason."""
        for path in SKILLS:
            found = missing_capability_rule(path.read_text(encoding="utf-8"))
            self.assertEqual(len(found), 1, path)
            self.assertIn("because", found[0], path)

    def test_the_rule_names_no_language_and_no_tool(self):
        """TSK-5040, REQ-0070: the rule holds in every repository."""
        for path in SKILLS:
            found = missing_capability_rule(path.read_text(encoding="utf-8"))
            self.assertEqual(len(found), 1, path)
            self.assertNotRegex(found[0], r"(?i)\b(cargo|npm|python|rust|git|gh|mise)\b")


if __name__ == "__main__":
    unittest.main()
