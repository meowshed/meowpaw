# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures that read what the implement step says about delegating a task (TSK-4950, TSK-5175, SPC-1030
"Delegation", SPC-1090 "Delegated work").

A step is text a model follows, so each fixture reads the step for the instruction a requirement asks of it.
Whether a model follows it is measured by the hand-run case in `evals/`.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
ROOT = UNIT.parent.parent
STEP = UNIT / "skills" / "method" / "steps" / "implement.md"
PI_STEP = ROOT / "packages" / "meow-flow" / "skills" / "method" / "steps" / "implement.md"
TEXT = STEP.read_text(encoding="utf-8")
FLAT = re.sub(r"\s+", " ", TEXT)
SCM = ROOT / "plugins" / "meow-scm" / "bin" / "meow-scm"


def rule(text, requirement):
    """The rule naming `requirement`, flattened, or an empty string where none does."""
    for item in re.split(r"\n- (?=I\d+\.)", text):
        if requirement in item:
            return re.sub(r"\s+", " ", item)
    return ""


class Delegation(unittest.TestCase):
    def test_two_reasons_to_delegate_and_never_because_a_task_is_large(self):
        """TSK-4950 criterion 1, REQ-0826, REQ-0828: context kept clean or independent tracks, never size."""
        reasons = rule(TEXT, "REQ-0826")
        self.assertRegex(reasons, r"keep (this|a|the) context clean")
        self.assertRegex(reasons, r"independent tracks")
        self.assertRegex(rule(TEXT, "REQ-0828"), r"never because (the|a) task is large")

    def test_a_parallel_dispatch_declares_a_worktree_and_carries_the_brief(self):
        """TSK-4950 criterion 2, REQ-2980, REQ-0810: `isolation: worktree`, and `paw brief <task>`'s output."""
        isolation = rule(TEXT, "REQ-2980")
        self.assertIn("isolation: worktree", isolation)
        self.assertRegex(isolation, r"parallel")
        self.assertRegex(rule(TEXT, "REQ-0810"), r"output of `paw brief <task>`")

    def test_review_is_a_fresh_agent_and_a_disagreement_goes_to_a_third(self):
        """TSK-4950 criterion 3, REQ-0818, REQ-0824: what the step tells the dispatcher; the hand-run case in
        `evals/delegation.py` measures whether a model does it."""
        review = rule(TEXT, "REQ-0818")
        self.assertRegex(review, r"fresh agent")
        self.assertRegex(review, r"never fork")
        third = rule(TEXT, "REQ-0824")
        self.assertRegex(third, r"third fresh agent")
        self.assertRegex(third, r"both positions and the brief")

    def test_a_delegated_pull_request_names_the_task_and_the_brief_and_no_agent(self):
        """TSK-4950 criterion 4, TSK-5175, REQ-1764, REQ-1294: the task and `paw brief <task>`, and no agent,
        model or vendor."""
        pull_request = rule(TEXT, "REQ-1764")
        self.assertRegex(pull_request, r"pull request")
        self.assertIn("`paw brief <task>`", pull_request)
        self.assertRegex(pull_request, r"no agent, model or vendor")
        for word in ("claude", "anthropic", "opus", "sonnet", "haiku", "co-authored-by", "generated with"):
            self.assertNotIn(word, FLAT.lower())

    def test_the_steps_example_passes_the_message_check(self):
        """TSK-4950 criterion 4, TSK-5175, REQ-1294: the delegated pull request's example meets the convention
        and carries no attribution."""
        examples = re.findall(r"<example>\n(.*?)</example>", TEXT, re.S)
        delegated = [e for e in examples if "paw brief" in e]
        self.assertEqual(len(delegated), 1, "the step carries no example of a delegated pull request")
        fences = re.findall(r"```text\n(.*?)```", delegated[0], re.S)
        messages = [f for f in fences if "paw brief" in f]
        self.assertEqual(len(messages), 1, "the example holds no corrected message in a text fence")
        message = messages[0]
        self.assertRegex(message, r"TSK-\d{4}")
        self.assertRegex(message, r"paw brief TSK-\d{4}")
        # The first sign-off names the commit's author, so the check runs as the person the example names.
        author = {"GIT_AUTHOR_NAME": "A Person", "GIT_AUTHOR_EMAIL": "person@example.com"}
        done = subprocess.run([str(SCM), "check-message"], input=message, cwd=ROOT, capture_output=True, text=True,
                              env={**os.environ, **author})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_the_pi_step_says_the_same(self):
        """Constitution `claude_pi_parity`: the step is the same text in both trees."""
        self.assertEqual(PI_STEP.read_text(encoding="utf-8"), TEXT)


if __name__ == "__main__":
    unittest.main()
