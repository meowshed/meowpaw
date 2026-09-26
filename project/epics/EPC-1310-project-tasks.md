---
id: EPC-1310
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1310
checked-at:
---

# The GitHub pack projects an approved epic's tasks onto issues

Realises exactly one authorising record, ADR-1310. The epic is complete when
`meow-github project` projects an approved epic's tasks, keeps them in step,
and reports where the record and the tracker disagree.

## Acceptance criteria

Taken from ADR-1310, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures with a stand-in `gh` show `project` creating one issue per task of
   an approved epic, citing its requirements and dependencies and carrying the
   marker, writing `issue:` and `projected:`, reading each back, refusing a
   draft epic, and changing nothing on a second run.
2. Fixtures show a changed task updating its issue, an edited issue reported
   and not overwritten, and a closed issue on an unmarked task reported, with
   `--check` writing nothing.
3. A fixture shows a profile with no tracker reported with nothing done, and
   `check frozen` passing an approved task whose `projected:` changed.
4. Every requirement ADR-1310 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1930 project an approved epic's tasks onto issues
      closes: REQ-1350, REQ-1352, REQ-1354, REQ-1355, REQ-1356, REQ-1360, REQ-1368, REQ-1382, REQ-1386, REQ-1396

- [ ] T-002 TSK-1940 report where the record and the tracker disagree
      closes: REQ-1353, REQ-1378, REQ-1388, REQ-1392, REQ-1394, REQ-1400

- [ ] T-003 TSK-1950 the tracker is declared, optional, and projectable by hand
      closes: REQ-1351, REQ-1372, REQ-1376, REQ-1380, REQ-1384, REQ-1402

## Coverage

ADR-1310 addresses 22 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The tasks run in order, each extending the
command the one before wrote.

## Not covered

Nothing ADR-1310 addresses.
