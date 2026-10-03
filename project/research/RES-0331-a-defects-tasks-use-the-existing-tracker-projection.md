---
id: RES-0331
artifact: research
status: approved
revised: 2026-10-03
---

# A defect's tasks can use the existing tracker projection

## Summary

The existing projection contract already has everything a defect's tasks need:
an approved authorising record, tasks that name it, record-owned issue text,
task-local mappings and authoriser-owned completion marks. Supporting a defect
as a projection target should reuse that contract rather than introduce a
second synchronisation path.

## The question

Should tasks carried directly by a defect be projectable onto GitHub Issues,
and if so, does that require a separate protocol? The assumption to challenge
is that a defect needs special synchronisation merely because it is not an
epic. The record already deliberately makes a defect authorise and mark tasks
in the same way as an epic.

## Method

I read `ADR-1310`, `ADR-1440`, `SPC-1080`, the `meow-github project`
implementation and its fixture suite at revision `1ebfdb8b`. I also inspected
the approved defect and task records in this repository on 2026-10-03. No
external source was needed because the question concerns the repository's own
record and command contract.

## Findings

### The projection already accepts more than epics

`crates/meow/src/github/project.rs` accepts either an epic or an ADR target,
selects tasks by their authorising field, derives completion from the owning
record and keeps `issue` plus `projected` on each task. The protocol is already
about an authorising record despite retaining the older parameter name.

### A defect already owns tasks and their completion marks

`ADR-1440` makes a defect authorise work directly and gives its `## Tasks`
section the same marks an epic uses. `SPC-1090` states that the task state of
work authorised by a defect derives from those marks. The information needed
to project and compare a task therefore exists without a new field.

### The current command leaves defect-authorised tasks unreachable

`meow-github project` resolves only `ADR-*` and `EPC-*`, while approved tasks
may name `bug: BUG-NNNN`. Such tasks cannot use the command's create, replay or
`--check` behaviour even though their records carry the same mapping fields.

### Reusing the command has fewer states than alternatives

| Option                             | Better at                                         | Result                                                                                    |
| ---------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Do nothing                         | Keeps the command unchanged                       | Rejected: part of the approved task model remains outside the declared tracker projection |
| Add a separate defect synchroniser | Lets defect wording and policy diverge            | Rejected: it duplicates mapping, replay, refusal and read-back states                     |
| Accept defects in `project`        | Preserves one projection contract and one mapping | Chosen: the authorising kind changes, not the synchronisation protocol                    |

The strongest case against the chosen option is that the command and internal
names say `epic`, so widening them risks hiding kind-specific assumptions.
Fixtures for all three target kinds and explicit authoriser wording make those
assumptions visible. The comparison is decided because the record supplies all
data the shared path requires.

## Conclusions

1. Every approved defect that directly carries tasks must be accepted as a
   tracker-projection target.
2. A defect's projected task must use the same durable mapping, replay,
   disagreement and read-back behaviour as an epic's task.
3. Completion comparison for a defect's task must derive from the defect's own
   task marks.

## Sources

- `project/adrs/ADR-1310-the-github-pack-projects-an-approved-epic-onto-issues.md`, revision `1ebfdb8b`, read 2026-10-03 — the projection contract.
- `project/adrs/ADR-1440-a-defect-authorises-work-directly-and-enters-the-chain-where-its-triage-says.md`, revision `1ebfdb8b`, read 2026-10-03 — defect-owned tasks and marks.
- `crates/meow/src/github/project.rs` and `plugins/meow-github/tests/test_github.py`, revision `1ebfdb8b`, read 2026-10-03 — the implementation and observable fixtures.
