---
id: EPC-NNNN
artifact: epic
status: draft # draft, then approved; in-progress and closed are derived
revised: YYYY-MM-DD
realises: ADR-NNNN # exactly one authorising record: a decision or a defect
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <What this realises>

Realises exactly one authorising record, which gives it an end: the epic is
complete when that decision is realised or that defect is closed.

## Acceptance criteria

1. Taken from the decision's list of how it will be known realised, before the
   tasks are written, each decidable from this epic's own work, and ending
   with every requirement the record addresses named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number, as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [ ] T-001 TSK-NNNN <what, with the path it touches>
      closes: REQ-NNNN
      depends: TSK-NNNN (not blocking) - why, or (blocking) where it waits

## Coverage

Every requirement the record addresses lands in at least one task or is
deferred under the next heading with a reason. A task may close several
requirements, and several tasks may close one. Name the smallest set of tasks
that would test the decision.

## Not covered

What this deliberately leaves, and why, so a later reader can tell an omission
from a boundary.
