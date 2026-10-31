---
id: TSK-3430
artifact: task
status: done
revised: 2026-09-30
epic: EPC-1920
closes: []
issue: 739
projected: f0cba895a6ff
---

# Deny an edit that decides a record's status inside a run

The runner sets `MEOW_LOOP_RUN` to the run's id in every call's environment,
and the unit's hook gains a rule, active only when that variable is set, that
denies an Edit or a Write changing a record's stored status to a decided
status. The rule is the first line, so the model hears the refusal before it
spends the iteration; the comparison TSK-3420 adds decides whether a gate was
crossed. This task closes no requirement, because REQ-0888 closes in TSK-3440
(EPC-1920, Coverage). One task, one branch, one pull request, one review.

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1920
criterion 17).

1. Given the hook fed a PreToolUse Edit changing a record's `status: draft`
   to `status: approved` with `MEOW_LOOP_RUN` set, when it runs, then it
   denies the edit; given an Edit of an approved task's `## Evidence`, then it
   allows it. Without the variable, it allows both. Closed by:
   `Hook.test_status_rule` (EPC-1920 criterion 9).
2. Given a Write whose `content` holds `status: approved` for a draft record,
   and a Write of a new specification with `status: live`, with
   `MEOW_LOOP_RUN` set, when the hook runs, then it denies the first and
   allows the second. Closed by: `Hook.test_status_rule_on_write`.
3. Given a run of at least two calls, when the stand-in records its
   environment, then each call's `MEOW_LOOP_RUN` equals the run's id. Closed
   by: `Step.test_run_id_in_every_call`.
4. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Set `MEOW_LOOP_RUN` in each call's environment, as SPC-1201's section "Each
call" states. Add the status rule to the hook's handler for Edit and Write, as
its section "The status rule" states: find the record root as the runner
does, read the kind from the file's directory, use the record code's list of
living kinds for `live`, and read the file on disk to tell a change from a
status already there. Keep the hook's existing rules unchanged.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because the hook gains a rule.

Write the checks first, in a commit of their own, and see them fail on
TSK-3410's tree.

## Depends on

- TSK-3410 (blocking): the record code that names the living kinds and finds
  the record root.
- TSK-3400 (blocking): the last change to the hook this rule joins, so the
  two don't edit the handler at once.

## Evidence

`python3 -m unittest plugins/meow-loop/tests/test_loop.py` exits 0 on this
change, reporting `Ran 87 tests` and `OK`. Five checks in that file close
criteria 1 to 3: `Hook.test_status_rule`, `Hook.test_status_rule_on_write`,
`Step.test_run_id_in_every_call`, `Step.test_run_id_only_in_calls` and
`Hook.test_status_rule_with_an_empty_variable`. The first three failed first
in the checks' own commit, where the hook printed no denial and the stand-in's
environment held no `MEOW_LOOP_RUN`. After the agent review, I
rewrote the hook checks in commits of their own. The rows for a CRLF file, an
Edit with an empty `old_string`, a non-Markdown file in a kind directory and a
CRLF Edit across a line break failed first there, and the other rows pin the
rule against a wrong change. Criterion 4 is closed by the five verbs' outcomes
in this task's pull request, #797, since no run output is kept.

The rule is `status_rule` in `crates/meow/src/runloop.rs`, and the status and
kind logic is `decided_by_edit` in `crates/meow/src/record.rs`, beside the
`decided` rule the comparison after each call uses. The hook allows a write
where it can't read the layout or the profile. It covers Edit and Write, the
tools SPC-1201 names, so a MultiEdit passes it, which BUG-1390 records for the
spec step. A record with CRLF line endings has no front matter for the record
reader, so the comparison after a call reads its status as empty, while the
hook reads that file's status correctly.

## Left alone

A Bash command that writes a record, which the hook can't read and the
comparison after the call catches. Whether the hook fires in a `claude -p`
call and sees the variable, which only a real run shows (EPC-1920, Not
covered).
