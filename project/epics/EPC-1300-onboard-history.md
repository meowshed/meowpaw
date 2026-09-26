---
id: EPC-1300
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1300
checked-at:
---

# Onboarding reads what the history states

Realises exactly one authorising record, ADR-1300. The epic is complete when
the onboard command reads the forge history through `meow-github` and recovers
what it states as drafts.

## Acceptance criteria

Taken from ADR-1300, from its list of how I will know it was realised, before
the tasks below were written:

1. Each rule ADR-1300 places in the onboard command maps to its requirement
   in the task that closes it.
2. The onboard command runs `meow-github history` only as a bare command, and
   `check_standalone.py` passes.
3. Every requirement ADR-1300 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1920 the onboard command reads the forge history and recovers what it states
      closes: REQ-3110, REQ-3112, REQ-3128

## Coverage

ADR-1300 addresses 3 requirements, and all land in the one task above.

## Not covered

Nothing ADR-1300 addresses.
