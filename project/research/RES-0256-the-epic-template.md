---
id: RES-0256
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0055, RES-0069
---

# The epic template

## Summary

The published form writes an epic as a hypothesis, and two of its mechanisms
transfer. One is an early indicator, because a success measure available only
at the end cannot steer the work. The other is the smallest responsible test,
as the decomposition rule. What does not transfer is the proposal framing,
since the decision is already approved. The acceptance criteria are written
from that decision before the tasks, or verifying the epic verifies the plan
against itself.

Research for the shape of an epic: the record that decomposes one approved
decision into tasks, and the thing epic verification is measured against.

One of nine template documents, one per artifact kind in the record.

It does not cover the command that writes one, which is
[RES-0055-epic.md](RES-0055-epic.md), nor how one is verified, which is
[RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md).

## The question

An epic here has one job the published forms do not give it: it is what
verification compares the finished work against when asking whether the
decision behind it was realised.

So its template is not a planning form. It is the statement of what realising
this decision looks like, plus the decomposition.

## Method

The published epic form and the definition-of-done material were fetched and
read on 2026-09-20, the second specifically for the distinction between a
shared definition and per-item criteria, which this corpus had been loose
about.

This corpus's own practice was read against it, which is how the finding that
it requires a definition of done on every epic and task - two obligations under
one name - was reached.

Nothing was measured, and no epic was verified as an experiment.

## Findings

### The published form is a hypothesis, and that framing transfers

The scaled-agile form writes an epic as a hypothesis with fixed slots. **For**
the users, **who** have a problem, **the** proposed solution, **will** deliver
these benefits, and **we will know we are successful when**, followed by
measurable outcomes.

Two mechanisms come with it.

Leading indicators. The guidance separates them from business outcomes,
which are _"lagging indicators that only start moving once the work has been
done"_, and requires at least one indicator measurable early. The distinction
transfers exactly: an epic whose only success measure is available after
everything is built cannot be steered while it is being built.

The smallest responsible test. In that form the minimum viable product is
_"a pivot point where enough work has been done to test the hypothesis"_ -
explicitly not a small release. That is the decomposition rule stated as a
question: which subset of these tasks would tell us whether the decision was
right?

### Where the hypothesis framing does not fit, and why

Here an epic does not propose anything. It realises a decision that was already
argued and approved, so the _why_ and the alternatives live upstream and
restating them creates a second copy.

What survives is the last slot: **we will know we are successful when.** That
is the acceptance criteria, and this method defines it more sharply than the
published form does: what the authorising decision would recognise as realised.

Which connects to the finding this template exists to serve: every way a
decomposition can be wrong survives task verification untouched. Tasks can each
be complete and the decision unrealised - a missing task, a task that
implemented something adjacent, a task whose evidence closed a requirement the
decision did not mean.

So the acceptance criteria are written **from the decision, before the tasks
are written**. Written afterwards, they describe the decomposition, and then
verifying the epic against them verifies the plan against itself.

### Acceptance criteria and the definition of done are different things

The published position is clear and this corpus has been loose about it.

The definition of done is _"a formal description of the state of the Increment
when it meets the quality measures required for the product"_, created
collaboratively and shared across every item. Acceptance criteria are
_"conditions that a specific Product Backlog Item must meet"_, tailored to that
item.

The difference in use is the part that matters: the shared definition is
applied at the end to ask whether work is complete, and the per-item criteria
guide development and testing throughout.

This corpus requires a definition of done on every epic and every task. Read
against the above, that is two different obligations wearing one name:

- **The shared definition of done belongs to the repository**, declared once,
  applying to every unit of work. Restating it per epic produces copies that
  drift, and the drift is invisible because each copy looks reasonable.
- **Acceptance criteria belong to the epic**, and are specific to the decision
  being realised.

So the template carries acceptance criteria and **references** the repository's
definition of done, restating none of it. One exception: an epic may _add_ to
the shared definition where its work needs something extra, and the addition is
marked as an addition.

### The decomposition is the other half, and its shape is a dependency graph

Tasks with dependencies declared, because the order is a property of the work
rather than of the list. A linear list of tasks hides which of them could have
been done in parallel and which cannot start.

Two template rules follow from the stacked-proposal research. The dependency
order decides the proposal order, and a task with no dependency declared is
claiming it can start now, which is a statement somebody can check.

### What an epic must not contain

The reasoning. It belongs to the decision.

Requirements. They are cited, not restated.

Estimates. They are scheduling, they go stale, and nothing downstream reads
them.

A status per task. Whether a task is done is derived from the task and its
evidence, and a second copy in the epic is the classic drift this method exists
to prevent.

### The sections it carries

| Section                        | Holds                                                                                        | Mandatory        |
| ------------------------------ | -------------------------------------------------------------------------------------------- | ---------------- |
| Front matter                   | Identifier, kind, status, revision date, the decision it realises, the requirements in scope | Yes              |
| Title                          | What this epic realises, as a statement                                                      | Yes              |
| What realising this looks like | The acceptance criteria, written from the decision                                           | Yes              |
| Early indicator                | What can be measured before everything is built                                              | Where one exists |
| Done                           | A reference to the repository's definition, plus any addition, marked                        | Yes              |
| Tasks                          | The decomposition, each with its dependencies                                                | Yes              |
| Out of scope                   | What this epic deliberately does not do                                                      | Yes              |

## Conclusions

1. One epic realises one decision entirely, which is possible because the
   decision was required to be a complete story; an epic that realises part of
   a decision is a sign the decision was a fragment.
2. The acceptance criteria are written from the authorising decision before
   the tasks are written, or verifying the epic verifies the plan against
   itself.
3. They state what the decision would recognise as realised, which is what
   epic verification is measured against.
4. An epic names at least one thing measurable before the work is finished
   where one exists, because a success measure available only at the end cannot
   steer the work.
5. The decomposition identifies the smallest subset that would test the
   decision, which is the published form's pivot point stated as a question.
6. The definition of done is the repository's and is referenced, not
   restated, since copies drift invisibly.
7. An epic may add to the shared definition, and marks the addition as an
   addition.
8. Acceptance criteria are per epic and the definition of done is shared,
   and the two are not the same obligation under one name.
9. Tasks declare dependencies, because the order is a property of the work
   and a task with none declared is claiming it can start now.
10. The epic restates no reasoning and no requirement, citing both instead.
11. It carries no estimates and no per-task status, the first being
    scheduling and the second a second copy of a derived fact.
12. It states what it deliberately does not do, so a later reader can tell
    an omission from a boundary.

## Sources

All read 2026-09-20.

- [SAFe epics and the epic hypothesis statement](https://agility-at-scale.com/safe/lpm/epics/)
  and [Lean business case and epic hypothesis](https://agileseekers.com/blog/lean-business-case-epic-hypothesis-and-mvp-evidence-in-safe)
  - the fixed slots of for, who, the solution, the benefits and how success
    will be known; leading indicators as early measurements separated from
    lagging business outcomes, with at least one required early; and the minimum
    viable product as a pivot point where enough work has been done to test the
    hypothesis rather than a small release.
- [What is a definition of done?](https://www.scrum.org/resources/what-definition-done)
  and [The difference between the definition of done and acceptance criteria](https://www.scrum.org/resources/blog/what-difference-between-definition-done-and-acceptance-criteria)
  - the definition of done as a formal description of the increment's state
    created collaboratively and shared; acceptance criteria as conditions
    specific to one item; and the difference in use, the shared definition
    applied at the end and the per-item criteria guiding the work throughout.
- [RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md) - that every
  way a decomposition can be wrong survives task verification untouched.
- [RES-0255-the-decision-template.md](RES-0255-the-decision-template.md) - the
  requirement that a decision be realisable as a complete story, which is what
  makes one epic per decision achievable.
- [RES-0055-epic.md](RES-0055-epic.md) - the decomposition into tasks with
  dependencies and the approval that precedes filing them.
- [RES-0065-stacked-pull-requests.md](RES-0065-stacked-pull-requests.md) - that
  dependency order decides proposal order.
