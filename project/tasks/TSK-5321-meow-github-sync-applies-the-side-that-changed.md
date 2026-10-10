---
id: TSK-5321
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2810
closes: [REQ-4700, REQ-4702]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `meow-github sync` applies the side that changed

`meow-github sync` applies one side's change to the other and the file's where both
changed, and reports an approved record's difference.

## Acceptance criteria

1. Given a draft task whose issue's title changed after the last sync, when
   `sync` runs, then the file holds the new title. Closed by: a test in
   `plugins/meow-github/tests/test_github.py`.
2. Given a task whose title changed in the file only, when `sync` runs, then the
   issue holds it. Closed by: a test in the same file.
3. Given both sides changed, when `sync` runs, then the issue holds the file's
   text. Closed by: a test in the same file.
4. Given an approved task whose issue's title changed, when `sync` runs, then it
   writes nothing into the file and prints the difference. Closed by: a test in
   the same file.
5. Given an issue closed on the tracker, when `sync` runs, then the record
   carries the done mark as REQ-1355 asks. Closed by: a test in the same file.

## What to do

Add the subcommand through the request layer, compare the two fingerprints with
the current text of each side, and write the file as structured data.

## Depends on

- TSK-5320 (blocking): the command compares the two fingerprints.

## Evidence

Not yet.

## Left alone

The request layer's limits and spacing (ADR-1810), which every write already
goes through.
