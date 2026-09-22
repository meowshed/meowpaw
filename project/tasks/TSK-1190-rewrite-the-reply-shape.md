---
id: TSK-1190
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-0956]
issue: 56
---

# Rewrite the reply shape to the standard, and measure it

One task, one branch, one pull request, one review.

## What to do

Rewrite `plugins/meow-core/output-styles/meow.md` and
`plugins/meow-core/fragments/reply-shape.md` against the standard `meow-prose`
states. Keep every rule and its condition, since `tools/check_style.py` fails
on a rule with none.

Measure the rewrite against the style it replaces (REQ-0956), with the runner
TSK-1170 builds. The style and the fragment each go through the loop
separately, because the fragment reaches a subordinate agent the style never
reaches, and its cases are replies from an agent dispatched with it:

- The current style, or the current fragment, is the baseline.
- Each candidate changes one thing, so its delta can be attributed.
- Every candidate runs on the same cases, with the same run count and the same
  judge.
- A candidate lands when the delta holds or rises and the token cost falls. A
  better score at a higher cost is published with both numbers, and the owner
  decides.
- Every candidate's delta is published, including the ones that lost. If none
  lands, the baseline stays, and that is reported as the result.

Select the style explicitly in both arms, because BUG-1040 means it does not
apply on its own.

## Depends on

TSK-1110, because the rewrite follows the standard, and TSK-1170, because a
case set scoring 1.00 in both arms cannot see whether a rewrite helped.

## Evidence

Not yet. The task closes on the published table of candidates, each with its
delta, its token cost, the run count and the judge, and on
`mise run style` passing on whichever style landed.

## Left alone

How the style reaches a session, which BUG-1040 routes to design.
