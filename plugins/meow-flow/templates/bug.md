---
id: BUG-NNNN
artifact: bug
status: draft # draft, approved, done when `paw done` closes it in its pull request, then withdrawn, rejected or superseded
severity: minor # minor | major | critical, and the reason under Triage
violates: REQ-NNNN # omit where no requirement covers it yet, and say so below
enters: implement # the step it enters at: implement or design where it violates a requirement, requirements where the requirement is wrong or none covers it, research where the cause is unknown
found: YYYY-MM-DD
revised: YYYY-MM-DD
issue: # the tracker's number, where the repository uses one
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <What is wrong, as a statement>

One defect, stated so a reader who stops here knows what is broken; a second
defect is a second record, because a record describing two can't be closed.

## Reproduction

The environment and the versions, exactly, and the revision it was seen at.
Then ordered steps from a stated starting state. A defect with no reproduction
is a report, because the triage question can't be answered about behaviour
nobody has seen twice; where it can't be reproduced, say why and how often it
happens.

## What the system does

What happened, exactly, with the evidence: output, a log, a screenshot. Strip
secrets and personal data from it first.

## What it should do, and why

What was expected, and the requirement it violates, cited in `violates`. Where
none exists, say so here: that is a gap in the requirements and routes to the
requirements step.

## Triage

Where in the chain this enters, and why it has the severity it has. A report
that turned out not to be a defect says so here, so it isn't triaged again. No
priority: when to fix it is the tracker's question, not the record's.

## Closed by

The reproduction, now passing, and where it lives as a regression check. The
fix is a change reviewed on its own, never an edit made inside this record.

## Plan

The ordered steps of this defect's one pull request, required where `enters` is
`implement`. Each step lands its failing tests in a commit of their own, then
the change, its documentation and its record. Delete this section where the
defect enters earlier, because the decision it leads to carries the plan.

1. <What this step makes true, with the path it touches>
