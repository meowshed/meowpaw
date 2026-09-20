---
id: RES-0033
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Defects

## Summary

The model had a gap: an epic realises a decision, and nobody decides to have a
bug. The resolution is that a defect record authorises an epic exactly as a
decision does, so every task still traces to one of two records. A defect is
evidence that a requirement is not met, and it authorises no new work. Triage
asks one question: whether a requirement in force covers it. The reproduction
is both the check that closes it and the regression test that stays.

Research for how a defect is tracked and planned. The model has a gap: an epic
realises a decision, and nobody decided to have a bug. We derived this answer
and invented none of it.

## Method

The published material on defect handling and triage was fetched and read on
2026-09-20 for the standard vocabulary and the severity-against-priority
split.

We found the gap this document closes in the method itself, and in no source.
The existing model authorised work only through decisions, and seeing that a
defect does not fit took no source at all.

We ran nothing and examined no defect record, so the claims about what a defect
record must contain are reasoned from the model and observed nowhere.

## What a defect is, in this model

The field's own definition does the work:

> A defect is a specific flaw in a software system that causes it to behave
> differently from its intended requirements or specifications.

So a defect is not new work needing a decision. **It is evidence that a
requirement is not met.** The decision was already made; reality disagrees with
it.

That resolves the gap. Work needs an authorising record, and a decision is one
kind. **A defect record is the other.** Both are permanent, both name the
requirements they concern, and both can be realised by an epic.

```text
ADR-NNNN  a decision        --> EPC-NNNN  --> tasks   (new behaviour)
BUG-0031  a defect          ─► EPC-0013  ─► tasks   (restore conformance)
```

The symmetry is not a convenience. It means every task traces to something
permanent that authorised it, with no special case for the unplanned half of
the work - which is the half that actually dominates most repositories.

## Triage is one question

Does a requirement in force cover this?

| Answer                           | What it is                       | Route                                                                                                             |
| -------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Yes                              | The system is out of conformance | Defect record -> epic -> tasks, with no new decision, because the decision stands and the code does not honour it |
| No, and it should                | A **requirement defect**         | `/meow:requirements` appends the missing requirement; the defect record cites it; then the ordinary chain         |
| No, and the requirement is wrong | The decision was wrong           | `/meow:amend`: withdraw, replace, record the decision - the defect is what revealed it                            |
| No, and the behaviour is correct | Not a defect                     | Closed as such, **with the reasoning recorded**, because the same report will arrive again                        |

The second row is the expensive one, and the literature is emphatic.
Requirement defects "cost more than coding defects because they affect
architecture, development, testing, automation, and business validation", and
"the most expensive defects I have seen were written into requirements".

That is why the triage question asks about the requirement and never about the
code. Asking "where is the bug" first finds the line; asking "what did we
require" first finds whether there was ever agreement about what should happen.

## A defect is an entry point as well as an authorisation

The triage table above reads as four outcomes. It is better read as **four
places in the chain a defect can enter**:

```text
BUG ─► research      the cause is unknown
BUG ─► requirements  nothing covers this, and something should
BUG ─► amend         something covers it and is wrong
BUG ─► implement     the requirement stands; the code does not honour it
```

Only the last is "fix the bug". The other three mean the defect produces
research, or a requirement, or a decision - each citing the defect as what
prompted it - and the fix comes after, through the ordinary chain.

That is why a defect is a **record**, and a task is something it authorises. It
outlives whatever it spawned, and everything it spawned points back at it. A
defect modelled as a task would vanish into the work it caused, and the
question "why did we add that requirement" would lose its answer.

## The reproduction is the artifact

Everything else follows from having one ([RES-0015-debugging.md](RES-0015-debugging.md)):

- A defect with no reproduction is a report, and nobody can triage it - because
  the triage question cannot be answered about behaviour nobody has observed
  twice. - The reproduction becomes the **check that closes it**. It fails
  before, passes after, and stays as a regression test. That is evidence in the
  strict sense, and it asserts nothing about the bug being gone. - It is also
  what makes the requirement question answerable: a reproduction states the
  actual behaviour precisely enough to compare against a requirement.

The field says the same thing from the closure end: skipping the evidence
"means arguments later when someone claims it was never really fixed".

And the warning: **the most expensive defects are frequently the ones
introduced by a fix**, so a fix is checked by its own reproduction _and_ by the
checks around the change.

## Severity and priority are two things

Standard practice keeps them separate, because they are routinely conflated.
**Severity describes the defect, and priority describes the fix order.** A
cosmetic defect on the main path outranks a severe one in a corner nobody
reaches.

Severity belongs on the defect record, because it is a property of the defect
and does not change. Priority belongs to planning, because it is a judgement
about now.

## How defects get planned

This is the question the model has to answer, and the answer has two halves.

The small half. An earlier draft of this document said every defect gets an
epic, even for a one-task fix, on the grounds that consistency beats a saved
file. That was wrong, and wrong by the model's own standard: ceremony on
trivial work is what makes a method get worked around
([RES-0031-routing.md](RES-0031-routing.md)).

The correct arrangement: **the defect record carries its own tasks.** An epic
appears when the fix needs several tasks with an order between them - when
there is something to organise. A small defect is a record, one task, one pull
request.

```text
BUG-0031 ──► task ──► PR              small: no epic
BUG-0044 ──► EPC-0019 ──► tasks       large: an epic earns its place
ADR-NNNN --> EPC-NNNN --> tasks       new behaviour
```

The authorising record is always there; the epic is there when it organises
something. That keeps the rule true - every task traces to an authorising
record - without inventing a file whose only content is one line.

The half that matters: the ratio. Maintenance practice has a measure this
method takes. Work divides into _planned_ - scheduled, decided in advance - and
_corrective_, arising from breakdowns. And the balance is diagnostic:

> A reactive work ratio above 30-40% indicates the backlog is being driven by
> uncontrolled breakdown demand, which requires a reliability-centred review.

Translated: **if more than a third of tasks are authorised by defect records
and not by decisions, the problem is the system and not the backlog.** The
harness computes that, because every task names its authorising record and
every record has a kind.

The same source notes the other end: a queue dominated by planned work that
never executes points to a _scheduling_ problem, where the reliability is fine.
Both readings need the same number.

So defect planning is not a separate process. Defects are epics like anything
else, ordered by priority against the rest, and the measurement that matters is
what fraction of the work they are.

## What it costs to keep them permanent

A defect record is permanent, like research and decisions. Every
defect ever found stays.

That is deliberate and it buys two things. A defect that recurs is recognisable
and nobody re-diagnoses it, because the previous reproduction and the previous
cause are findable. And a closed-as-not-a-defect record is what stops the same
report being triaged from scratch every six months.

## Conclusions

1. A defect is evidence that a requirement is not met, and it authorises no new
   work. 2. A defect record authorises an epic exactly as a decision does.
   Every task traces to one or the other. 3. Triage asks one question: does a
   requirement in force cover this? 4. A defect with no reproduction is a
   report. The reproduction is the check that closes it and stays as a
   regression test. 5. Severity is on the record; priority is in planning. 6. A
   requirement defect goes through the requirements step, and a wrong
   requirement through amendment - the defect is what revealed it. 7.
   Not-a-defect is closed with its reasoning recorded. 8. The harness reports
   the ratio of defect-authorised to decision-authorised work, because above a
   third it is a statement about the system.

## Sources

All read 2026-09-20.

- [Defects in software testing](https://www.geeksforgeeks.org/software-testing/what-is-defect-in-software-testing/) - the definition used above: behaviour
  differing from intended requirements or specifications. - [The
  defect-requirements-test triangle](https://www.inflectra.com/Ideas/Entry/the-defectrequirementstest-triangle-196.aspx) - defects, requirements and tests
  as three linked artifacts, where three separate trackers link nothing. -
  [Requirements defects: the value of finding them
  early](https://www.scopemaster.com/blog/requirements-defects/) and [The most
  expensive defects I have seen were written into requirements](https://shiftsync.tricentis.com/software-testing-blogs-69/the-most-expensive-defects-i-have-seen-were-written-into-requirements-2832) - why the triage question asks
  about the requirement and never the code. - [Defect tracking: process, tools,
  and what to capture](https://bug0.com/knowledge-base/defect-tracking) -
  severity describing the defect against priority describing the fix order, and
  native linking to requirements, where a pasted identifier resolves to
  nothing. - [Bug life cycle in software
  testing](https://keploy.io/blog/community/bug-life-cycle) and [Bug life
  cycle: 11 stages](https://www.zoho.com/qengine/know/bug-life-cycle-in-software-testing.html) - evidence at closure, and regression around the change
  because a fix is a common source of the next defect. - [Bug triage:
  definition, examples, and best
  practices](https://www.atlassian.com/agile/software-development/bug-triage) -
  triage as confirming reproducibility, then classifying, then filtering out
  user error, duplicates and feature requests. - [Maintenance backlog meaning:
  the 2026 standard for reliability](https://f7i.ai/blog/backlog-meaning-in-maintenance-the-definitive-guide-to-workflow-management-and-reliability) and
  [Backlog (maintenance)](https://worktrek.com/glossary/maintenance-backlog/) -
  planned against corrective work, and the reactive-ratio threshold of 30-40%
  as a signal about the system, and not about the schedule.
