---
id: TSK-5322
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2810
closes: [REQ-4706]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The method runs the synchronisation and the script is retired

The method's start and end steps for an epic run `meow-github sync` where a tracker
is declared, and `tools/sync_issues.py` is removed.

## Acceptance criteria

1. Given the method unit's steps, when read, then the implement step names
   `meow-github sync` at its start and at its end where `[tracker] kind` is
   declared. Closed by: a test in `plugins/meow-flow/tests/test_record.py`.
2. Given the repository, when `tools/sync_issues.py` is looked for, then it is
   gone and no file names it. Closed by: a test in `tools/`.

## What to do

Add the lines to the implement step and its package mirror, and delete the script
with its mentions.

## Depends on

- TSK-5321 (blocking): the steps name the command.

## Evidence

Not yet.

## Left alone

The request layer's limits and spacing (ADR-1810), which every write already
goes through.
