---
id: EPC-2840
artifact: epic
status: done
revised: 2026-10-11
realises: ADR-2960
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The checker's walk follows no relation a record moved away on

Realises exactly one authorising record, ADR-2960. The epic is complete when
the specification states that the provider walk treats `supersedes`,
`postpones` and `violates` as what a record moved away on or moved against,
and the walk's code and its tests hold under TSK-5500, as SPC-1100 states
under "Deep coverage, suspect citations and unconnected artifacts".

## Acceptance criteria

1. The specification names the three excluded relations and why a defect's
   `violates` is among them.
2. Every requirement ADR-2960 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-5620 state the walk's excluded relations in the specification (done: pull request 1062)
      closes: REQ-0139
      — done in this pull request: the specification states the three
      exclusions, and the two crate tests the code carries pass by name.

## Coverage

REQ-0139, the one requirement ADR-2960 addresses, lands in TSK-5620, whose
work is the specification sentence; the code change and its tests landed
under BUG-1640's TSK-5500, whose exclusion is already in `record.rs`, and
that task's evidence closes where the tests ran.

## Not covered

Every other relation's provider semantics, which TSK-5500's Left alone
states, and the status report's rejected-provider walk, which follows the
same exclusion and is held by the same tests.
