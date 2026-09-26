---
id: EPC-1330
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1330
checked-at:
---

# A decision may postpone requirements

Realises exactly one authorising record, ADR-1330. The epic is complete when a
decision can postpone requirements, the program derives and counts them as
postponed, and the verify step revisits them.

## Acceptance criteria

Taken from ADR-1330, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show a requirement an approved decision postpones derived as
   postponed by `show` and counted by `status`, and no longer postponed once a
   task closes it.
2. A fixture shows a decision that only postpones passing `check`, with no
   epic and no specification, and one with neither `addresses` nor
   `postpones` reported.
3. The verify step carries a rule revisiting postponements, traced in the
   task.
4. Every requirement ADR-1330 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-2010 a decision postpones requirements, and each verification revisits them
      closes: REQ-0325

## Coverage

ADR-1330 addresses 1 requirement, which lands in the one task above.

## Not covered

Nothing ADR-1330 addresses.
