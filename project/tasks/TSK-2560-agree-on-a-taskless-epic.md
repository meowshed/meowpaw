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

- Checks: plugins/meow-flow/tests/test_record.py, the class `TasklessEpic`
- Failing run: project/evidence/caa66d8d0c05.txt
- Landed in: #622
- Judgement: none

## Evidence

`crates/meow/src/record.rs` gains `taskless_gaps`, which both the `document`
and `verify` gate and `status`'s position call. An epic that lists no tasks
gets one line for each requirement its record addresses and leaves unnamed
under Not covered, and none where it names them all. An epic with no tasks
whose record addresses nothing, such as one realising a defect, is refused as
before, with `lists no tasks`.

The three checks in the class `TasklessEpic` failed first: `meow-verbs run
test` exited 1 with `FAILED (failures=3)`, kept as
`project/evidence/caa66d8d0c05.txt`, in the commit that held the checks
alone. They pass now:

```text
$ python3 -m unittest test_record.TasklessEpic    # in plugins/meow-flow/tests
Ran 3 tests
OK                                               # exit 0
$ python3 -m unittest discover -s plugins/meow-flow/tests
Ran 173 tests
OK                                               # exit 0
$ plugins/meow-flow/bin/paw ready document EPC-1590
paw ready document: ready; EPC-1590 approved and complete
```

`meow-flow` 0.34.0 isn't released yet, so this fix ships in it without a
version of its own. `meow-verbs evidence --keep format lint check test build`
exits 0 on this change's own tree, each result kept in `project/evidence/`,
as the pull request cites.

## Left alone

EPC-1590's own document and verify steps, which run once this lands.
