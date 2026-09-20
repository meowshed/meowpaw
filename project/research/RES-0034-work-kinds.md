---
id: RES-0034
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Does every kind of work fit?

## Summary

The model authorises work with two records and derives everything else, and
this document tests that claim against two established taxonomies of work.
Every type in both routes through a decision or a defect, because requirements
are about observable behaviour rather than about products, which is what lets
pipelines, infrastructure and design changes through the same chain. Recurring
work is decided once and executed many times, so no third record is needed.

The model authorises work with two kinds of record - a decision and a defect -
and derives everything else from them. This tests that claim against the
taxonomies the field already uses, rather than against intuition.

It covers whether each established work type has a home, and what happens to the
ones with no evident home. It does not cover how work is prioritised
or scheduled.

## Method

Two published taxonomies of work were fetched and read on 2026-09-20 and used
as the test: each of their categories was taken in turn and routed through the
model to see whether it fitted.

That is the whole method here, and its weakness is that the test was performed
by the same party that designed the model. A category that did not fit would
have been visible, but a category neither taxonomy names would not.

Nothing was run.

## The two taxonomies this model is tested against

The Phoenix Project's four types of work, which is the operations view:

| Type              | What it is                                                                            |
| ----------------- | ------------------------------------------------------------------------------------- |
| Business projects | New products or features - something to show a customer                               |
| Internal projects | Environments, deployment automation, "the often invisible work of keeping IT running" |
| Changes           | Work generated when the first two require changes to existing processes or systems    |
| Unplanned work    | Recovery work, which "almost always takes you away from meeting your goals"           |

The backlog view, which is the engineering one: story or feature, defect,
spike, chore or refactor, technical debt, documentation, change request, risk.

The two overlap badly, which is itself informative: one classifies by _who the
work serves_, the other by _what the work looks like_. Neither classifies by
what authorises it, which is the axis this model uses.

## Running them through the model

| Work                                                | Authorised by                                                                                              | Route                                                                                                                                     |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| A feature                                           | Decision - what to build and why                                                                           | Full chain at L2, reduced at L1                                                                                                           |
| A defect                                            | Defect record - evidence a requirement is unmet                                                            | [RES-0033-defects.md](RES-0033-defects.md)                                                                                                |
| **Design work** - a screen, a flow, a visual system | Decision, where the design _is_ the deliverable and `meow-design`'s `interface-design` skill constrains it | Chain; the artifacts are designs rather than code                                                                                         |
| **A deploy pipeline**                               | Decision - "CI runs these checks", "deploys are blue-green"                                                | Chain, with requirements about the delivery system's behaviour that a check settles: a pipeline either blocks a failing build or does not |
| **Infrastructure**                                  | Decision                                                                                                   | Same, because the method already covers configuration as work it applies to                                                               |
| **A refactor**                                      | Decision - the defect it prevents, or the boundary it restores                                             | Chain, and the requirement is that behaviour is _unchanged_, which the existing checks already assert                                     |
| **Technical debt**                                  | Decision, once someone decides to pay it                                                                   | Until then it is an observation, and belongs in the development log or as a defect if it violates something                               |
| **A spike**                                         | Nothing - it _is_ the research step                                                                        | Its output is a research artifact, permanent and dated, and a spike that answers nothing still produced evidence                          |
| **Documentation**                                   | Usually the `document` step of other work                                                                  | Standalone documentation work is authorised by a decision like anything else                                                              |
| **A dependency upgrade**                            | L0 when routine; a decision when it is a policy                                                            | See below                                                                                                                                 |
| **Toil** - rotating a credential, clearing a queue  | L0 each time                                                                                               | See below                                                                                                                                 |

Nothing in either taxonomy failed to route. Two rows deserve the argument
rather than the assertion.

## Deploy pipelines are behaviour, and that is the whole answer

The intuition that a pipeline does not fit comes from expecting requirements to
be about a product. They are about **a system's observable behaviour**, and a
delivery pipeline has plenty:

- _The pipeline MUST refuse to publish an artifact whose checks did not pass._
- _A deploy MUST be reversible within one command for the previous release._
- _A failed migration MUST leave the previous schema intact._

Each is testable, each has a failure path, and each is exactly the kind of
statement that otherwise lives in somebody's head until the night it matters.
The method's own gate verbs apply unchanged - the `test` verb for a pipeline is
running it against a fixture.

This also explains why the Phoenix Project split "internal projects" out: not
because they are a different kind of work, but because they are **invisible**,
and invisible work does not get specified. Putting them through the same chain
is the fix, not an imposition.

## Routine work is authorised by a standing decision

The genuinely awkward case is work that recurs forever: dependency bumps,
certificate rotation, clearing a queue. It is not a defect - nothing is
violated. It is not a decision each time - nobody decides weekly.

The resolution is that **the recurrence was decided once.** "Dependencies are
upgraded weekly and a failing upgrade opens a defect" is a decision, recorded
once, and each execution is L0 work under it. The decision is what carries the
reasoning - why weekly, what happens when it breaks - and the executions carry
nothing because there is nothing to carry.

This is the same shape as `meowhub`'s treatment of anything that accumulates: a
standing obligation needs a drain and a ceiling
([RES-0017-design-lenses.md](RES-0017-design-lenses.md)), and the decision is where those are
stated.

## The vocabulary, term by term

The backlog world's words, what each actually means, and whether this model
needs it.

Story. A feature stated from the user's side - "as a X, I want Y, so that
Z". Its value is not the format; it is the **question the format forces**: who
wants this, and what do they get? That question is answered in research and in
the vision, and a requirement that traces to neither is a requirement nobody
asked for. **Not needed as a type; needed as a question**, which
[RES-0028-requirements.md](RES-0028-requirements.md) already places - a user story captures _why_
and never substitutes for a requirement.

Spike. A time-boxed investigation to reduce uncertainty about how something
might be delivered, feeding back into refinement. **That is the research step**,
and it already produces a permanent, dated artifact. Making it a work type would
create a second way to produce evidence, with one of them exempt from citing
sources.

Chore / refactor. Work with no visible user feature. Authorised by a
decision like anything else; the decision is where the reason lives, which is
exactly what a chore label omits and what makes chores accumulate unexamined.

Technical debt. Not work at all until someone decides to pay it - it is an
observation. It belongs in the development log, or as a defect where it violates
something in force. A backlog of debt items nobody decided on is a list of
regrets.

Epic. Kept, and redefined: it realises exactly one authorising record. The
common meaning - "a big story" - has no end condition, which is precisely the
problem.

Task. Kept. One task, one branch, one pull request, one review.

Feature, enhancement, improvement, change request. Four names for "new
behaviour somebody decided on". One record covers them.

So the model keeps **two** of the field's nouns - epic and task - and replaces
the rest with two records that say who authorised the work.

## What the model does not have, and why that is right

No work-type taxonomy. The backlog view has six to twelve types; this model
has tasks, and the type is a consequence of what authorised them. A taxonomy
would have to be maintained, argued about at the boundaries - is a refactor a
chore or debt? - and would classify by appearance rather than by anything
actionable.

The field's own guidance concedes the point indirectly: "a work item type groups
items that behave similarly and follow the same workflow". Under this model
every task follows the same workflow, so the grouping has nothing to do.

No classes of service. Urgency is priority, which lives in planning rather
than on the record ([RES-0033-defects.md](RES-0033-defects.md)).

No separate spike type. A spike is research, and giving it its own type
would create a second way to produce evidence.

## Conclusions

1. Two authorising records are enough. Every type in both taxonomies routes
   through a decision or a defect.
2. Requirements are about observable behaviour, not about products. That is
   what lets pipelines, infrastructure and designs through the same chain.
3. Recurrence is decided once and executed many times, which is what covers
   routine work without a third record kind.
4. The model deliberately has no work-type taxonomy, because the type is
   derivable and a maintained taxonomy is a boundary argument that never ends.

## Sources

All read 2026-09-20.

- [The four types of work](https://www.oreilly.com/library/view/the-phoenix-project/9781457191350/46-resourceFour.xhtml),
  _The Phoenix Project_ - business projects, internal projects, changes and
  unplanned work.
- [The Phoenix Project and its four types of work](https://apsuedonym.medium.com/the-phoenix-project-and-its-four-types-of-work-21cca861bd16)
  and [4 types of work](https://klotzandrew.com/blog/4-types-of-work/) - the
  characterisation of internal work as invisible, and of unplanned work as
  recovery that displaces goals.
- [Classes of service and work item types](https://kanbantool.com/kanban-guide/classes-of-service),
  Kanban Guide - work item types as kinds of demand, and the distinction between
  a type and a class of service.
- [Agile ticket types: story, spike, bug, epic](https://medium.com/@qingedaig/agile-ticket-types-story-spike-bug-epic-etc-adbdd796e3e2)
  and [The 6 backlog item types](https://edwardearle.medium.com/the-6-backlog-item-types-bdd2e1ab450)
  - the engineering taxonomy, including spike as a time-boxed investigation and
    chore as work with no visible user feature.
- [Understanding agile work items](https://www.agilepal.co.uk/article/understanding-agile-work-items-spike-user-story-task-and-bug)
  - spikes feeding back into backlog refinement.
