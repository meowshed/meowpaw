---
id: TSK-4760
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2450
closes: [REQ-0624, REQ-2852]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ask in the design step whether a decision's vision claims are falsifiable, and which of a contradicting pair is stale

The design step asks of each decision that changes the vision whether every
claim it adds is made falsifiable by a requirement, and where a decision
contradicts the vision, reports that one is stale, asks which and writes
neither, as SPC-1230 states under "What the design step asks". One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given `steps/design.md`, when a fixture reads it, then it asks, for a
   decision that changes the vision, whether a requirement makes each claim
   it adds falsifiable, and says a claim with none is removed (REQ-2852).
   Closed by: a fixture under `plugins/meow-flow/tests/` naming REQ-2852,
   seen failing first.
2. Given the same file, when the fixture reads it, then it says that where a
   decision contradicts the vision, the step reports one of the two as stale,
   asks which, and stops without writing the decision (REQ-0624). Closed by:
   the same fixture naming REQ-0624.

## What to do

Add both questions to `plugins/meow-flow/skills/method/steps/design.md` as
labelled rules, held to SPC-1030 and the unit's `budget.toml`.

## Depends on

- TSK-4710 (not blocking): both add a question to `steps/design.md`, and whichever lands second rebases its rule.

## Evidence

Not yet.

## Left alone

`project/vision.md`, which TSK-4740 rewrites.
