---
id: TSK-2250
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1450
closes: [REQ-0143, REQ-0161]
issue: 503
projected: 6fbe4daa2dd8
---

# `paw status` reports unconnected artifacts, frozen suspect citations and the share resting on judgement

`status` gains the reports ADR-1470 sends there, none of which fails. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved artifact that cites nothing and that nothing cites, and a
   draft doing the same, when `paw status` runs, then it lists the first and
   not the second, and exits as it did before. Closed by: a fixture naming
   REQ-0143.
2. Given an approved artifact over a rejected provider, and an approved record
   citing a requirement revised after it, when `paw status` runs, then it lists
   the first and counts the second. Closed by: a fixture naming REQ-0143.
3. Given requirements verified statically, behaviourally, by evaluation and by
   judgement of an agent and of a person, when `paw status` runs, then it
   counts each and states the share resting on evaluation or judgement. Closed
   by: a fixture naming REQ-0161.
4. Given the project record, when `paw status` runs, then it lists TSK-1000,
   TSK-1100, TSK-1220, BUG-1130 and BUG-1150, counts three suspect citations
   and states 61 of 1,091. Closed by: its output.

## What to do

Add the four reports to `status` in the native tool's `record` feature, using
the chain walk and suspect test TSK-2240 adds.

## Depends on

TSK-2240.

## Evidence

Closes REQ-0143 and REQ-0161. `plugins/meow-verbs/bin/meow-verbs run format lint
test` exits 0 with `summary: format passed, lint passed, test passed`, and the
record fixtures run 152 tests, OK. Each criterion's check:

1. `Reported.test_an_approved_unconnected_artifact_is_listed_and_a_draft_is_not`
   (REQ-0143), seen failing first.
2. `Reported.test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported`
   (REQ-0143), seen failing first.
3. `Reported.test_the_share_resting_on_judgement_is_stated` (REQ-0161), seen
   failing first.
4. `plugins/meow-flow/bin/paw status` on the project record prints
   `61 of 1091 rest on evaluation or judgement`, the three suspect citations
   ADR-1020, ADR-1350 and TSK-2020, and the five unconnected artifacts
   BUG-1130, BUG-1150, TSK-1000, TSK-1100 and TSK-1220, matching ADR-1470.

Two additions the decision didn't foresee. The project record has 7 judged
requirements naming no verifier, approved before a judgement had to name one,
so the count says so instead of leaving 30 and 5 short of 42. And `check
coverage` also reports a draft or living artifact over a rejected provider,
which it can be moved off, following ADR-1470's rule that `check` fails where
a change can clear the finding; its fixture,
`Connections.test_a_living_artifact_over_a_rejected_provider_is_reported`, was
written after the code and not seen failing first.

## Left alone

Withdrawing any unconnected artifact, which is the owner's call.
