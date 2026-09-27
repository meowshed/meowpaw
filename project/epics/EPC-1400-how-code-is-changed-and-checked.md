---
id: EPC-1400
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1420
checked-at:
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

## Coverage

ADR-1420 addresses 17 requirements, and each lands in the one task above,
which is the smallest set that tests the decision.

## Not covered

Nothing ADR-1420 addresses. A measurement of how reliably the rules hold comes
with the unit's evaluation cases, as ADR-1420 says.
