---
id: EPC-1250
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1250
checked-at:
---

# A repository is brought into the harness by `/meow-method:init`

Realises exactly one authorising record, ADR-1250. The epic is complete when
the init command and its template exist with their rules, and an empty record
reports its coverage as zero.

## Acceptance criteria

Taken from ADR-1250, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-method template profile` prints a template that names no language,
   build tool or package manager, and `/meow-method:init` carries
   `disable-model-invocation`.
2. Each rule ADR-1250 places in the command maps to its requirement in the
   task that closes it.
3. A fixture shows `check coverage` and `status` on an empty record reporting
   zero requirements and coverage as zero.
4. Every requirement ADR-1250 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1810 the init command and the profile template
      closes: REQ-1560, REQ-1563

- [ ] T-002 TSK-1820 the init command reports before it writes and chooses nothing
      closes: REQ-1554, REQ-1561, REQ-1562, REQ-1564

- [ ] T-003 TSK-1830 an empty record reports its coverage as zero
      closes: REQ-3098, REQ-3180

## Coverage

ADR-1250 addresses 8 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1820 follows TSK-1810; TSK-1830 runs
alongside.

## Not covered

Nothing ADR-1250 addresses.
