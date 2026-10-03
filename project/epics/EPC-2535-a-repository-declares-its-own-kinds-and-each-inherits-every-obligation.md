---
id: EPC-2535
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2600
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A repository declares its own artifact kinds, and each inherits every obligation

Realises exactly one authorising record, ADR-2600. The epic is complete when
`paw check` reads the kinds a repository declares under `[record.kinds]`,
reports a conflict across a declared order, and holds a task's produced
document and the task to each other, as SPC-1070 states under "Kinds a
repository declares" and "A document a task produces".

## Acceptance criteria

Taken from ADR-2600's list of how it will be known realised:

1. A fixture repository declares a kind with prefix `NAR`, and `paw check` checks a `NAR-0001` file's front matter like a built-in kind's (REQ-0666, REQ-0670).
2. A declaration with no template fails `paw check` (REQ-0668).
3. A task with `produces:` whose artifact lacks `prompted-by:` fails `paw check` (REQ-0662).
4. Every requirement ADR-2600 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-4970 read `[record.kinds.<name>]` and hold a declared kind to every general obligation, in the `record` feature of `crates/meow/`
      closes: REQ-0666, REQ-0668, REQ-0670

- [ ] T-002 TSK-4975 report a conflict across a declared kind's `outranks` order, in the `record` feature of `crates/meow/`
      closes: REQ-0667
      depends: TSK-4970 (blocking) - the order is read from the declaration TSK-4970 parses

- [ ] T-003 [P] TSK-4980 check `produces:` on a task against `prompted-by:` on its artifact, in `crates/meow/` and the `task` template
      closes: REQ-0660, REQ-0662, REQ-0664
      depends: TSK-4970 (not blocking) - a produced document may be of a declared kind, and the built-in kinds test the rule without one

## Coverage

Each of the seven requirements ADR-2600 addresses lands in exactly one task.
TSK-4970 and TSK-4980 are the smallest set that tests the decision, because a
declared kind checked like a built-in one and a produced document held to its
task is the claim. TSK-4980 runs in parallel with TSK-4970 and TSK-4975.

## Not covered

A generated index for a declared kind, which ADR-2600 leaves to a later
decision, so `paw index` keeps writing the built-in kinds' indexes only.
