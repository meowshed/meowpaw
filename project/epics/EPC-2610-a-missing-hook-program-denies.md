---
id: EPC-2610
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2710
---

# A missing hook program denies

Realises ADR-2710 in TSK-5165.

## Acceptance criteria

1. Every blocking hook denies with its install command when its program is absent.
2. REQ-1426 lands in the closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5165 deny from a blocking hook whose program is missing
      closes: REQ-1426

## Coverage

TSK-5165 covers each launcher in one shared fixture matrix.

## Not covered

Non-blocking informational hooks.
