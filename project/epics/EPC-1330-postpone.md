---
id: EPC-1330
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1330
checked-at: "#398"
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

- [x] T-001 TSK-2010 a decision postpones requirements, and each verification revisits them
      closes: REQ-0325
      evidence: four fixtures and V13 in the verify step, in #395.

## Verified

Checked under issue 398 on the trunk after #397, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                                                             | Evidence on the trunk after #397                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1. A requirement an approved decision postpones is derived as postponed by `show`, counted by `status`, and no longer postponed once a task closes it | `test_a_postponed_requirement_is_derived_and_counted` and `test_a_postponed_requirement_a_task_closes_is_no_longer_postponed` pass     |
| 2. A decision that only postpones passes `check` with no epic and no specification, and one with neither field is reported                            | The same fixture passes `check rules` and `check coverage`, and `test_a_decision_addressing_and_postponing_nothing_is_reported` passes |
| 3. The verify step carries a rule revisiting postponements                                                                                            | V13 is found once in `steps/verify.md`, traced in TSK-2010. Applied here, it finds no postponement yet: `status` counts 0 postponed    |
| 4. Every requirement lands in exactly one closed task                                                                                                 | `meow-method check coverage` reports 0 findings, and TSK-2010 is marked `[x]` with evidence                                            |

## Coverage

ADR-1330 addresses 1 requirement, which lands in the one task above.

## Not covered

Nothing ADR-1330 addresses.
