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
        self.assertIn("Run `${CLAUDE_SKILL_DIR}/../../bin/paw status --brief` and show its output.", TEXT)
        self.assertIn("Stop where that step ends at an approval gate.", TEXT)


STEPS = Path(__file__).resolve().parent.parent / "skills" / "method" / "steps"


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def in_a_run():
    """The run skill's steps for a run, without the attended steps and the rules."""
    start = FLAT.index('<steps name="in a run">')
    return FLAT[start:FLAT.index("</steps>", start)]


class OneRecordOnOneBranch(unittest.TestCase):
    """ADR-3090: the prompts that drive the chain carry a record's plan on its one branch."""

    def test_a_run_opens_one_pull_request_for_a_record_and_merges_once_it_is_closed(self):
        """ADR-3090, REQ-3668: the merge waits for the record's whole plan."""
        steps = in_a_run()
        self.assertRegex(steps, r"record's one branch, in its one pull request")
        self.assertRegex(steps, r"open the pull request once")
        self.assertRegex(steps, r"record's plan on the same branch")
        self.assertRegex(steps, r"merge the pull request only once[^.]{0,120}closed")
        self.assertNotRegex(steps, r"open the pull request and merge it once")

    def test_the_implement_step_goes_on_to_the_next_plan_step(self):
        """ADR-3090, REQ-3682: finishing a plan step is not where the step stops."""
        text = flat(STEPS / "implement.md")
        self.assertRegex(text, r"next plan step on the same branch")
        self.assertRegex(text, r"Stop at that pull request")
        self.assertNotRegex(text, r"and stop there\.")

    def test_the_review_step_reads_a_records_pull_request(self):
        """ADR-3090, REQ-3668: the review reads the one pull request of a decision or a defect."""
        text = flat(STEPS / "review.md")
        role = text[: text.index("</role>")]
        self.assertRegex(role, r"pull request of a decision or a defect")
        self.assertNotRegex(text, r"task's pull request|epic's pull request")
        self.assertRegex(text, r"what the record's plan asks")
        self.assertRegex(text, r"put the record back to `approved`, remove its `pr:`")

    def test_no_prompt_keeps_the_retired_epic_or_task_step(self):
        """ADR-3090, REQ-3666: the wording of the retired decomposition is gone from the shipped prompts."""
        unit = Path(__file__).resolve().parent.parent
        files = [unit / "skills" / "run" / "SKILL.md", unit / "lib" / "layout.toml"]
        files += sorted((unit / "skills" / "method").rglob("*.md"))
        pattern = re.compile(r"\b(?:a|each|every|its|the) task's (?:own )?(?:branch|pull request|review)\b"
                             r"|\bone task, one branch\b|\bnext task of\b|\bthe epic's\b", re.IGNORECASE)
        found = {}
        for path in files:
            hits = pattern.findall(re.sub(r"\s+", " ", path.read_text(encoding="utf-8")))
            if hits:
                found[path.name] = hits
        self.assertEqual(found, {}, "a prompt keeps a retired step")
        self.assertFalse((STEPS / "epic.md").exists())

    def test_the_layout_names_the_pull_request(self):
        """ADR-3090: the reason a retired Cover section prints names the pull request."""
        unit = Path(__file__).resolve().parent.parent
        text = (unit / "lib" / "layout.toml").read_text(encoding="utf-8")
        self.assertIn("commit of their own in the pull request", text)

    def test_the_method_description_attaches_no_pull_request_to_a_task(self):
        """TSK-5360 criterion 3, REQ-4400: the description the model chooses by."""
        head = (STEPS.parent / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        self.assertNotRegex(head, r"its pull request")


if __name__ == "__main__":
    unittest.main()


class Invocable(unittest.TestCase):
    """ADR-2900, REQ-4900: the model may invoke the driver, and the loop stays person-only."""

    def test_the_driver_is_invokable_and_the_loop_is_not(self):
        """ADR-2900 criterion 1, REQ-4900: the run skill carries no `disable-model-invocation`, and the loop's does."""
        run = Path(__file__).resolve().parent.parent / "skills" / "run" / "SKILL.md"
        loop = run.parent.parent.parent.parent / "meow-loop" / "skills" / "run" / "SKILL.md"
        self.assertNotIn("disable-model-invocation", run.read_text(encoding="utf-8"))
        self.assertIn("disable-model-invocation: true", loop.read_text(encoding="utf-8"))
