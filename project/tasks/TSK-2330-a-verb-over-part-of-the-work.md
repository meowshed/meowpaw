---
id: TSK-2330
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1500
closes: [REQ-0140, REQ-0142]
issue: 541
projected: 0d3cff48b702
---

# `meow-verbs` runs a verb over part of the work through its declared form

A verb's profile value may be a table with `command` and `subset`;
`run <verb>... -- <targets>` runs the subset form, reports a verb with none as
`no subset form`, and records the targets, which `evidence` keeps out of the
whole verb's result. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1520's first criterion lists, when `run`, `status`
   and `evidence` run, then each behaves as that criterion says. Closed by:
   fixtures naming REQ-0140 and REQ-0142, seen failing first.
2. Given a later subset record, when `evidence test` runs, then it reports the
   whole run's record and prints the subset one as `subset only`. Closed by: a
   fixture naming REQ-0142.
3. Given the `verify` skill, when it is read, then it runs a part through
   `run <verb> -- <targets>`, reports `no subset form`, asks the person before
   a whole run, and never runs a tool around the program; `meow-author check`
   passes. Closed by: the trace and its output.

## What to do

Change the native tool's `verbs` feature and `plugins/meow-verbs/skills/verify/SKILL.md`,
state the form on `meow-verbs`' page, and move the unit to its next minor
version.

## Depends on

Nothing. ADR-1520 is approved.

## Evidence

Closes REQ-0140 and REQ-0142. `meow-verbs evidence format lint test` exits 0,
as cited in the pull request at the tree the task's commit records.

The `meow-verbs` fixtures run 30 tests, OK; the 8 in `Subset` failed on the
program before the change, with 5 failures and 1 error. Each criterion's
check:

1. `Subset`: a declared form run with two targets quoted, one holding a space
   and one a semicolon; a verb with no form reported as `no subset form`, with
   nothing run and exit 3; a run naming both kinds of verb running the first
   and reporting the second, exiting 3; a string value still resolving; `--`
   with no target refused; a form without `{targets}` reported as a malformed
   declaration; and `status` showing each form or its absence (REQ-0140,
   REQ-0142).
2. `Subset.test_a_subset_record_never_stands_for_the_whole_verb`: `evidence`
   reports the whole run's record and prints the later subset one as
   `subset only` (REQ-0142).
3. The `verify` skill's step 2 runs a part through `run test -- <target>...`,
   and V6 reports `no subset form` and asks the person before a whole run,
   reporting it as the whole verb; `meow-author check` passes on it, 0
   authoring failures.

`meow-verbs` moves to 0.5.0, and its page and SPC-1040 name the sixth kind of
unresolved verb.

## Left alone

A language pack's subset form.
