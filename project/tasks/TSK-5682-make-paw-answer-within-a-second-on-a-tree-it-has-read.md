---
id: TSK-5682
artifact: task
status: approved
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-2800]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make `paw` answer within a second on a tree it has read

`paw check` took 3.5 seconds and `paw status --brief` 1.2 seconds on this repository's record of about 2,200 artifacts on 2026-10-24, with nothing changed between calls. Both have to complete in under one second when nothing changed, and read only what changed when something did.

## Acceptance criteria

1. Given this repository's record read once, when `paw check` runs again with no file changed, then it completes in under 1 second, and `paw status --brief` does too (REQ-2800). The predicted number is under 1 second on the machine that ran the gate. Closed by: a script or test timing the second call, with the measured seconds in the Evidence.
2. Given one record file edited since the last call, when `paw check` runs, then it re-reads that file and no unchanged one, and its findings equal what a run from scratch reports (REQ-2800). Closed by: a crate test that counts file reads and compares the findings with a cold run, seen failing against a cache that ignores the edit.
3. Given a cache that is missing, unreadable or written by another version, when `paw check` runs, then it reads everything and reports the same findings, never a stale result (REQ-2800). Closed by: a crate test for each of the three states.

## What to do

Profile first and say what the 3.5 seconds are spent on. A fix in the hot spot that reaches the second needs no cache, and then the second and third criteria hold trivially and say so. Where a cache is needed, keep it under a state directory the tool owns, never in the record, never committed, and key each entry by the file's path, size and modification time.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

What `paw` reports, which must stay byte-identical to a cold run.
