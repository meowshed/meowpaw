---
id: EPC-1220
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1220
checked-at:
---

# The record keeps an insight

Realises exactly one authorising record, ADR-1220. The epic is complete when
the record keeps an insight with its shape checked, and the method says when
to write one and how to find one.

## Acceptance criteria

Taken from ADR-1220, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `check` refusing an insight whose title carries a date, whose
   evidence holds no number or block, or that doesn't end with its pattern,
   and passing one that meets each rule.
2. `meow-method template insight` prints the template, and `new insight`
   allocates `INS-0001` in an empty record.
3. Each rule ADR-1220 places in the skill and the implement step maps to its
   requirement in the task that closes it.
4. Every requirement ADR-1220 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1730 the record keeps an insight, its shape checked
      closes: REQ-0568, REQ-0569, REQ-0571, REQ-0574, REQ-0576

- [ ] T-002 TSK-1740 the method says when to write an insight and how to find one
      closes: REQ-0570, REQ-0572, REQ-0577, REQ-0578, REQ-0580

## Coverage

ADR-1220 addresses 10 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The two tasks can run in parallel.

## Not covered

Nothing ADR-1220 addresses.
