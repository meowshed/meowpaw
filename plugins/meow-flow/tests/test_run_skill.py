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


STEPS = Path(__file__).resolve().parent.parent / "skills" / "method" / "steps"


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def in_a_run():
    """The run skill's steps for a run, without the attended steps and the rules."""
    start = FLAT.index('<steps name="in a run">')
    return FLAT[start:FLAT.index("</steps>", start)]


class EpicOnOneBranch(unittest.TestCase):
    """TSK-5360: the prompts that drive the chain carry an epic's tasks on its one branch."""

    def test_a_run_opens_one_pull_request_for_an_epic_and_merges_at_its_last_task(self):
        """TSK-5360 criterion 1, REQ-4400, REQ-4414: the merge waits for the epic, not for a task."""
        steps = in_a_run()
        self.assertRegex(steps, r"epic's (one )?(branch|pull request)")
        self.assertRegex(steps, r"next task of the epic[^.]{0,120}same branch")
        self.assertRegex(steps, r"merge the pull request only once[^.]{0,120}is closed")
        self.assertNotRegex(steps, r"open the pull request and merge it once")

    def test_a_defect_or_a_task_that_realises_a_decision_keeps_its_own_pull_request(self):
        """TSK-5360 criterion 1, REQ-4402, REQ-4404: the merge condition names the record the pull request carries."""
        steps = in_a_run()
        self.assertRegex(steps, r"defect's")
        self.assertRegex(steps, r"realises")

    def test_the_implement_step_goes_on_to_the_epics_next_task(self):
        """TSK-5360 criterion 2, REQ-4410, REQ-4414: marking a task is not where the step stops."""
        text = flat(STEPS / "implement.md")
        self.assertRegex(text, r"next task of (the|its) epic[^.]{0,160}same branch")
        self.assertRegex(text, r"stop at the epic's pull request")
        self.assertNotRegex(text, r"and stop there\.")

    def test_the_review_step_reads_an_epics_pull_request(self):
        """TSK-5360 criterion 3, REQ-4400: a task has no review of its own."""
        text = flat(STEPS / "review.md")
        role = text[: text.index("</role>")]
        self.assertRegex(role, r"epic's pull request")
        self.assertNotRegex(role, r"task's pull request")
        self.assertRegex(text, r"what the tasks in it ask")
        self.assertRegex(text, r"unmark the task whose stage failed")

    def test_no_prompt_gives_a_task_a_branch_a_pull_request_or_a_review_of_its_own(self):
        """TSK-5360 criterion 3, REQ-4400: the wording that attached them is gone from the shipped prompts."""
        unit = Path(__file__).resolve().parent.parent
        files = [unit / "skills" / "run" / "SKILL.md", unit / "lib" / "layout.toml", unit / "README.md"]
        files += sorted((unit / "skills" / "method").rglob("*.md"))
        files += [unit.parent / "meow-prose" / "skills" / "writing" / "types" / "record" / "task.md"]
        pattern = re.compile(
            r"\b(?:a|each|every|its|the) task's (?:own )?(?:branch|pull request|review)\b|\bits own pull request\b"
            r"|\bone task, one branch\b",
            re.IGNORECASE,
        )
        found = {}
        for path in files:
            hits = pattern.findall(re.sub(r"\s+", " ", path.read_text(encoding="utf-8")))
            if hits:
                found[path.name] = hits
        self.assertEqual(found, {}, "a prompt attaches a branch, a pull request or a review to a task")

    def test_the_layout_copies_agree(self):
        """TSK-5360: the reason a retired Cover section prints names the epic's pull request."""
        unit = Path(__file__).resolve().parent.parent
        text = (unit / "lib" / "layout.toml").read_text(encoding="utf-8")
        self.assertIn("commit of their own in the epic's pull request", text)

    def test_the_method_description_attaches_no_pull_request_to_a_task(self):
        """TSK-5360 criterion 3, REQ-4400: the description the model chooses by."""
        head = (STEPS.parent / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        self.assertNotRegex(head, r"its pull request")


if __name__ == "__main__":
    unittest.main()
