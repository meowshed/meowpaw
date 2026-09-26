---
id: EPC-1270
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1270
checked-at:
---

# Each unit is adopted alone, and a missing capability names its fix

Realises exactly one authorising record, ADR-1270. The epic is complete when
a check holds each unit apart, every unavailable capability names what would
supply it, and the adoption rules that already hold have their evidence.

## Acceptance criteria

Taken from ADR-1270, from its list of how I will know it was realised, before
the tasks below were written:

1. A fixture shows `check_standalone.py` reporting a path that climbs out of
   a unit and one naming another unit's directory, and this repository
   passes it.
2. Fixtures show `meow-verbs status` naming `.meowpaw/profile.toml` for an
   undeclared verb, and a launcher with no binary naming the machine and the
   reinstall, each still reported unresolved or unchecked.
3. Each requirement that already holds has its evidence recorded in the task
   that closes it.
4. Every requirement ADR-1270 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1860 an unavailable capability names what would supply it
      closes: REQ-0036, REQ-0038, REQ-0040

- [ ] T-002 TSK-1870 each unit stands alone, and a check holds it
      closes: REQ-0012, REQ-0014, REQ-0034

- [ ] T-003 TSK-1880 record the evidence for the adoption rules that already hold
      closes: REQ-0010, REQ-0016, REQ-0018, REQ-0022, REQ-0024, REQ-0026, REQ-0028, REQ-0030

## Coverage

ADR-1270 addresses 14 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The three tasks can run in parallel.

## Not covered

Nothing ADR-1270 addresses.
