---
id: RES-0257
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0068, RES-0256
---

# The task template

## Summary

A task is read by an agent that was not present for any of the discussion that
produced it, which the published forms do not assume. So it is self-contained,
carrying enough and duplicating nothing, and its criteria are observable. The
field the published forms lack is the one that matters most here: what evidence
will close each criterion, named in advance, because evidence chosen afterwards
is always evidence the work happened to produce.

Research for the shape of a task: the unit of work an agent is dispatched with,
and the record its evidence is measured against.

One of nine template documents, one per artifact kind in the record.

It does not cover how a task is verified, which is
[RES-0068-verifying-a-task.md](RES-0068-verifying-a-task.md), nor the
decomposition it comes from, which is
[RES-0256-the-epic-template.md](RES-0256-the-epic-template.md).

## The question

A task here is read by an agent that was not present for any of the discussion
that produced it. The published forms assume a person who was.

So the template asks two questions. What the document needs for a reader with
no context to do the work correctly, and what it needs for the result to be
checkable afterwards.

## Method

We fetched and read the published item form and the definition-of-done material
on 2026-09-20. The survey finding that three harnesses independently dispatch
from a written brief and never from a conversation came from the synthesis
already in this corpus.

The user-story framing was read and deliberately rejected, and the document
records the reason, leaving no omission for a reader to wonder about.

Nothing was measured, and no task was dispatched to test whether a
self-contained brief produces better work.

## Findings

### A written brief beats a conversation, and three harnesses found this separately

The survey's finding is that the task's artifacts are the source of
requirements, and the conversation is not. One harness dispatches a fresh
implementer per task with a written brief, the interfaces from earlier tasks
and a report contract, and explicitly no session history. Another runs an
independent reviewer per task in a clean context. A third puts rationale,
constraints and embedded tests in the item so the implementer needs no prior
context.

That decides the template's first property: **a task is self-contained.** A
task that makes sense only after reading the epic, the decision and three other
tasks will be done wrongly by whoever reads it fresh, and under delegation that
is everyone.

Self-contained does not mean duplicated. It means the task carries what is
needed to do the work: the requirements it must satisfy by identifier, the
interfaces it must use or provide, and the constraints that bind it.

### The published item form contributes two things and one trap

The standard item is a user story with acceptance criteria in a
given-when-then form, sized to fit one iteration, and tested against the INVEST
properties - independent, negotiable, valuable, estimable, small, testable.

Given-when-then transfers. It forces a precondition, an action and an
observable outcome, which is exactly the shape a check has to take. Criteria
written as a list of adjectives are not checkable.

Independent and small transfer, and are the properties the decomposition is
tested against.

The user-story sentence is the trap. _As a user, I want_ is a framing for work
whose value is user-visible. A task implementing a parser, a check or a
migration has no user in the sentence. Forcing one produces the familiar
contortion, _as a developer, I want the code to work_, which carries no
information. This method has the value statement upstream, in the decision and
the epic, so the task does not need to reproduce it.

### Acceptance criteria per task, definition of done per repository

The same division as at the epic level, and the same correction to this
corpus's current practice.

The shared definition of done applies to every task and is declared once for
the repository. The acceptance criteria are this task's, and are what the
evidence is measured against.

So a task states its criteria and references the shared definition. A task that
restates the definition produces a copy that drifts from the repository's.

### The evidence contract is what makes a task verifiable

Task verification asks whether the evidence closes the requirements the task
cited. That only works if the task said, in advance, what evidence would close
them.

The published forms have no equivalent for that field, and it decides more here
than any other: **what will be true, and what will show it.** A verb and its
result, a fixture that fails without the change, a measurement against a stated
threshold.

Writing it in advance prevents the failure that this method exists to stop:
evidence chosen after the work, which is always evidence the work happens to
produce.

### Dependencies, and the honest default

A task declares what it depends on. A task with nothing declared is claiming it
can start immediately, which is a statement somebody can check, where an
absence says nothing.

The dependency list is also what orders the proposals, so getting it wrong is
not a planning inconvenience - it produces a proposal whose base is not yet
merged.

### What a task must not contain

Reasoning. It is in the decision.

A restated requirement. Cited by identifier, so the one copy stays
authoritative.

An estimate, for the same reasons as at the epic level.

A status field. Whether a task is done is derived from its evidence.

Instructions for how to implement it, beyond the constraints that bind the
result. A task that prescribes the implementation has moved the design into the
plan, where it is not reviewed as a design.

### The sections it carries

| Section               | Holds                                                                                              | Mandatory        |
| --------------------- | -------------------------------------------------------------------------------------------------- | ---------------- |
| Front matter          | Identifier, kind, status, revision date, the epic, the requirements it satisfies, its dependencies | Yes              |
| Title                 | What will be true when this is done                                                                | Yes              |
| What is being changed | The scope, in the tree's terms                                                                     | Yes              |
| Acceptance criteria   | Given, when, then - observable                                                                     | Yes              |
| Evidence              | What will show each criterion holds, named in advance                                              | Yes              |
| Interfaces            | What it must use or provide, where another task depends on it                                      | Where applicable |
| Constraints           | What binds the result without prescribing the implementation                                       | Where applicable |
| Done                  | A reference to the repository's definition                                                         | Yes              |

### What the template must refuse

A task citing no requirement, which is work nothing authorised.

A criterion that is not observable.

Evidence named after the work.

A task large enough that its proposal will not be reviewed, which is the size
rule arriving from the reviewer's side.

## Conclusions

1. A task is self-contained, carrying what a reader with no context needs,
   because the implementer is dispatched with the document and never with the
   conversation. 2. Self-contained means it carries enough and duplicates
   nothing: requirements are cited by identifier and never restated. 3.
   Acceptance criteria are written as given, when, then, so each is observable,
   where an adjective is not. 4. The evidence that will close each criterion is
   named in advance, since evidence chosen afterwards is evidence the work
   happened to produce. 5. The shared definition of done is referenced, and
   never restated. 6. The user-story sentence is not used, because the value
   statement lives in the decision and the epic and forcing it here produces a
   contortion. 7. Dependencies are declared, and none declared is a claim that
   it can start now. 8. A task carries no reasoning, no restated requirement,
   no estimate and no status. 9. A task does not prescribe its implementation,
   beyond the constraints that bind the result, or the design has moved into
   the plan where it is not reviewed as one. 10. A task citing no requirement
   is refused, being work nothing authorised. 11. A task is small enough that
   its proposal gets reviewed, and never merely approved, which is the size
   rule seen from the reviewer's side.

## Sources

All read 2026-09-20.

- [What is a definition of
  done?](https://www.scrum.org/resources/what-definition-done) and [The
  difference between the definition of done and acceptance
  criteria](https://www.scrum.org/resources/blog/what-difference-between-definition-done-and-acceptance-criteria)
  - the shared definition of done against per-item acceptance criteria, and the
    difference in when each is applied. - [SAFe user stories and
    INVEST](https://agility-at-scale.com/safe/lpm/epics/) - the story form sized
    to one iteration, the INVEST properties, and acceptance criteria in the
    given-when-then form. - [RES-0001-synthesis.md](RES-0001-synthesis.md) -
    finding five, that a written brief beats a long conversation, with three
    harnesses arriving at it independently, and the task's artifacts being the
    source of requirements where the session is not. -
    [RES-0068-verifying-a-task.md](RES-0068-verifying-a-task.md) - the two
    completion tests and evidence measured against the requirements the task
    cited. - [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the finding
    that review effectiveness falls with the size of what is reviewed, which is
    where the task size rule comes from.
