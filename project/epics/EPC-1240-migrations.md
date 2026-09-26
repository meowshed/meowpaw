---
id: EPC-1240
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1240
checked-at: "#316"
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

- [x] T-001 TSK-1780 a retired name is recorded and never reused
      closes: REQ-3010, REQ-3011
      evidence: two fixtures and three retired names recorded, in #309.

- [x] T-002 TSK-1790 the record can be counted before and after a migration
      closes: REQ-3020
      evidence: a fixture, and the count read-only, in #310.

- [x] T-003 TSK-1800 the method says how a change to the record's shape migrates it
      closes: REQ-3008, REQ-3009, REQ-3012, REQ-3014, REQ-3016, REQ-3018, REQ-3019
      evidence: 7 requirements traced to five rules, in #311.

## Verified

Checked under issue 316 at revision `f3b04a2`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                               | Evidence at `f3b04a2`                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `check front-matter` reports a record carrying `unit` or `status: proposed`, and a layout declaring a retired status | `test_a_retired_name_is_refused_in_a_record` and `test_a_retired_name_is_refused_in_the_layout` pass                                            |
| 2. `count` prints each kind's count by status and the number of identifiers, identical on two runs                      | `test_count_prints_each_kind_by_status_and_the_identifiers` passes, and the read-only fixture shows `count` writes nothing; `Ran 4 tests`, `OK` |
| 3. Each rule in the skill maps to its requirement in the task that closes it                                            | TSK-1800's trace holds 7 rows, and M14 to M18 are each found once in `SKILL.md`                                                                 |
| 4. Every requirement lands in exactly one closed task                                                                   | `meow-method check coverage` reports 0 findings, and the three tasks are marked `[x]` with evidence                                             |

## Coverage

ADR-1240 addresses 10 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1780 and TSK-1790 change the record's
program, so they run one after the other; TSK-1800 runs alongside.

## Not covered

Nothing ADR-1240 addresses.
