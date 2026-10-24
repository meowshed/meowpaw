# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures that read what the method skill says about an insight (TSK-4960, SPC-1090 "Insights").

A skill is text a model follows, so each fixture reads the skill for the
instruction a requirement asks of it. Whether a model follows it is measured
by the evals, which run by hand.
"""

import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent


def rule(path, name):
    text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
    found = re.search(rf"- {name}\. (.*?)(?= - [A-Z]\d+\. |</rules>)", text)
    if found is None:
        raise AssertionError(f"{path} has no rule {name}")
    return found.group(1)


class InsightRule(unittest.TestCase):
    def test_the_model_writes_an_insight_as_a_draft_with_no_prompt(self):
        """TSK-4960 criterion 2, REQ-2142: M11 says the model writes the draft unprompted."""
        for tree in (UNIT,):
            said = rule(tree / "skills" / "method" / "SKILL.md", "M11")
            self.assertRegex(said, r"\bmodel\b", tree)
            self.assertRegex(said, r"\bdraft\b", tree)
            self.assertRegex(said, r"no person's prompt", tree)
            self.assertRegex(said, r"holds past its case", tree)


if __name__ == "__main__":
    unittest.main()
