---
id: TSK-5320
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2810
closes: [REQ-4704]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The mapping carries the tracker side's fingerprint

The mapping on a task holds a fingerprint of the issue's title, body and state at the
last synchronisation, beside the record side's.

## Acceptance criteria

1. Given a projected task, when `meow-github project` finishes, then `projected:`
   holds a record fingerprint and a tracker fingerprint. Closed by: a test in
   `plugins/meow-github/tests/test_github.py`.
2. Given an existing mapping with the record fingerprint only, when `project`
   runs, then it adds the tracker fingerprint and changes nothing else. Closed
   by: a test in the same file.

## What to do

Extend the mapping and read it with both forms (expand, migrate, contract), and
name the release that drops the older form.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The request layer's limits and spacing (ADR-1810), which every write already
goes through.
