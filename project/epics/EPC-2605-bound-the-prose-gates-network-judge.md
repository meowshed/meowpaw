---
id: EPC-2605
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2700
---

# Bound the prose gate's network judge

Realises ADR-2700 in TSK-5160.

## Acceptance criteria

1. Only the prose gate may call its bounded judge, and every tool attempt advances the revision.
2. Every addressed requirement lands in the closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5160 hold the prose gate's network exception and revision
      closes: REQ-2716, REQ-2727, REQ-2728

## Coverage

TSK-5160 covers all three obligations at the hook boundary.

## Not covered

No other network exception.
