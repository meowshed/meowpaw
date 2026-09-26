---
id: TSK-1460
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1110
closes: [REQ-0223, REQ-0262, REQ-0558, REQ-2868, REQ-2882]
issue: 200
---

# The rules check

One task, one branch, one pull request, one review.

## What to do

Add a seventh check, `rules`, running the named rules the layout lists per kind, each with its scope: a research draft's source lines each carry a date, a research draft's body cites no requirement, a requirement draft verified by judgement carries `verifier`, an epic's `realises` names exactly one decision or defect, and a decision's alternatives table has a column saying why each lost. Write a fixture for each, seen failing first.

## Depends on

TSK-1450, because the rules read the scope the layout declares.

## Evidence

Not yet.

## Left alone

Rules that need judgement, as ADR-1140 says.
