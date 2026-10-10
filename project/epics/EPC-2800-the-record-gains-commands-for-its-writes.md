---
id: EPC-2800
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2880
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2800. The record gains commands for its writes

This epic realises ADR-2880. It is complete when a task is closed, a draft
approved and a requirement withdrawn by one command each.

## Acceptance criteria

1. `paw done` leaves the task, its epic or defect, the decision and the index
   in the state `paw check` accepts (ADR-2880, criterion 1).
2. Each command's result differs from its input only in the lines it owns
   (ADR-2880, criterion 2).
3. REQ-4600 and REQ-4602 are each named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5310 `paw approve` and `paw withdraw` (done: pull request 884)
      closes: REQ-4602
      depends: nothing
- [x] T-002 TSK-5311 `paw done` (done: pull request 884)
      closes: REQ-4600
      depends: TSK-5310 (not blocking) - the two share the writer that changes a status line

## Coverage

REQ-4602 lands in TSK-5310 and REQ-4600 in TSK-5311.

## Not covered

- A command for the project index's prose, which stays a person's.
