---
id: EPC-1410
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1430
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

## Coverage

ADR-1430 addresses 7 requirements, and each lands in the one task above,
which is the smallest set that tests the decision.

## Not covered

Nothing ADR-1430 addresses. The method's path for a defect is a later
decision, as ADR-1430 says.
