---
id: EPC-2770
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2860
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2770. An epic is one pull request, from its research or from its approved records

This epic realises ADR-2860. It is complete when a task approved on the working
tree is ready to implement, the constitution and the method unit say that the
work of one epic is one pull request in either form, and the commit skill says
the same.

## Acceptance criteria

1. `paw ready implement` exits 0 for a task approved on the working tree and
   absent from the trunk (ADR-2860, criterion 1).
2. No living or shipped text says "one task, one branch, one pull request", and
   `CLAUDE.md` says that the work of an epic is one pull request (ADR-2860,
   criterion 2).
3. REQ-4400, REQ-4402, REQ-4404, REQ-4406, REQ-4408, REQ-4410, REQ-4412 and
   REQ-4414 are each named by a closed task.
4. This epic merged as one pull request holding its records and its three tasks
   (ADR-2860, criterion 3).

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5290 The readiness check reads a task's approval from the working tree (done: pull request 880)
      closes: REQ-4412
      depends: nothing
- [x] T-002 TSK-5291 The constitution, the method unit and its templates say it (done: pull request 880)
      closes: REQ-4400, REQ-4402, REQ-4404, REQ-4410, REQ-4414
      depends: TSK-5290 (blocking) - the text says a task approved on the branch is ready, and that has to work
- [x] T-003 TSK-5292 The commit skill states the unit of a pull request (done: pull request 880)
      closes: REQ-4406, REQ-4408
      depends: TSK-5291 (not blocking) - the two texts agree, and either task can write first

## Coverage

REQ-4412 lands in TSK-5290. REQ-4400, REQ-4402, REQ-4404, REQ-4410 and REQ-4414
land in TSK-5291, and REQ-4406 and REQ-4408 in TSK-5292. TSK-5290 and TSK-5291
are the smallest set that would show the decision realised.

## Not covered

- Stacking an epic on another epic's unmerged branch, whose tooling names tasks
  (ADR-2550). A later decision settles it, because no requirement here asks for
  it.
