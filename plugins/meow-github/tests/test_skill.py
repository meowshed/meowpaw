# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The `governance` skill says why the governance guard asks (BUG-1562, REQ-2576, REQ-2712).

A rule the harness holds three times has an instruction beside its hook and its check. The skill is loaded by a
description that states the obligation (ADR-1050).
"""

import json
import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
SKILL = UNIT / "skills" / "governance" / "SKILL.md"


class GovernanceSkill(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SKILL.is_file(), "the unit ships no governance skill")
        self.text = SKILL.read_text(encoding="utf-8")
        head = self.text.split("---")[1]
        self.fields = dict(line.split(": ", 1) for line in head.strip().splitlines())

    def test_the_description_states_the_obligation_and_names_each_verb(self):
        """REQ-1144, REQ-1146, REQ-1148: loaded before a change to how the repository is governed."""
        self.assertEqual(self.fields["name"], "governance")
        description = self.fields["description"]
        self.assertRegex(description, r"It MUST be loaded before[^.]*(branch protection|ruleset)[^.]*\.")
        for verb in ("secret", "setting", "collaborator", "workflow"):
            self.assertIn(verb, description)
        self.assertRegex(description, r"It MUST NOT be skipped")
        self.assertNotRegex(description, r"\b(you|your|I|we)\b")

    def test_the_body_carries_the_rule_and_where_it_stops(self):
        """REQ-2576, REQ-2722: asked, never made, and a person answers."""
        flat = " ".join(self.text.split())
        self.assertIn("<role>", flat)
        self.assertRegex(flat, r"- G\d+\. [^.]*unless (a person )?(asked|asks)")
        self.assertRegex(flat, r"never answer[^.]*for the person|answers? through the platform")
        self.assertRegex(flat, r"because")

    def test_the_budget_counts_the_description(self):
        """REQ-1056: the unit's budget states what its description loads."""
        budget = (UNIT / "budget.toml").read_text(encoding="utf-8")
        ceiling = int(re.search(r"^permanent_characters\s*=\s*(\d+)", budget, re.M).group(1))
        self.assertGreaterEqual(ceiling, len(self.fields["description"]))
        manifest = json.loads((UNIT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn(f"{ceiling:,} characters", manifest["description"])


if __name__ == "__main__":
    unittest.main()
