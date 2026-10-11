# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The kernel's output style states the secrets rule (TSK-4935, REQ-1424)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLE = ROOT / "plugins" / "meow-core" / "output-styles" / "meow.md"


class SecretsRule(unittest.TestCase):
    def setUp(self):
        self.text = " ".join(STYLE.read_text(encoding="utf-8").split())

    def rule(self):
        found = re.search(r"- R\d+\. ([^-]*?secret[^-]*?)(?= - R\d+\. |</rules>)", self.text)
        self.assertIsNotNone(found, "the style carries no rule about secret material")
        return found.group(1)

    def test_the_rule_states_the_four_prohibitions(self):
        """TSK-4935 criterion 1, REQ-1424: never read, never print, never transmit, never place in an artifact."""
        rule = self.rule()
        for word in ("read", "print", "transmit", "artifact"):
            self.assertRegex(rule, rf"\b{word}\b", f"the rule names no `{word}`: {rule}")
        self.assertRegex(rule, r"Never read, print or transmit", "the rule names no prohibition of the three")
        self.assertRegex(rule, r"never place it in", "the rule names no prohibition of the fourth")
        self.assertRegex(rule, r"because", "the rule carries no reason")
        self.assertRegex(rule, r"It never yields\.\s*$", "the rule yields")


if __name__ == "__main__":
    unittest.main()
