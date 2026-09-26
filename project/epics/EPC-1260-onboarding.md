---
id: EPC-1260
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1260
checked-at: "#334"
---

# Onboarding recovers what a repository is, and places every document

Realises exactly one authorising record, ADR-1260. The epic is complete when
the onboarding report exists with its disposition checked, and the onboard
command carries its rules.

## Acceptance criteria

Taken from ADR-1260, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `check coverage` reporting a document the report doesn't
   place, one placed twice, an unknown outcome and a discard with no reason,
   and passing a report that places every document once.
2. A fixture shows `check rules` reporting an Adoption section without
   numbered steps.
3. `/meow-method:onboard` carries `disable-model-invocation`, and each rule
   ADR-1260 places in it maps to its requirement in the task that closes it.
4. Every requirement ADR-1260 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1840 the onboarding report places every document, and the check holds it
      closes: REQ-1556, REQ-3096
      evidence: the report kind, its template and four fixtures, in #329.

- [x] T-002 TSK-1850 the onboard command recovers what a repository is and invents nothing
      closes: REQ-1540, REQ-1542, REQ-1544, REQ-1546, REQ-1548, REQ-1550, REQ-1552, REQ-1558, REQ-3092, REQ-3094
      evidence: the command, 10 requirements traced to ten rules, in #330.

## Verified

Checked under issue 334 at revision `f14eb0c`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                                                                             | Evidence at `f14eb0c`                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 1. `check coverage` reports a document not placed, one placed twice, an unknown outcome and a discard with no reason, and passes a report placing every document once | The three onboarding coverage fixtures pass                                                                                   |
| 2. `check rules` reports an Adoption section without numbered steps                                                                                                   | `test_onboarding_adoption_is_numbered_steps` passes; the four onboarding fixtures report `Ran 4 tests`, `OK`                  |
| 3. `/meow-method:onboard` carries `disable-model-invocation`, and each rule maps to its requirement                                                                   | `disable-model-invocation: true` is found once in `skills/onboard/SKILL.md`, and B1 to B10 once each; TSK-1850 traces the ten |
| 4. Every requirement lands in exactly one closed task                                                                                                                 | `meow-method check coverage` reports 0 findings, and both tasks are marked `[x]` with evidence                                |

## Coverage

ADR-1260 addresses 12 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1850 follows TSK-1840.

## Not covered

Nothing ADR-1260 addresses.
