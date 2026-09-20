---
id: RSH-NNNN
artifact: research
status: draft # draft | approved | superseded
revised: YYYY-MM-DD
unit: U-NNNN
prompted-by: BUG-NNNN | ADR-NNNN # omit where nothing prompted it
---

# <Question>

What this covers and what it does not. A reader who stops here knows whether
their question belongs in this document.

## The question

What is being decided, what constrains it, and what is explicitly out of scope.

## Findings

One per claim, stated as a claim rather than as a topic. Each carries its
evidence and its source. A finding with no source is an assertion.

## What this implies

Implications, not decisions. The decisions are recorded separately, and this
section is what they will cite.

## Conclusions

What follows for the system, numbered, each standing on its own. This is the
section requirements are built from, so a conclusion states what must now be
true rather than what was interesting. It cites no requirement: requirements
come later and cite this, and a record written earlier cannot be kept current
by one written later.

A conclusion that no finding above supports is an opinion. A finding that
supports no conclusion belongs in a different document.

## Sources

Every source, identified well enough to reach: a link for anything published, a
path and a revision for anything in a repository, **and a date for anything that
can change** ([R-H-034a], [R-H-034b]).
