---
id: TSK-5620
artifact: task
status: approved
revised: 2026-10-11
epic: EPC-2840
closes: [REQ-0139]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State the walk's excluded relations in the specification

SPC-1100's "Deep coverage, suspect citations and unconnected artifacts" names
the relations the provider walk excludes, with the reason ADR-2960 gives: a
defect's `violates` names what it moved against, the same kind of link
`supersedes` and `postpones` already are. One task, one branch, one pull
request, one review: the specification is the change, the tests that hold it
already ran under TSK-5500, and the marks land in the same pull request.

## Acceptance criteria

1. Given `project/specs/SPC-1100-the-records-relations.md`, when a reader
   reads the deep-coverage section, then it names `supersedes`, `postpones`
   and `violates` as excluded from the walk, with the reason.
   Closed by: the section's own text in this pull request.
2. Given the checker's tests, when the crate test suite runs, then
   `a_violation_behind_a_specification_is_no_provider` and
   `a_draft_behind_a_specification_still_reports` pass.
   Closed by: the `test` stage's outcome in the task's pull request.

## What to do

Edit the living specification only. The code holds: `NOT_PROVIDERS` in
`crates/meow/src/record.rs` already excludes the three, and TSK-5500's crate
tests pin both directions.

## Depends on

- TSK-5500 (not blocking): the code and its tests landed under the defect,
  and this task states what they do.

## Evidence

Criterion 1 closes with the deep-coverage section's own text, which names
`supersedes`, `postpones` and `violates` and the reason ADR-2960 gives.
Criterion 2 closes with the two named crate tests, each seen passing by
name: `cargo test --bin paw a_violation_behind` and `... a_draft_behind`, 1
passed each at tree `9e0982c0c387`'s parent change. The five stages passed
at the tree this pull request binds, and their records are cited in the pull
request.

## Left alone

Every other relation's provider semantics, and the wording of `chains`' rule,
which REQ-0139 states and this task doesn't touch.
