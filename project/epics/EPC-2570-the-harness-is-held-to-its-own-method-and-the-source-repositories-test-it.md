---
id: EPC-2570
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2690
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The harness is held to its own method, and the six source repositories test it

Realises exactly one authorising record, ADR-2690. The epic is complete when
a test fails a record file outside the layout, the method skill states what a
missing capability becomes, and the first of the six source repositories has
migrated with its evaluation as evidence, as SPC-1090 states under "This
repository's own work".

## Acceptance criteria

Taken from ADR-2690's list of how it will be known realised:

1. A test fails when a record file sits outside the layout `paw template` prints (REQ-1668).
2. The first of the six repositories runs its gate green after migrating, and its evaluation is the task's evidence (REQ-1666).
3. Every requirement ADR-2690 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-5035 pin the record's layout and the four kinds of check with tests in `crates/meow/`
      closes: REQ-1660, REQ-1662, REQ-1668

- [ ] T-002 [P] TSK-5040 state in the method skill that a missing capability becomes a defect or a postponement
      closes: REQ-1670

- [ ] T-003 TSK-5045 migrate the smallest of the six source repositories onto the harness, evaluated by hand
      closes: REQ-1666
      depends: TSK-5040 (not blocking) - a gap the migration finds is recorded by the rule that task states, and can be recorded by hand without it

## Coverage

Each of the five requirements ADR-2690 addresses lands in exactly one task.
TSK-5035 and TSK-5045 are the smallest set that tests the decision, because a
record held to its own layout and a source repository migrated without loss
is the claim. TSK-5035 and TSK-5040 run in parallel. TSK-5045 has an open
question that blocks its implement step: which of the six repositories is
the smallest, and access to it, which only the owner can give.

## Not covered

The other five migrations, each a task the epic step adds after the first
lands, because a defect the first finds would repeat in the rest. REQ-3034,
which asks that the measurement suite run on a schedule and which ADR-2690
leaves open against the owner's rule that evaluations run by hand.
