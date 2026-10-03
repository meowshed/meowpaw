# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""What `tools/loop.py` reports and refuses, as ADR-1500 decides, tested with
no model call so the `test` verb can run it."""

import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop  # noqa: E402


class Labels(unittest.TestCase):
    """REQ-3022: a case is kept only where it separates the arms."""

    def test_an_interval_within_the_margin_of_zero_is_deleted(self):
        self.assertEqual(loop.label(0.02, 0.02), "delete: scores the same without the unit")

    def test_an_interval_clearing_zero_separates(self):
        self.assertEqual(loop.label(0.6, 0.1), "separates")
        self.assertEqual(loop.label(-0.6, 0.1), "separates")

    def test_a_wide_interval_is_undetermined(self):
        self.assertEqual(loop.label(0.1, 0.2), "undetermined: run more")

    def test_no_arm_without_the_unit_is_said(self):
        self.assertEqual(loop.label(float("nan"), 0.0), "no arm without the unit")


class Rates(unittest.TestCase):
    """REQ-0160, REQ-3026: every rate carries its error and its run count."""

    def test_a_rate_carries_its_error_and_count(self):
        p, se, n = loop.rate([True, True, False, True])
        self.assertEqual((p, n), (0.75, 4))
        self.assertAlmostEqual(se, math.sqrt(0.75 * 0.25 / 4))

    def test_two_arms_give_a_delta_with_the_combined_error(self):
        c = loop.compare([True] * 5, [False] * 5)
        self.assertEqual((c["with"], c["without"], c["delta"], c["runs"]), (1.0, 0.0, 1.0, 5))
        self.assertEqual(c["label"], "separates")

    def test_the_case_table_prints_the_runs_error_and_label(self):
        base = {"model": "m", "cases": {"a-case": loop.compare([True] * 5, [True] * 5)}}
        row = loop.per_case(base, {"a-case": 0.66})[-1]
        self.assertIn("| a-case | 5 | 1.00 | 1.00 | +0.00 | 0.00 | 0.66 | yes | delete", row)


class Judge(unittest.TestCase):
    """REQ-0160, REQ-3026, REQ-3028: the header names the judge, its family and what the result supports."""

    def test_the_family_comes_from_the_identifier(self):
        self.assertEqual(loop.family("claude-opus-5-5"), "claude")
        self.assertEqual(loop.family("gpt-6"), "gpt")

    def test_a_same_family_judge_makes_a_smoke_check(self):
        text = " ".join(loop.judge_line("claude-opus-5-5", ["claude-sonnet-5"], 5))
        self.assertIn("of the claude family", text)
        self.assertIn("smoke check", text)
        self.assertNotIn("supports no claim", text)

    def test_another_family_is_still_no_claim(self):
        text = " ".join(loop.judge_line("gpt-6", ["claude-sonnet-5"], 5))
        self.assertIn("no smoke check by family, and still no claim", text)

    def test_the_judge_as_a_candidate_is_said(self):
        text = " ".join(loop.judge_line("claude-opus-5-5", ["claude-opus-5-5"], 5))
        self.assertIn("also a candidate model", text)

    def test_three_runs_support_no_claim(self):
        self.assertIn("3 runs per arm supports no claim (REQ-3026).", loop.judge_line("claude-opus-5-5", ["claude-sonnet-5"], 3))


class Verdicts(unittest.TestCase):
    """REQ-0159: what counts is stated before the run."""

    def row(self, delta, se, tokens):
        return {"delta": delta, "se": se, "tokens": tokens}

    def test_a_candidate_lands_only_within_twice_the_combined_error(self):
        base = self.row(0.5, 0.05, 100)
        self.assertEqual(loop.verdict(base, self.row(0.40, 0.05, 90)), "lands")
        self.assertTrue(loop.verdict(base, self.row(0.30, 0.05, 90)).startswith("loses: delta fell"))

    def test_a_case_below_its_threshold_does_not_meet_it(self):
        self.assertEqual(loop.meets(0.5, 0.66), "no")
        self.assertEqual(loop.meets(0.8, 0.66), "yes")

    def test_a_case_with_no_threshold_gets_no_verdict(self):
        self.assertEqual(loop.meets(1.0, None), "no threshold set before the run")


class Cases(unittest.TestCase):
    """REQ-3752: a unit whose `evals/` holds only a hand run has no case to measure."""

    def unit(self, *files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name in files:
            path = root / "evals" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        return root

    def test_a_hand_run_alone_is_no_case(self):
        self.assertFalse(loop.has_cases(self.unit("hand_run.py")))

    def test_a_prompt_is_a_case(self):
        self.assertTrue(loop.has_cases(self.unit("a-case/prompt.md")))

    def test_a_case_file_at_any_depth_is_a_case(self):
        self.assertTrue(loop.has_cases(self.unit("group/a-case/case.yaml")))

    def test_the_loop_skips_a_unit_with_no_case(self):
        unit = self.unit("hand_run.py")
        done = subprocess.run([sys.executable, str(Path(loop.__file__)), str(unit)],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("no eval case, nothing to measure", done.stdout)
        self.assertFalse((unit / "evals" / "results").exists())


class Refusals(unittest.TestCase):
    """REQ-0159, REQ-0153: the loop refuses what it can't hold."""

    def unit(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        run = lambda *a: subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b", *a],
                                        cwd=root, check=True, capture_output=True, env=env)
        run("init", "-q", "-b", "work")
        (root / "evals" / "a-case" / "graders").mkdir(parents=True)
        (root / "evals" / "thresholds.toml").write_text("[cases]\na-case = 0.66\n", encoding="utf-8")
        run("add", "-A")
        run("commit", "-q", "-m", "c")
        return root

    def test_committed_thresholds_are_named_with_their_commit(self):
        commit, refusal = loop.threshold_commit(self.unit())
        self.assertIsNone(refusal)
        self.assertRegex(commit, r"^[0-9a-f]{7,} \d{4}-\d{2}-\d{2}T")

    def test_thresholds_differing_from_the_last_commit_are_refused(self):
        root = self.unit()
        (root / "evals" / "thresholds.toml").write_text("[cases]\na-case = 0.5\n", encoding="utf-8")
        commit, refusal = loop.threshold_commit(root)
        self.assertIsNone(commit)
        self.assertIn("differs from the last commit", refusal)

    def test_a_baseline_grader_is_refused(self):
        root = self.unit()
        (root / "evals" / "a-case" / "graders" / "compare.md").write_text(
            "---\ntype: baseline\nbaseline_file: expected.md\n---\n\nCompare.\n", encoding="utf-8")
        (root / "evals" / "a-case" / "graders" / "judge.md").write_text(
            "---\ntype: llm\nfocus: last_message\n---\n\nJudge.\n", encoding="utf-8")
        self.assertEqual([g.name for g in loop.baseline_graders(root)], ["compare.md"])


if __name__ == "__main__":
    unittest.main()
