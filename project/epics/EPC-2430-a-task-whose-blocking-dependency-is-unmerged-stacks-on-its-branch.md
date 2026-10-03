---
id: EPC-2430
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2550
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A task whose blocking dependency is unmerged stacks on its branch, built with `git` and `gh`

Realises exactly one authorising record, ADR-2550. The epic is complete when
the implement step opens, rebases and reports a stack as SPC-1090 states under
"Stacked tasks", `meow-git restack` rebuilds one as SPC-1060 states under
"Restacking", and `paw status` names the layer that merges next.

## Acceptance criteria

Taken from ADR-2550's list of how it will be known realised:

1. A fixture epic with a blocking chain of three tasks opens three pull
   requests, each against the one below (REQ-1810, REQ-1814).
2. A fixture epic of independent tasks opens each against the trunk and says
   it declined to stack (REQ-1812, REQ-1840).
3. After a base change, the report names the checks as not run (REQ-1820).
4. A fixture restack with a conflict stops and names the branch (REQ-1826).
5. `paw status` names the next layer to merge (REQ-1816).
6. Every requirement ADR-2550 addresses is named by a closed task.

Criteria 1 to 3 are read from the implement step's file against fixture
records, because the step is a prompt and the fixtures check what it tells
the model to run, not a live code host.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4660 open a stack in the implement step: when to stack, the order, the branch name and the cross-repository refusal, in `plugins/meow-flow/skills/method/steps/implement.md`
      closes: REQ-1810, REQ-1812, REQ-1814, REQ-1832, REQ-1834, REQ-1835, REQ-1836, REQ-1838, REQ-1840, REQ-1844

- [ ] T-002 TSK-4670 read a changed base back, report its checks as not run and review one layer's diff, in the implement and review step files
      closes: REQ-1818, REQ-1820, REQ-1822, REQ-1830, REQ-1842
      depends: TSK-4660 (blocking) - it extends the stacking rules TSK-4660 writes into the same file

- [ ] T-003 [P] TSK-4680 rebuild a stack with `meow-git restack`, in the `git` feature of `crates/meow/`
      closes: REQ-1824, REQ-1826, REQ-1828

- [ ] T-004 [P] TSK-4690 print each stack and the layer that merges next in `paw status`, in the `record` feature of `crates/meow/`
      closes: REQ-1816, REQ-1830

## Coverage

Each of the nineteen requirements ADR-2550 addresses lands in a task. REQ-1830
lands in two, because a dropped layer is in the record, which `paw status`
reads, and a closed or ejected one is on the code host, which the step reads.
TSK-4660 and TSK-4680 together are the smallest set that tests the decision,
because a stack that opens and can be rebuilt is the claim. TSK-4660,
TSK-4680 and TSK-4690 run in parallel.

## Not covered

Whether this repository's push guard allows a lease push for a restack, which
ADR-2550 leaves to a later decision, so `restack` prints the lease push and
pushes nothing. Merge queues beyond reporting an ejected layer.
