# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1010 states `meow-prose-gate check` blocks.

Each fixture feeds the launcher the JSON Claude Code passes a `PreToolUse`
hook and reads the exit status and standard error. A block must quote a span
found verbatim in the command (REQ-3183). The four false blocks BUG-1230
records are among the texts that must pass. `MEOW_PROSE_GATE_BIN` names the
launcher to test, so the fixtures can run against another build.

No fixture calls a model: each one sets `MEOW_PROSE_GATE_JUDGE` to a stub
judge, which answers with no finding unless the fixture says otherwise.
"""
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_PROSE_GATE_BIN", UNIT / "bin" / "meow-prose-gate"))
FINDING = re.compile(r'^(P[123]|J[123]) \| "(.*)" \| (.+)$')
SCRATCH = tempfile.TemporaryDirectory()


def judge(first=(), second=None, record=None, status=0, sleep=0, raw=None, fork=0, error=None):
    """A stub judge: an executable answering the gate's two calls the way
    `claude -p --output-format json` does, from `first` and `second` (the same
    findings for both when `second` is None). It appends each call's standard
    input to `record` where one is given, prints `error` on standard error,
    and with `fork` leaves a child holding its output open that many seconds
    after it exits."""
    answers = {"1": list(first), "2": list(first if second is None else second)}
    handle, name = tempfile.mkstemp(dir=SCRATCH.name, prefix="judge-")
    os.close(handle)
    path = Path(name)
    path.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import json, os, subprocess, sys, time
        prompt = sys.stdin.read()
        if {str(record)!r} != "None":
            with open({str(record)!r}, "a", encoding="utf-8") as out:
                out.write(prompt + "\\n---\\n")
        time.sleep({sleep})
        if {raw!r} is not None:
            print({raw!r})
        else:
            findings = {answers!r}[os.environ["MEOW_PROSE_GATE_CALL"]]
            print(json.dumps({{"type": "result", "structured_output": {{"findings": findings}}}}))
        if {error!r} is not None:
            print("starting the judge", file=sys.stderr)
            print({error!r}, file=sys.stderr)
        sys.stdout.flush()
        if {fork}:
            subprocess.Popen(["sleep", "{fork}"])
        sys.exit({status})
        """), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


def finding(rule, span, fix="say it plainly"):
    return {"rule": rule, "span": span, "fix": fix}


QUIET = judge()


def gate(command, judge_command=None, timeout=30):
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    env = dict(os.environ, MEOW_PROSE_GATE_JUDGE=judge_command or QUIET)
    return subprocess.run([str(BIN), "check"], input=json.dumps(event), capture_output=True, text=True,
                          timeout=timeout, env=env)


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
    """REQ-3183: one block per rule, each quoting a span found verbatim."""

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

    def test_p1_in_a_heredoc_read_through_dev_stdin(self):
        self.assert_blocks("git commit --allow-empty -F /dev/stdin <<'MSG'\na silver bullet\nMSG", "P1", "silver bullet")

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
    "gh -R": ('gh -R o/r pr create --title "Cache pages" --body "the low-hanging fruit"', "P1", "low-hanging fruit"),
    "gh --repo": ('gh --repo=o/r release create v1.2.0 --notes "a silver bullet"', "P1", "silver bullet"),
    "git -C": ('git -C sub commit -m "a silver bullet"', "P1", "silver bullet"),
    "git -c": ('git -c user.name=x commit -m "a deep dive"', "P1", "deep dive"),
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

    def test_gh_short_repo_option(self):
        self.assert_blocks(*GATED["gh -R"])

    def test_gh_long_repo_option(self):
        self.assert_blocks(*GATED["gh --repo"])
        self.assert_blocks('gh --repo o/r issue comment 5 --body "the low-hanging fruit"', "P1", "low-hanging fruit")

    def test_git_directory_option(self):
        self.assert_blocks(*GATED["git -C"])

    def test_git_config_option(self):
        self.assert_blocks(*GATED["git -c"])

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

    def test_a_heredoc_read_through_dev_stdin(self):
        self.assert_passes("git commit --allow-empty -F /dev/stdin <<'MSG'\nCache pages\nMSG")

    def test_a_body_read_through_dev_fd_0(self):
        self.assert_passes(
            "gh pr create --title \"Cache pages\" --body-file /dev/fd/0 <<'EOF'\n"
            "The server skips the template step on a repeat request.\nEOF")

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

    def test_an_idiom_inside_longer_words_passes(self):
        self.assert_passes(
            'git commit -m "Route the circle backend through the cache" -m "a deep diver reads the '
            'undercircle back pages"')

    def test_the_rules_the_gate_left_to_the_reviewer(self):
        self.assert_passes(
            'git commit --allow-empty -m "Normalize the retry behavior" -m "The worker moves a batch to the DLQ '
            'after the third failed attempt."')

    def test_a_bold_opener_with_text_after_it(self):
        self.assert_passes(pr("**Note:** the verbs run through the crate now."))

    def test_a_repo_option_before_a_command_that_publishes_nothing(self):
        self.assert_passes('gh -R o/r pr list --search "the low-hanging fruit"')

    def test_an_idiom_in_a_command_that_publishes_nothing(self):
        self.assert_passes('git commit -m "Cache pages" && grep -c "low-hanging fruit" notes.txt')


COMMIT = 'git commit -m "Stop circling back to the cache"'
PLAIN = pr("The server skips the template step on a repeat request.")


class TheJudgedRules(unittest.TestCase):
    """ADR-2390: a judged finding blocks only where two judgements agree on a span the text holds."""

    def test_a_finding_both_judgements_report_blocks(self):
        # REQ-3744: the first judgement's fix is the one printed.
        done = gate(COMMIT, judge([finding("J1", "circling back", "say you return to it")],
                                  second=[finding("J1", "circling back", "write returning")]))
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertEqual(done.stderr.splitlines(), ['J1 | "circling back" | say you return to it'])

    def test_a_finding_one_judgement_reports_passes(self):
        # REQ-3744, whichever of the two calls reports it.
        for first, second in (([finding("J1", "circling back")], []), ([], [finding("J1", "circling back")])):
            done = gate(COMMIT, judge(first, second=second))
            self.assertEqual((done.returncode, done.stderr, done.stdout), (0, "", ""), (first, second))

    def test_a_judged_span_inside_code_passes(self):
        # REQ-3746: code font, URLs and identifiers name things, so no judged rule reads them.
        for command, rule, span in (
            ("git commit -m 'Name the `circling back` flag'", "J1", "circling back"),
            ("git commit -m 'See https://example.com/perfect-storm now'", "J1", "perfect-storm"),
            ("git commit -m 'Read the TTL_SECONDS setting'", "J2", "TTL"),
            ("git commit -m 'Quote it\n\n```text\n**Why.** Because\n```'", "J3", "**Why.**"),
        ):
            done = gate(command, judge([finding(rule, span)]))
            self.assertEqual((done.returncode, done.stderr, done.stdout), (0, "", ""), command)

    def test_a_judged_span_outside_code_still_blocks_where_it_also_appears_inside(self):
        # REQ-3744: one occurrence in prose is enough.
        done = gate("git commit -m 'Name the `TTL` flag, the TTL of a page'", judge([finding("J2", "TTL")]))
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)

    def test_a_finding_on_a_span_the_text_lacks_passes(self):
        # REQ-3746
        done = gate(PLAIN, judge([finding("J3", "**Why.** Because the server")]))
        self.assertEqual((done.returncode, done.stderr, done.stdout), (0, "", ""))

    def test_an_exact_finding_calls_no_judge(self):
        # REQ-3740
        record = Path(SCRATCH.name) / "calls-exact"
        done = gate(pr("A deep dive into the cache."), judge(record=record))
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn('P1 | "deep dive"', done.stderr)
        self.assertFalse(record.exists(), "the judge was called on a text an exact rule blocked")

    def test_the_judge_reads_the_published_text(self):
        # REQ-3744: both calls judge the same text, the one the command publishes.
        record = Path(SCRATCH.name) / "calls-text"
        gate(COMMIT, judge(record=record))
        calls = record.read_text(encoding="utf-8").split("\n---\n")[:-1]
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])
        self.assertIn("Stop circling back to the cache", calls[0])

    def assert_not_checked(self, judge_command, cause):
        # REQ-3748
        done = gate(PLAIN, judge_command, timeout=110)
        self.assertEqual((done.returncode, done.stderr), (0, ""), done.stdout)
        message = json.loads(done.stdout)["systemMessage"]
        self.assertTrue(message.startswith("meow-prose-gate: the judged rules were not checked: "), message)
        self.assertIn(cause, message)

    def test_a_missing_judge_is_reported_not_checked(self):
        self.assert_not_checked(str(Path(SCRATCH.name) / "no-such-judge"), "could not be started")

    def test_a_failing_judge_is_reported_not_checked(self):
        self.assert_not_checked(judge(status=1), "exited 1")

    def test_a_failing_judge_names_its_last_error_line(self):
        self.assert_not_checked(judge(status=1, error="Not logged in"), "exited 1: Not logged in")

    def test_a_slow_judge_is_reported_not_checked(self):
        self.assert_not_checked(judge(sleep=50), "45 seconds")

    def test_a_judge_whose_child_holds_its_output_is_stopped_at_the_limit(self):
        # REQ-3748: the limit bounds the judge and everything it started.
        started = time.monotonic()
        self.assert_not_checked(judge(fork=70), "45 seconds")
        self.assertLess(time.monotonic() - started, 55)

    def test_an_answer_outside_the_schema_is_reported_not_checked(self):
        self.assert_not_checked(judge([finding("J9", "server")]), "outside the schema")
        self.assert_not_checked(judge(raw="not json"), "outside the schema")

    def test_the_schema_allows_exactly_the_judged_rules(self):
        # REQ-3742
        schema = json.loads((UNIT / "fragments" / "judge.schema.json").read_text(encoding="utf-8"))
        rule = schema["properties"]["findings"]["items"]["properties"]["rule"]
        self.assertEqual(sorted(rule["enum"]), ["J1", "J2", "J3"])

    def test_the_judge_loads_nothing(self):
        # REQ-3750: the judge's command line, as the program's source holds it.
        source = (UNIT.parent.parent / "crates" / "meow" / "src" / "prose.rs").read_text(encoding="utf-8")
        line = re.search(r"const JUDGE_ARGS: \[&str; \d+\] = \[(.*?)\];", source, re.S)
        self.assertIsNotNone(line, "prose.rs holds no JUDGE_ARGS")
        self.assertIn(".args(JUDGE_ARGS)", source, "the judge isn't started with JUDGE_ARGS")
        args = re.findall(r'"((?:[^"\\]|\\.)*)"', line.group(1))
        for flag in ("-p", "--safe-mode", "--no-session-persistence", "--json-schema"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("--tools") + 1], "")
        self.assertEqual(args[args.index("--max-turns") + 1], "1")
        self.assertEqual(args[args.index("--model") + 1], "sonnet")

    def test_every_hook_waits_long_enough_for_the_judge(self):
        # ADR-2390: the hook's timeout outlasts the judge's 45-second limit.
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        timeouts = {hook["timeout"] for group in hooks["hooks"]["PreToolUse"] for hook in group["hooks"]}
        self.assertEqual(timeouts, {120})


class TheHook(unittest.TestCase):
    """ADR-1600: every hook is a command, and a missing binary blocks nothing."""

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
