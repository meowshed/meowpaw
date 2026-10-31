---
id: TSK-5690
artifact: task
status: done
revised: 2026-10-24
epic: EPC-2860
closes: [REQ-0930, REQ-0932]
issue: 1088
projected: a61719c7ee64
tracked: 1e5652c203cf
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Print the reply shape at session start

`meow-core` ships a `SessionStart` hook that prints the style's role and rules blocks as `additionalContext`, so a session holds the reply shape whether or not the style is selected (ADR-3050).

## Acceptance criteria

1. Given `meow-core`'s style file, when the hook runs with `CLAUDE_PLUGIN_ROOT` set to the unit, then it prints one JSON object whose `hookSpecificOutput.hookEventName` is `SessionStart` and whose `additionalContext` equals the style's `<role>` block and `<rules name="the reply shape">` block, and exits 0 (REQ-0930, REQ-0932). Closed by: a test in `plugins/meow-core/tests/` naming both requirements, seen failing first.
2. Given a style file whose blocks hold quotes, backslashes and tabs, when the hook runs, then the JSON parses and the text round-trips unchanged (REQ-0930). Closed by: the same test file.
3. Given a style file that is missing, unreadable or without a rules block, when the hook runs, then it prints nothing and exits 0 (REQ-0930). Closed by: the same test file, one case for each.
4. Given `hooks/hooks.json`, when a test reads it, then `SessionStart` lists the new hook beside `write-root` (REQ-0932). Closed by: the same test file.
5. Given the unit's page and SPC-1240, when `tools/check_docs.py` and `paw check` run, then both list the hook and report no finding. Closed by: those two commands.

## What to do

Write `hooks/reply-shape` as a POSIX shell script in the style of `write-root`, with the same licence header. It reads `output-styles/meow.md` under `CLAUDE_PLUGIN_ROOT`, cuts the `<role>` block and the `<rules name="the reply shape">` block, and prints them as the JSON string the platform expects, escaping backslash, quote, newline and tab with `awk`. Add it to `hooks/hooks.json` under `SessionStart`. Raise `meow-core` by one patch version in both trees, with a changelog line, and carry the version to the pages that name it. Rewrite the three places SPC-1000 states that the style applies only when selected, and add the hook's row to SPC-1240 and a sentence to the unit's `## Hooks` section.

## Depends on

Nothing.

## Evidence

Criteria 1 to 4 are closed by `plugins/meow-core/tests/test_reply_shape_hook.py`, whose docstrings name REQ-0930 and REQ-0932: the hook's JSON carries the role and rules blocks of `output-styles/meow.md` byte for byte and names rules R1 to R11, the encoding keeps quotes, backslashes and tabs, the hook prints nothing and exits 0 for a missing style file, a style without a rules block and an unset plugin root, and `hooks.json` lists it beside `write-root`. The six tests failed first with `FileNotFoundError` on `hooks/reply-shape`, in the commit before the hook, and pass with it. Run against the shipped style the hook prints 3,682 bytes of context.

Criterion 5 is closed by `python3 tools/check_docs.py`, which reports 29 pages and 0 failures, and by `paw check`, which reports no finding apart from the length advice for `CLAUDE.md`.

The hook was not run inside a live Claude Code session, so that the platform delivers `additionalContext` to the model rests on its documentation, which RES-0203 records, and a first real session shows it.

Every stage passed in pull request #1087.

## Left alone

The style file, the rules block, and the Pi extension, which delivers the shape already.
