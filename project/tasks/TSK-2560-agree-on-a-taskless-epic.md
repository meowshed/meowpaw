---
id: TSK-2560
artifact: task
status: approved
revised: 2026-09-28
bug: BUG-1250
closes: []
issue:
---

# Make `ready` and `status` agree on an epic with no tasks

`paw ready document`, `paw ready verify` and `paw status` read an epic that
lists no tasks the same way: ready when it names every requirement its record
addresses under `## Not covered`, and refused, with the same reason, when it
doesn't. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved epic with no tasks that names every requirement its
   decision addresses under `## Not covered`, when `paw ready document` and
   `paw ready verify` run on it, then each exits 0. Closed by: a fixture.
2. Given the same epic, when `paw status` runs, then it names `next:
document, then verify` for its decision. Closed by: a fixture.
3. Given an approved epic with no tasks that leaves an addressed requirement
   unnamed, when `paw ready document` runs, then it exits 1 naming that
   requirement, and `paw status` names the same refusal rather than a step.
   Closed by: a fixture.

## What to do

Change the `document` and `verify` gate and `status`'s position for a
decision in `crates/meow/src/record.rs`, reading `## Not covered` the way the
coverage check does. Keep the refusal for an epic that lists tasks and leaves
one open.

## Depends on

Nothing. BUG-1250 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: none

## Evidence

Not yet.

## Left alone

EPC-1590's own document and verify steps, which run once this lands.
