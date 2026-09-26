---
id: EPC-1240
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1240
checked-at:
---

# A change to the record's shape migrates what exists

Realises exactly one authorising record, ADR-1240. The epic is complete when a
retired name fails the check, the record can be counted, and the method
carries the migration rules.

## Acceptance criteria

Taken from ADR-1240, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `check front-matter` reporting a record carrying `unit` or
   `status: proposed`, and a layout declaring a retired status.
2. A fixture shows `count` printing each kind's count by status and the
   number of identifiers, identical on two runs.
3. Each rule ADR-1240 places in the skill maps to its requirement in the task
   that closes it.
4. Every requirement ADR-1240 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1780 a retired name is recorded and never reused
      closes: REQ-3010, REQ-3011

- [ ] T-002 TSK-1790 the record can be counted before and after a migration
      closes: REQ-3020

- [ ] T-003 TSK-1800 the method says how a change to the record's shape migrates it
      closes: REQ-3008, REQ-3009, REQ-3012, REQ-3014, REQ-3016, REQ-3018, REQ-3019

## Coverage

ADR-1240 addresses 10 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1780 and TSK-1790 change the record's
program, so they run one after the other; TSK-1800 runs alongside.

## Not covered

Nothing ADR-1240 addresses.
