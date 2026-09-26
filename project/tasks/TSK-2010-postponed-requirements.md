---
id: TSK-2010
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1330
closes: [REQ-0325]
issue:
---

# A decision postpones requirements, and each verification revisits them

A decision postpones requirements, and each verification revisits them, as
ADR-1330 decides. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved decision postponing a requirement no task closes, when `show` and `status` run, then the requirement reads as postponed by that decision and is counted. Closed by: a fixture.
2. Given a task closing that requirement, when `show` runs, then it no longer reads as postponed. Closed by: a fixture.
3. Given a decision that only postpones, when `check` and `status` run, then it passes with no epic and shows as postponing; and given a decision with neither field, then `check rules` reports it. Closed by: fixtures.
4. Given the verify step, when the trace is read, then REQ-0325 maps to a labelled rule in it. Closed by: the trace and a script finding the label.

## What to do

Add `postpones` to the layout's relations, replace the decision's required `addresses` with the rule `addresses-or-postpones`, derive the postponed state in `show` and `status`, show a postponing decision's position, skip what it postpones in `check coverage`, and add the verify step's rule.

## Depends on

Nothing. ADR-1330 is approved.

## Evidence

Not yet.

## Left alone

Judging whether a postponement's condition holds, which ADR-1330 leaves to a
person.
