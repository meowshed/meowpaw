---
id: EPC-1300
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1300
checked-at: "#368"
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

- [x] T-001 TSK-1920 the onboard command reads the forge history and recovers what it states
      closes: REQ-3110, REQ-3112, REQ-3128
      evidence: 3 requirements traced to three rules, in #365.

## Verified

Checked under issue 368 at revision `254f25e`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                  | Evidence at `254f25e`                                                                       |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1. Each rule in the onboard command maps to its requirement in the task that closes it                     | B13, B14 and B15 are each found once in `skills/onboard/SKILL.md`, traced in TSK-1920       |
| 2. The onboard command runs `meow-github history` only as a bare command, and `check_standalone.py` passes | `check_standalone.py` reports `88 unit files, 0 paths leaving their unit`                   |
| 3. Every requirement lands in exactly one closed task                                                      | `meow-method check coverage` reports 0 findings, and TSK-1920 is marked `[x]` with evidence |

## Coverage

ADR-1300 addresses 3 requirements, and all land in the one task above.

## Not covered

Nothing ADR-1300 addresses.
