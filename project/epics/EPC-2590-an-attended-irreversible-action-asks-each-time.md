---
id: EPC-2590
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2750
---

# An attended irreversible action asks each time

Realises ADR-2750. The epic is complete when every named attended action asks
once per invocation and no approval carries to the next.

## Acceptance criteria

1. Fixtures cover push, merge, release, issue write and governance change.
2. A second invocation asks again, while reads and local writes do not.
3. REQ-1420 and REQ-1422 land in a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5150 require a fresh prompt for each attended irreversible
      action, in the permission hooks and method
      closes: REQ-1420, REQ-1422

## Coverage

Both requirements land in TSK-5150 because one fixture sequence proves the
prompt occurs and does not carry over.

## Not covered

Unattended actions, whose authority ADR-2380 fixes before the run starts.
