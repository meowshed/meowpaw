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
fix is a task of its own, or a change reviewed on its own, never an edit made
inside this record.
