---
id: EPC-2600
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2540
---

# Project an epic onto a tracker group

Realises ADR-2540 in TSK-5155. The epic is complete when projection creates
the parent, links every task and reports each mechanism and pending state.

## Acceptance criteria

1. A fixture epic projects its parent, task links, mechanisms and pending state.
2. A harness-authored write starts no second synchronisation.
3. Every addressed requirement lands in the closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5155 project an epic onto the tracker's grouping
      closes: REQ-1364, REQ-1366, REQ-1370, REQ-1390, REQ-1398, REQ-2562, REQ-2570, REQ-2584, REQ-2586, REQ-2588, REQ-2824

## Coverage

TSK-5155 tests the projection as one transaction because its parent, links
and report are one observable result.

## Not covered

Tracker kinds with no grouping mechanism.
