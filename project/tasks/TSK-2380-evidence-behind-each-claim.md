---
id: TSK-2380
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1530
closes: [REQ-0452, REQ-0454, REQ-0456]
issue:
---

# A dirty submodule binds no result, and `evidence --kept` lists the evidence a change adds

The tree id is `none` where a submodule has uncommitted changes, and
`evidence --kept` lists each kept file the branch adds with its record, its
outcome and whether it matches `HEAD`. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1560's first criterion lists, when they run, then
   each behaves as it says. Closed by: the trace and fixtures naming REQ-0452
   and REQ-0454, the new ones seen failing first.
2. Given the fixtures ADR-1560's second criterion lists, when they run, then
   each behaves as it says. Closed by: fixtures naming REQ-0456, seen failing
   first.

## What to do

Change the native tool's `verbs` feature and its fixtures, and state the
listing on `meow-verbs`' page, moving the unit to its next minor version.

## Depends on

Nothing. ADR-1560 is approved.

## Evidence

Not yet.

## Left alone

Matching record identifiers in tasks, which ADR-1560 leaves to `paw`.
