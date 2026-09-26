---
id: EPC-NNNN
artifact: epic
status: draft # draft, then approved; in-progress and done are derived
revised: YYYY-MM-DD
realises: ADR-NNNN # exactly one authorising record: a decision or a defect
checked-at: # the verification issue, such as "#123", once verified
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <What this realises>

Realises exactly one authorising record, which gives it an end: the epic is
complete when that decision is realised or that defect is closed.

## Acceptance criteria

1. Taken from the decision's list of how it will be known realised, before the
   tasks are written, and ending with every requirement the record addresses
   in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-NNNN <what, with the path it touches>
      closes: REQ-NNNN
      depends: TSK-NNNN - and why, since a convenience isn't a dependency

## Coverage

Every requirement the record addresses lands in exactly one task or is
deferred under the next heading with a reason. Name the smallest set of tasks
that would test the decision.

## Not covered

What this deliberately leaves, and why, so a later reader can tell an omission
from a boundary.
