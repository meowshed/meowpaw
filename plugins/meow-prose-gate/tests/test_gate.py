# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1010 states `meow-prose-gate check` blocks.

Each fixture feeds the launcher the JSON Claude Code passes a `PreToolUse`
hook and reads the exit status and standard error. A block must quote a span
found verbatim in the command (REQ-3183), and the program holds only the
three exact rules (REQ-3187). The four false blocks BUG-1230 records are
among the texts that must pass. `MEOW_PROSE_GATE_BIN` names the launcher to
test, so the fixtures can run against another build.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_PROSE_GATE_BIN", UNIT / "bin" / "meow-prose-gate"))
FINDING = re.compile(r'^(P[123]) \| "(.*)" \| (.+)$')


def gate(command):
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    return subprocess.run([str(BIN), "check"], input=json.dumps(event), capture_output=True, text=True, timeout=30)


def pr(body):
    return 'gh pr create --title "Bind the verbs to the crate" --body "' + body + '"'


class FalseBlocksFromBug1230(unittest.TestCase):
    """REQ-1756: the four bodies BUG-1230 records, each once blocked for a finding it didn't hold."""

    def assert_passes(self, command):
        done = gate(command)
        self.assertEqual((done.returncode, done.stderr, done.stdout), (0, "", ""), command)

    def test_a_body_with_no_bold_passes_p2(self):
        self.assert_passes(pr(
            "The verbs now run through the crate, so a repository without Python still gets them.\n\n"
            "Each verb resolves from the profile, and an undeclared one reports unresolved.\n\n"
            "Closes #12"))

    def test_a_body_without_deep_dive_passes_p1(self):
        self.assert_passes(pr(
            "I read the parser in depth and found two defects in how it reads a heredoc.\n\n"
            "Both are fixed here, each with a fixture seen failing first."))

    def test_look_and_gate_passes_are_off_the_list(self):
        self.assert_passes(pr(
            "Look at the fixtures first: they hold the four cases the defect records.\n\n"
            "The gate passes on this tree, and `mise run all` exits 0."))

    def test_plain_paragraphs_pass_p2(self):
        self.assert_passes(pr(
            "This change replaces the prompt hook with a program.\n\n"
            "The program reads the command, takes the text from its arguments and checks three rules.\n\n"
            "Nothing else changes for a repository that installs the unit."))


class TruePositives(unittest.TestCase):
    """REQ-3183 and REQ-3187: one block per rule, each quoting a span found verbatim."""

    def assert_blocks(self, command, rule, span):
        done = gate(command)
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        findings = [FINDING.match(line) for line in done.stderr.splitlines() if line.strip()]
        self.assertTrue(findings and all(findings), done.stderr)
        self.assertIn((rule, span), [(f.group(1), f.group(2)) for f in findings])
        for found in findings:
            self.assertIn(found.group(2), command, "a quoted span must occur verbatim in the command")

    def test_p1_an_idiom_from_the_list(self):
        self.assert_blocks(
            'git commit --allow-empty -m "Cache rendered pages" -m "Caching is the low-hanging fruit here, '
            'so the server skips the template step on a repeat request."',
            "P1", "low-hanging fruit")

    def test_p1_an_idiom_split_across_lines_is_quoted_as_written(self):
        self.assert_blocks(
            'git commit -m "Cache pages" -m "This change gets\nunder the hood of the renderer."',
            "P1", "under the hood")

    def test_p2_a_line_holding_only_bold_text(self):
        self.assert_blocks(
            'gh issue create --repo meowpaw-eval/none --title "Retries drop the batch silently" --body "**Why.**\n\n'
            'The worker retries five times and then drops the batch without logging it."',
            "P2", "**Why.**")

    def test_p3_a_body_hidden_in_a_file(self):
        self.assert_blocks(
            'gh pr create --repo meowpaw-eval/none --title "Cache rendered pages" --body-file body.md',
            "P3", "body.md")

    def test_p3_a_commit_message_hidden_in_a_file(self):
        self.assert_blocks("git commit --allow-empty -F notes.txt", "P3", "notes.txt")

    def test_p3_a_substitution_reading_a_file(self):
        self.assert_blocks('gh pr create --title "Cache" --body "$(cat notes.md)"', "P3", "notes.md")


# One blocking command for each `if` pattern in hooks/hooks.json, keyed by the
# command the pattern names, so a pattern with no fixture fails `TheHook`.
GATED = {
    "git commit": ('git commit -m "Cache pages" -m "Caching is the low-hanging fruit here."', "P1", "low-hanging fruit"),
    "gh pr create": ('gh pr create --title "Cache pages" --body "a silver bullet for slow pages"', "P1", "silver bullet"),
    "gh issue create": ('gh issue create --title "Slow pages" --body "**Why.**\n\nThe server renders twice."', "P2", "**Why.**"),
    "gh pr edit": ('gh pr edit 5 --body "This is no silver bullet for slow pages."', "P1", "silver bullet"),
    "gh pr comment": ('gh pr comment 5 --body "Let us circle back after the release."', "P1", "circle back"),
    "gh pr review": ('gh pr review 5 --comment -b "A deep dive into the cache shows two misses."', "P1", "deep dive"),
    "gh issue edit": ('gh issue edit 7 --body "__Steps__:\n\nRun the server twice."', "P2", "__Steps__:"),
    "gh issue comment": ('gh issue comment 7 -b "The retry is under the hood of the worker."', "P1", "under the hood"),
    "gh release create": ('gh release create v1.2.0 --title "1.2.0" --notes "Caching was the low-hanging fruit."', "P1", "low-hanging fruit"),
    "gh release edit": ('gh release edit v1.2.0 -n "A game changer for slow pages."', "P1", "game changer"),
}


class EveryGatedCommand(unittest.TestCase):
    """REQ-3182: the gate holds a text back in each command the hook routes, and in each argument it reads."""

    def assert_blocks(self, command, rule, span):
        TruePositives.assert_blocks(self, command, rule, span)

    def test_git_commit(self):
        self.assert_blocks(*GATED["git commit"])

    def test_gh_pr_create(self):
        self.assert_blocks(*GATED["gh pr create"])

    def test_gh_issue_create(self):
        self.assert_blocks(*GATED["gh issue create"])

    def test_gh_pr_edit(self):
        self.assert_blocks(*GATED["gh pr edit"])

    def test_gh_pr_comment(self):
        self.assert_blocks(*GATED["gh pr comment"])

    def test_gh_pr_review(self):
        self.assert_blocks(*GATED["gh pr review"])

    def test_gh_issue_edit(self):
        self.assert_blocks(*GATED["gh issue edit"])

    def test_gh_issue_comment(self):
        self.assert_blocks(*GATED["gh issue comment"])

    def test_gh_release_create(self):
        self.assert_blocks(*GATED["gh release create"])

    def test_gh_release_edit(self):
        self.assert_blocks(*GATED["gh release edit"])

    def test_release_notes_hidden_in_a_file(self):
        self.assert_blocks('gh release create v1.2.0 --notes-file notes.md', "P3", "notes.md")


class ReadableTexts(unittest.TestCase):
    """REQ-1756: forms the program reads, and text the rules leave alone, pass."""

    def assert_passes(self, command):
        done = gate(command)
        self.assertEqual((done.returncode, done.stderr, done.stdout), (0, "", ""), command)

    def test_a_heredoc_on_standard_input(self):
        self.assert_passes(
            "git commit --allow-empty -F - <<'MSG'\nCache rendered pages\n\n"
            "The server skips the template step on a repeat request.\nMSG")

    def test_a_heredoc_inside_a_substitution(self):
        self.assert_passes(
            'git commit -m "$(cat <<\'EOF\'\nCache rendered pages\n\nThe server skips the template step.\nEOF\n)"')

    def test_an_idiom_inside_code_passes(self):
        self.assert_passes(pr(
            "The skill lists `under the hood` as an idiom to avoid.\n\n"
            "```text\nlow-hanging fruit\n**Why.**\n```\n\nNothing else changed."))

    def test_an_idiom_in_a_url_or_a_path_passes(self):
        self.assert_passes(pr(
            "The notes are at https://example.com/deep-dive and in plugins/deep-dive/rule-of-thumb.md now."))

    def test_the_rules_the_gate_left_to_the_reviewer(self):
        self.assert_passes(
            'git commit --allow-empty -m "Normalize the retry behavior" -m "The worker moves a batch to the DLQ '
            'after the third failed attempt."')

    def test_a_bold_opener_with_text_after_it(self):
        self.assert_passes(pr("**Note:** the verbs run through the crate now."))

    def test_an_idiom_in_a_command_that_publishes_nothing(self):
        self.assert_passes('git commit -m "Cache pages" && grep -c "low-hanging fruit" notes.txt')


class TheHook(unittest.TestCase):
    """ADR-1600: no model judges a publish, and a missing binary blocks nothing."""

    def test_a_launcher_with_no_binary_lets_the_publish_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "meow-prose-gate"
            shutil.copy(UNIT / "bin" / "meow-prose-gate", launcher)
            event = json.dumps({"tool_input": {"command": 'git commit -m "a silver bullet"'}})
            done = subprocess.run(["sh", str(launcher), "check"], input=event, capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("nothing was checked", done.stdout)

    @staticmethod
    def hook_types(hooks):
        return [hook["type"] for groups in hooks["hooks"].values() for group in groups for hook in group["hooks"]]

    @staticmethod
    def shipped_hooks():
        return json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))

    def test_no_hook_is_a_prompt(self):
        kinds = self.hook_types(self.shipped_hooks())
        self.assertTrue(kinds)
        self.assertEqual(set(kinds), {"command"})

    def test_a_prompt_hook_under_any_event_is_refused(self):
        hooks = self.shipped_hooks()
        hooks["hooks"]["Stop"] = [{"hooks": [{"type": "prompt", "prompt": "Check the prose."}]}]
        self.assertIn("prompt", self.hook_types(hooks))

    def test_an_agent_hook_under_any_event_is_refused(self):
        hooks = self.shipped_hooks()
        hooks["hooks"]["PostToolUse"] = [{"matcher": "Bash", "hooks": [{"type": "agent", "prompt": "Check the prose."}]}]
        self.assertIn("agent", self.hook_types(hooks))

    def test_each_routed_command_has_a_blocking_fixture(self):
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        routed = {hook["if"] for group in hooks["hooks"]["PreToolUse"] for hook in group["hooks"]}
        self.assertEqual(routed, {f"Bash({command} *)" for command in GATED})


if __name__ == "__main__":
    unittest.main()
