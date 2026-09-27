---
id: EPC-1520
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1550
checked-at:
---

# Evidence is kept beside the record by default, and a kept file git ignores is reported

Realises exactly one authorising record, ADR-1550. The epic is complete when
`evidence --keep` writes `<record root>/evidence/<record>.txt` by default and
reports a kept file git ignores or can't check.

## Acceptance criteria

Taken from ADR-1550, from its list of how I will know it was realised, before
the task below was written:

1. Fixtures show `--keep` writing `project/evidence/<record>.txt` with no
   declaration, following a moved `[record] root`, and still obeying
   `evidence_dir`.
2. Fixtures show `--keep` exiting 1 and naming the rule when git ignores the
   kept file, and exiting 3 when git can't answer.
3. `paw check` passes with a kept file under `project/evidence`.
4. REQ-2956 lands in a closed task of this decision's epic.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2370 keep evidence at `<record root>/evidence/<record>.txt`
      and report a kept file git ignores or can't check
      closes: REQ-2956
      evidence: four fixtures seen failing first, and this task's results kept
      in `project/evidence/`, in #553.

## Coverage

ADR-1550 addresses 1 requirement, and it lands in the one task above. TSK-2340
in EPC-1510 closes it too, for ADR-1530, which this decision amends.

## Not covered

Nothing ADR-1550 addresses. Moving files kept before it is left out, as
ADR-1550 says.
