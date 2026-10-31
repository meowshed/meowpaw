# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures that read the prompts and the vision SPC-1220 and SPC-1230 state (TSK-4710, TSK-4740, TSK-4760).

A prompt is text a model follows, so each fixture reads it for the instruction a requirement asks of it. Whether a
model follows it rests on review, because ADR-2980 keeps no case set.
"""

import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
ROOT = UNIT.parent.parent
TREES = {"Claude": UNIT, "Pi": ROOT / "packages" / "meow-flow"}
STEPS = ("research", "requirements", "design", "spec", "implement", "review")


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class Constitution(unittest.TestCase):
    def test_the_template_names_no_step_and_quotes_no_method_rule(self):
        """TSK-4710 criterion 1, REQ-2740: the constitution template carries none of the seven steps."""
        for tree, unit in TREES.items():
            text = (unit / "templates" / "constitution.md").read_text(encoding="utf-8")
            for step in STEPS:
                self.assertIsNone(re.search(rf"\b{step}\b", text, re.I), f"{tree}: names the step {step}")
            self.assertIsNone(re.search(r"\bM\d+\.", text), f"{tree}: quotes a rule of the method skill")

    def test_init_copies_nothing_of_the_method_into_the_constitution(self):
        """TSK-4710 criterion 2, REQ-2740: init writes CLAUDE.md from the template and the repository's own files."""
        for tree, unit in TREES.items():
            text = flat(unit / "skills" / "init" / "SKILL.md")
            self.assertRegex(text, r"template", tree)
            self.assertRegex(text, r"(copy|copies) nothing (of|from) the method", f"{tree}: no ban on copying")
            self.assertRegex(text, r"because", tree)

    def test_the_design_step_asks_whether_a_constitution_rule_pulls_against_another(self):
        """TSK-4710 criterion 3, REQ-2738: two rules that pull against each other become one with its exception."""
        for tree, unit in TREES.items():
            text = flat(unit / "skills" / "method" / "steps" / "design.md")
            self.assertRegex(text, r"adds a rule to the constitution", tree)
            self.assertRegex(text, r"pulls against", tree)
            self.assertRegex(text, r"one rule with its exception", tree)


class Vision(unittest.TestCase):
    def headings(self):
        text = (ROOT / "project" / "vision.md").read_text(encoding="utf-8")
        return re.findall(r"^## (.+)$", text, re.M), text

    def test_the_vision_carries_the_four_required_sections(self):
        """TSK-4740 criterion 1, REQ-2850, REQ-2854: the four sections SPC-1230 requires, in the template's order."""
        headings, _ = self.headings()
        for section in ("Who it is for", "Quality goals", "What it will not do", "Risks"):
            self.assertIn(section, headings)
        self.assertLess(headings.index("Quality goals"), headings.index("What it will not do"))
        self.assertLess(headings.index("What it will not do"), headings.index("Risks"))

    def test_the_vision_is_within_two_thousand_words_and_holds_no_date(self):
        """TSK-4740 criterion 4, REQ-0611, REQ-2856: at most 2,000 words outside fenced code, and no date."""
        _, text = self.headings()
        body = text.split("\n---\n", 1)[1]
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        self.assertLessEqual(len(body.split()), 2000)
        self.assertIsNone(re.search(r"\b\d{4}-\d{2}-\d{2}\b|\bQ[1-4] \d{4}\b", body))
        self.assertIsNone(re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", body))

    def test_the_vision_states_no_requirement_as_an_obligation(self):
        """TSK-4740 criterion 3, REQ-2857: no requirement identifier in the body."""
        _, text = self.headings()
        self.assertIsNone(re.search(r"\bREQ-\d+", text.split("\n---\n", 1)[1]))


class VisionQuestions(unittest.TestCase):
    def test_the_design_step_asks_for_a_requirement_behind_each_claim(self):
        """TSK-4760 criterion 1, REQ-2852: a claim with no requirement making it falsifiable is removed."""
        for tree, unit in TREES.items():
            text = flat(unit / "skills" / "method" / "steps" / "design.md")
            self.assertRegex(text, r"changes the vision", tree)
            self.assertRegex(text, r"falsifiable", tree)
            self.assertRegex(text, r"remove a claim with no requirement", tree)

    def test_a_contradiction_stops_the_step_without_writing_the_decision(self):
        """TSK-4760 criterion 2, REQ-0624: report one of the two as stale, ask which, write no decision."""
        for tree, unit in TREES.items():
            text = flat(unit / "skills" / "method" / "steps" / "design.md")
            self.assertRegex(text, r"contradicts the vision", tree)
            self.assertRegex(text, r"one of the two is stale", tree)
            self.assertRegex(text, r"ask which", tree)
            self.assertRegex(text, r"writes no decision", tree)


if __name__ == "__main__":
    unittest.main()
