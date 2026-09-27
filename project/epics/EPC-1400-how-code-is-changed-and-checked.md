---
id: EPC-1400
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1420
checked-at: "#464"
---

# A coding unit holds how code is changed and how a check is written

Realises exactly one authorising record, ADR-1420. The epic is complete when
`meow-code` ships a skill carrying every rule ADR-1420 lists, and a session
shows it loading before an edit.

## Acceptance criteria

Taken from ADR-1420, from its list of how I will know it was realised, before
the tasks below were written:

1. Each requirement ADR-1420 addresses is carried by a labelled rule in the
   skill, traced in the task's evidence, and no rule names a requirement, a
   language, a tool or a file extension.
2. The prompt check and the budget check pass on the unit.
3. A Claude Code session on Sonnet 5 and one on Opus 5.5, each with only the
   unit installed and asked to change code, load the skill before the first
   edit.
4. Every requirement ADR-1420 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2150 ship `meow-code` with the skill that holds how code is
      changed and how a check is written
      closes: REQ-0090, REQ-0092, REQ-0094, REQ-0096, REQ-0098, REQ-1010,
      REQ-1015, REQ-2010, REQ-2012, REQ-2014, REQ-2016, REQ-2018, REQ-2070,
      REQ-2072, REQ-2074, REQ-2076, REQ-2078
      evidence: thirteen rules traced, and the skill loading first on both
      models, in #461.

## Verified

I checked this under #464 on `main` after #466, gathering the evidence there
rather than carrying it over from the task. Every criterion is met, the third
after BUG-1200's fix:

| Criterion                                                                                                     | Evidence on `main` after #466                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Each requirement is carried by a labelled rule, traced, naming no requirement, language, tool or extension | The skill carries 13 labelled rules, TSK-2150 traces all 17 requirements to them, and a search of the skill for record identifiers and file extensions finds 0 |
| 2. The prompt and budget checks pass                                                                          | `check_prompts.py` reports 54 prompts and 0 failures, and `check_budget.py` measures the description at 274 of 330 characters                                  |
| 3. A session on each model loads the skill before the first edit                                              | Five runs per model, asked to change a one-line function with only the unit installed: Sonnet 5 loaded it in 5 of 5, Opus 5.5 in 5 of 5                        |
| 4. Every requirement lands in exactly one closed task                                                         | `paw show` derives all 17 requirements ADR-1420 addresses as closed and not yet verified                                                                       |

The first measurement here, at #463, found Sonnet 5 loading the skill in 2 of
5 runs. BUG-1200 records that, and #466 fixed the description; the runs in
the table are the ones after the fix. Every measurement is by hand, as this
repository's evaluations are.

### Documentation

TSK-2150 wrote `meow-code`'s page, and #466 restamped it at 0.1.1 with the
description's new cost. The `test` verb checked it, running
`tools/check_docs.py`, which reports 14 pages and 0 failures.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1420 addresses 17 requirements, and each lands in the one task above,
which is the smallest set that tests the decision.

## Not covered

Nothing ADR-1420 addresses. A measurement of how reliably the rules hold comes
with the unit's evaluation cases, as ADR-1420 says.
