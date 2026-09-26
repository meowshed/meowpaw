---
id: EPC-1210
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1210
checked-at:
---

# The record reports where it contradicts itself

Realises exactly one authorising record, ADR-1210. The epic is complete when
the check reports each contradiction ADR-1210 names, and `show` and `status`
derive each requirement's state.

## Acceptance criteria

Taken from ADR-1210, from its list of how I will know it was realised, before
the tasks below were written:

1. A fixture with a task whose evidence is written and whose epic leaves it
   unmarked fails `check coverage`, and one whose body names a missing
   identifier fails `check relations`.
2. A fixture shows `show` printing a requirement's closing task and its
   verification, and "checked by nothing" for one with none.
3. A fixture shows `status` withholding "verified" from an epic with a finding,
   and reporting a record under no version control as local.
4. Each requirement ADR-1210 addresses that already holds has its evidence
   recorded in the task that closes it.
5. Every requirement ADR-1210 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1700 the check reports work left unmarked and identifiers that resolve to nothing
      closes: REQ-0704, REQ-0710

- [ ] T-002 TSK-1710 show and status derive each requirement's state
      closes: REQ-0527, REQ-0584, REQ-0591, REQ-0706, REQ-0712, REQ-0714

- [ ] T-003 TSK-1720 record the evidence for the status rules that already hold
      closes: REQ-0510, REQ-0516, REQ-0518, REQ-0519, REQ-0582, REQ-0586, REQ-0690, REQ-0694, REQ-0696, REQ-0716

## Coverage

ADR-1210 addresses 18 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1700 and TSK-1710 both change the
record's program, so they run one after the other; TSK-1720 runs alongside.

## Not covered

Nothing ADR-1210 addresses.
