---
id: EPC-1230
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1230
checked-at:
---

# The record keeps its reading order, and its history out of the way

Realises exactly one authorising record, ADR-1230. The epic is complete when
the specifications read in citation order, withdrawn statements and archives
are reported, and a draft requirement is checked for one obligation.

## Acceptance criteria

Taken from ADR-1230, from its list of how I will know it was realised, before
the tasks below were written:

1. A fixture lists a specification before one it cites and fails `check
index`, and this repository's index passes.
2. Fixtures show `check shape` reporting a withdrawn requirement in a living
   document's body and an archive directory, and passing one collected under
   Withdrawn.
3. Fixtures show `check rules` reporting each of the three statements in a
   draft requirement, and passing each in an approved one.
4. Each requirement that already holds has its evidence recorded in the task
   that closes it.
5. Every requirement ADR-1230 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1750 the specifications read in citation order
      closes: REQ-0525
      evidence: a fixture, and the specifications reordered with their cycles
      broken, in #299.

- [x] T-002 TSK-1760 withdrawn statements are collected and nothing is archived
      closes: REQ-0530, REQ-0552, REQ-0554, REQ-0555
      evidence: two fixtures and two recorded rules, in #300.

- [ ] T-003 TSK-1770 a draft requirement carries one obligation, stands alone, and prohibits with MUST NOT
      closes: REQ-2880

## Coverage

ADR-1230 addresses 6 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The three tasks change the record's program,
so they run one after the other.

## Not covered

Nothing ADR-1230 addresses.
