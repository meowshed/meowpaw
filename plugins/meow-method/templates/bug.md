---
id: BUG-NNNN
artifact: bug
status: draft # draft, approved, or withdrawn; open and closed are derived
severity: minor # minor | major | critical, and the reason under Triage
violates: REQ-NNNN # omit where no requirement covers it yet, and say so below
found: YYYY-MM-DD
revised: YYYY-MM-DD
issue: # the tracker's number, where the repository uses one
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <What is wrong, as a statement>

## Reproduction

Ordered steps from a stated starting state, with the environment, the versions
and the revision it was seen at. A defect with no reproduction is a report,
because the triage question can't be answered about behaviour nobody has seen
twice; where it can't be reproduced, say why and how often it happens.

## What the system does

What was observed, exactly, with the evidence, sanitised.

## What it should do, and why

The requirement it violates. Where none exists, say so: that is a gap in the
requirements and routes to the requirements step.

## Triage

Where in the chain this enters, and why it has the severity it has. A report
that turned out not to be a defect says so here, so it isn't triaged again.

## Closed by

The reproduction, now passing, and where it lives as a regression check. The
fix is a change of its own, reviewed as one.
