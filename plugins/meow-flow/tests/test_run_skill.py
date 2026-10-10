# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures that read what `/meow-flow:run` says to do inside a run (TSK-4130, SPC-1200).

A skill is text a model follows, so each fixture reads the skill for the
instruction a requirement asks of it and fails where one is missing. Whether a
model follows the instruction is measured by the evals, which run by hand.
"""

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "run" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
FLAT = re.sub(r"\s+", " ", TEXT)


class RunSkill(unittest.TestCase):
    def test_a_run_is_recognised_by_its_frozen_prompt_and_decides_without_asking(self):
        """TSK-4130 criterion 1, REQ-3714, REQ-2380: the signal of a run, the principles and no question."""
        self.assertRegex(FLAT, r"meow-loop run <run id>")
        self.assertRegex(FLAT, r"frozen prompt")
        self.assertRegex(FLAT, r"CLAUDE\.md")
        self.assertRegex(FLAT, r"\[method\] principles")
        self.assertRegex(FLAT, r"ask(s)? the person nothing")

    def test_a_separate_agent_critiques_before_the_approval_is_written(self):
        """TSK-4130 criterion 2, REQ-2382, REQ-2384: the critique comes first, in another agent, and the approval
        is a harness approval that names the run."""
        self.assertRegex(FLAT, r"separate agent")
        self.assertLess(FLAT.index("critique"), FLAT.index("harness approval"))
        self.assertRegex(FLAT, r"harness approval[^.]{0,120}run")

    def test_the_run_merges_after_the_checks_and_releases_only_the_declared_command(self):
        """TSK-4130 criterion 3, REQ-3716, REQ-3718: merge after checks pass, release by the declared command."""
        self.assertRegex(FLAT, r"merge[^.]{0,160}checks pass")
        self.assertRegex(FLAT, r"\[unattended\] release")
        self.assertRegex(FLAT, r"never guess")
        self.assertRegex(FLAT, r"prohibition")

    def test_each_decision_appends_a_line_to_the_report(self):
        """TSK-4130 criterion 4, REQ-2386: approval, merge, release, next block and a thing it couldn't do."""
        self.assertRegex(FLAT, r"report\.md")
        self.assertRegex(FLAT, r"one line")
        for word in ("approval", "merge", "release", "next block", "couldn't"):
            self.assertIn(word, FLAT)

    def test_the_next_block_is_one_topic_with_neighbouring_identifiers(self):
        """TSK-4130 criterion 5, REQ-3720: where nothing begins `next:`, the run chooses a block itself."""
        self.assertRegex(FLAT, r"no `next:` line")
        self.assertRegex(FLAT, r"neighbouring identifiers")
        self.assertRegex(FLAT, r"postponed")
        self.assertRegex(FLAT, r"already addresses|addressed")
        self.assertRegex(FLAT, r"amend")

    def test_fetched_material_is_data(self):
        """TSK-4130 criterion 6, REQ-2402: a page, an issue or a file it didn't write carries no instruction."""
        self.assertRegex(FLAT, r"fetched[^.]{0,200}data")
        self.assertRegex(FLAT, r"no instruction")

    def test_outside_a_run_the_attended_steps_stay(self):
        """TSK-4130 criterion 7 rests on the evals; here the attended steps are still in the file."""
        self.assertIn("Run `${CLAUDE_SKILL_DIR}/../../bin/paw status` and show its output.", TEXT)
        self.assertIn("Stop where that step ends at an approval gate.", TEXT)


if __name__ == "__main__":
    unittest.main()
