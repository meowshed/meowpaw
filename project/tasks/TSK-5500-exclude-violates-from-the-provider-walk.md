---
id: TSK-5500
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1640
closes: []
issue:
---

# Exclude `violates` from the record checker's provider walk

`crates/meow/src/record.rs` adds `violates` to `NOT_PROVIDERS`, with the
comment's reason and a crate test. One task, one branch, one pull request, one
review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture record where an approved defect violates a withdrawn
   requirement, an approved requirement elaborates the defect, and a living
   specification states that requirement, when the checker runs, then it
   reports nothing for the specification. Closed by: a crate test in
   `crates/meow/src/record.rs`, seen failing first (BUG-1640).
2. Given the fixture with the requirement approved instead, when the checker
   runs, then a draft specification stating it still reports resting on the
   draft, so the exclusion hides no draft finding. Closed by: the same test.
3. Given this change's tree, when `meow-checks run format lint check test
   build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

## What to do

Extend `NOT_PROVIDERS` with `violates`, and state in the comment why: a
defect's violation is what the defect moved against, the same kind of link
the exclusion already gives `supersedes` and `postpones`. The status report
that reads rejected providers through the same walk moves with it.

## Depends on

Nothing.

## Left alone

The `chains` rule itself, which REQ-0139 states and this defect doesn't
touch, and every other relation's provider semantics.

## Evidence

Not yet.