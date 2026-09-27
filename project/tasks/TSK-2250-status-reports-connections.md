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

Not yet.

## Left alone

Withdrawing any unconnected artifact, which is the owner's call.
