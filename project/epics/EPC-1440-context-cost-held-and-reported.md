---
id: EPC-1440
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1460
checked-at: "#498"
---

# Material loads only when it is needed, and `meow-author` reports each unit's cost and use

Realises exactly one authorising record, ADR-1460. The epic is complete when
`meow-author cost` reports each unit's cost and use and runs in the gate, and
the `write` skill carries the rules on loading.

## Acceptance criteria

Taken from ADR-1460, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-author cost` reports this repository's units against their budgets
   and passes, and fixtures show it failing on a unit over its ceiling, a unit
   with no budget, and a description over the cap.
2. `meow-author cost` names `/skill-doctor` as where each skill's use is
   reported, and the `write` skill has the model consult it before cutting or
   keeping a unit.
3. The skill's rules carry REQ-1052, REQ-1054, REQ-1068, REQ-1070, REQ-1076,
   REQ-1078 and REQ-2696 to REQ-2704, traced in the task's evidence.
4. Every requirement ADR-1460 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2220 report each unit's cost and use with `meow-author cost`,
      in the gate
      closes: REQ-1072, REQ-1074
      evidence: four fixtures, and the `budget` task running the shipped report,
      in #493.

- [x] T-002 [P] TSK-2230 carry the loading rules in `meow-author:write`
      closes: REQ-1052, REQ-1054, REQ-1068, REQ-1070, REQ-1076, REQ-1078,
      REQ-2696, REQ-2698, REQ-2700, REQ-2702, REQ-2704
      evidence: eleven rules traced, in #494.

## Verified

I checked this under #498 on `main` after #497, gathering the evidence there
rather than carrying it over from the tasks. Every criterion is met:

| Criterion                                                                                                                            | Evidence on `main` after #497                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1. `meow-author cost` passes on this repository, and fixtures fail it on an overrun, a missing budget and a description over the cap | The report gives 12 units and 0 failures, and the 4 fixtures in `Cost` pass                                                        |
| 2. The report names `/skill-doctor`, and the `write` skill has the model consult it                                                  | The report's last line names `/skill-doctor`, and step 4 of `meow-author:write` sends the model to it before a unit is cut or kept |
| 3. The skill's rules carry the eleven loading requirements, traced                                                                   | The skill carries C1 to C11, traced in TSK-2230                                                                                    |
| 4. Every requirement lands in exactly one closed task                                                                                | `paw show` derives all 13 requirements ADR-1460 addresses as closed and not yet verified                                           |

### Documentation

TSK-2220 described `meow-author cost` on the unit's page, at 0.3.0. The
`test` verb checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1460 addresses 13 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001. T-002 changes only the
skill, so it can run beside T-001.

## Not covered

Nothing ADR-1460 addresses. Usage across machines is left out, as ADR-1460
says.
