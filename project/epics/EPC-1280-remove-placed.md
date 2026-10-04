---
id: EPC-1280
artifact: epic
status: done
revised: 2026-09-26
realises: ADR-1280
---

# Onboarding finishes by removing what it placed

Realises exactly one authorising record, ADR-1280. The epic is complete when
`onboarding remove` removes what an approved report placed, and the onboard
command migrates an existing record and writes drafts.

## Acceptance criteria

Taken from ADR-1280, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `onboarding remove` refusing on a draft report, refusing a
   migrated document whose destination doesn't exist, keeping a cited
   document, and removing the rest with a count before and after.
2. Each rule ADR-1280 places in the onboard command maps to its requirement in
   the task that closes it.
3. Every requirement ADR-1280 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1890 remove the documents an approved onboarding report placed
      closes: REQ-3118, REQ-3120, REQ-3122, REQ-3124, REQ-3126
      evidence: three fixtures, the removal and both refusals, in #351.

- [x] T-002 TSK-1900 the onboard command migrates an existing record and writes drafts
      closes: REQ-3114, REQ-3116
      evidence: 2 requirements traced to two rules, in #352.

## Coverage

ADR-1280 addresses 7 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The two tasks can run in parallel.

## Not covered

Nothing ADR-1280 addresses.
