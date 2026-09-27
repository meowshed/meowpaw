---
id: EPC-1410
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1430
checked-at: "#472"
---

# A debugging skill reproduces first and tests one hypothesis at a time

Realises exactly one authorising record, ADR-1430. The epic is complete when
`meow-code` ships a debugging skill carrying every rule ADR-1430 lists, and
sessions on both models load it before they edit.

## Acceptance criteria

Taken from ADR-1430, from its list of how I will know it was realised, before
the tasks below were written:

1. Each requirement ADR-1430 addresses is carried by a labelled rule in the
   skill, traced in the task's evidence, and no rule names a requirement, a
   language or a tool.
2. The prompt check and the budget check pass on the unit.
3. Five sessions on each of Sonnet 5 and Opus 5.5, with only the unit
   installed and asked to find why a script prints the wrong value, load the
   debugging skill before any other tool in at least four of the five on each
   model.
4. Every requirement ADR-1430 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2160 add `meow-code:debug` with the debugging rules
      closes: REQ-1890, REQ-1892, REQ-1894, REQ-1896, REQ-1898, REQ-1900,
      REQ-1902
      evidence: seven rules traced, and the skill loading first in ten of ten
      sessions, in #469.

## Verified

I checked this under #472 on `main` after #471, gathering the evidence there
rather than carrying it over from the task. Every criterion is met:

| Criterion                                                                                          | Evidence on `main` after #471                                                                                                             |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Each requirement is carried by a labelled rule, traced, naming no requirement, language or tool | The skill carries 7 labelled rules, TSK-2160 traces the 7 requirements to them, and a search of the skill for record identifiers finds 0  |
| 2. The prompt and budget checks pass                                                               | `check_prompts.py` reports 55 prompts and 0 failures, and `check_budget.py` measures the unit at 502 of 600 characters                    |
| 3. Five sessions per model load the debugging skill before any other tool in at least four         | Asked why a script prints 5 where it should print 4, with only the unit installed: Sonnet 5 loaded it first in 5 of 5, Opus 5.5 in 5 of 5 |
| 4. Every requirement lands in exactly one closed task                                              | `paw show` derives all 7 requirements ADR-1430 addresses as closed and not yet verified                                                   |

The sessions measure routing, by hand. Whether the rules change how the model
debugs needs the unit's evaluation cases, as ADR-1430 says.

### Documentation

TSK-2160 added the skill to `meow-code`'s page and restamped it at 0.2.0. The
`test` verb checked it, running `tools/check_docs.py`, which reports 14 pages
and 0 failures.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1430 addresses 7 requirements, and each lands in the one task above,
which is the smallest set that tests the decision.

## Not covered

Nothing ADR-1430 addresses. The method's path for a defect is a later
decision, as ADR-1430 says.
