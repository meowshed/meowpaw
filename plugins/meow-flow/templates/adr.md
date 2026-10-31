---
id: ADR-NNNN
artifact: adr
status: draft # draft, approved, done when `paw done` closes it in its pull request, then withdrawn, rejected or superseded
revised: YYYY-MM-DD
issue: # the tracker's number, where the repository uses one
addresses: [REQ-NNNN] # required: a decision that addresses nothing is a preference
supersedes: []
concerns: [] # optional: each concern the decision raises, such as performance, security or upgrade
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# NNNN. <The decision, as a statement>

## Decision

What was decided, in the present tense, so it can be checked. End with what
works once it is accepted and what still doesn't, because without that line a
reader can't tell an increment from a promise.

## Why

The reasoning and the constraints that made the alternatives lose, each claim
pointing at the research that recorded it.

## Alternatives

| Option     | Better at | Why it lost |
| ---------- | --------- | ----------- |
| Do nothing |           |             |

Three options where the question admits them, each in its advocate's terms,
and doing nothing evaluated rather than mentioned.

## What it costs

Every decision costs something, and an alternative that costs nothing was not
an alternative.

## What would reverse it

- A condition, not an opinion. While it doesn't occur, the argument is over.

## Consequences

What follows mechanically: obligations added, artifacts affected, work
created.

## How I will know it was realised

1. An observable outcome, written now, before the work, so the work can't
   choose its own finish line.

## What this does not settle

- What a reader might assume this decides and it doesn't.

## Plan

The ordered steps of this decision's one pull request. Each step lands its
failing tests in a commit of their own, then the change, its documentation and
its record. The plan stays editable until the decision is done, because the
work corrects it, and it freezes then. Delete this section where the decision
addresses no requirement.

1. <What this step makes true, the requirements it closes and the path it
   touches>
