---
id: RES-0152
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0072, RES-0052
---

# `/meow:design`

## Summary

The step that turns approved requirements into decisions, one per coherent
block. Three questions from the surveyed sequence belong in it and were absent
from the first draft: state the non-goals, ask what would be regretted later,
and record what would reverse the decision. The previous design is read as
history and never as a starting point, because a design in front of a model is
something the model extends.

The third step of the chain. It takes approved requirements and produces
decisions - one per coherent block of requirements - and stops for approval.

Its siblings are [RES-0052-chain.md](RES-0052-chain.md) and
[RES-0151-requirements-command.md](RES-0151-requirements-command.md).

## Who has an equivalent

| Harness        | Command       | Output                                         |
| -------------- | ------------- | ---------------------------------------------- |
| spec-kit       | `plan`        | `data-model.md`, `contracts/`, `quickstart.md` |
| cc-sdd         | `spec-design` | A design carrying a file structure plan        |
| harness4claude | `design-doc`  | One document                                   |
| vlie           | `/design`     | One document with options and trade-offs       |

spec-kit is the one that outputs several artifacts, which is right where the
system has an interface: a contract is a different kind of thing from a
rationale and is read by different people.

## Method

We read the surveyed harnesses' own command templates and the internal
repositories' commands on 2026-09-20 for what a comparable command does. We
fetched the platform's command documentation for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The three questions vlie asks that the others do not

vlie's sequence runs like this. Read the current documentation, and use
research and any frozen initial design **as historical context only**. Define
problem, consumers, invariants, non-goals and failure modes. Ask why it must
exist, what the simplest viable design is, and **what would be regretted
later**. Compare at least three options for non-trivial decisions, then state
the chosen approach, the rejected ones, the trade-offs and the revisit
conditions.

Three of those belong in this command and were absent from the first draft of
it.

Non-goals, stated explicitly. A design without them is a design whose scope
is whatever a reader assumes, and the first argument about it is about
something it never claimed.

What would be regretted later. This is a premortem in one line, and it is
placed where a premortem is cheapest - before anything is built.

Revisit conditions. A decision that cannot say what would reverse it is
either obvious or unfalsifiable. Recording the condition turns a decision into
something that can later be shown to have expired.

## Reading the previous design as history

vlie's phrasing - _historical context only_ - transfers directly, because the
failure it prevents is subtle. An earlier design in front of a model is
something the model will extend, and extending a design nobody re-derived is
how a structure accumulates decisions that no longer fit the requirements.

So the input to this step is the requirements. The previous design is evidence
about what was once believed, and it starts nothing.

## Progressive enhancement is what makes the output a series

This command does not produce one design. It produces a series of decisions
where **each leaves the system working**: a skeleton first, then layers.

That changes what a good decision looks like. A decision realisable only
together with three others is no layer. It is a quarter of one, and it gets
approved with nobody able to picture the state after it.

It also changes the review question. The question is not _is this design
right_, it is _does the system work after this one_, which is answerable.

## Where the architecture lives

A decision says what was chosen and why; a requirement says what must be true.
Neither carries structure - what the system is made of, how its parts depend on
each other, which dependencies are allowed.

So this step also produces the architecture description, organised by concern,
with the allowed dependencies stated, and nothing left implied. An import that
crosses a forbidden boundary is then a finding nobody argues about, which is
what makes it checkable, and a review can be given the structure as well as the
diff.

## What it must refuse

A decision with no requirement behind it, because that is a preference.

A requirement with no decision addressing it is the coverage question in the
other direction, and the one that goes unnoticed. A design looks complete while
leaving a requirement unaddressed, and only a count finds it.

A decision that mixes abstraction levels, for the same reason a document does
not mix kinds. The level is named before the description is written.

## Conclusions

1. The input is the requirements, and any previous design is read as historical
   context that starts nothing. 2. Non-goals are stated explicitly, so the
   design's scope is written rather than assumed. 3. The command asks what
   would be regretted later, which is a premortem at the point where it costs
   least. 4. Every decision records what would reverse it, or it cannot later
   be shown to have expired. 5. At least three options are compared for a
   non-trivial decision, with the rejected ones and their trade-offs recorded,
   and none of them discarded. 6. Decisions form a series in which each leaves
   the system working, so a reviewer can picture the state after each one. 7. A
   decision that can only be realised together with several others is merged
   with them, because it cannot be approved on its own terms and cannot say
   what works after it. 8. Each decision states what the system does after it
   that it did not do before, which is the test that it is a complete story,
   and is recorded in
   [RES-0255-the-decision-template.md](RES-0255-the-decision-template.md). 9.
   The step produces the architecture description, organised by concern, with
   allowed dependencies stated so a crossing is a finding. 10. The abstraction
   level is named before the description is written, and one description does
   not mix two. 11. Coverage is checked in both directions: no decision without
   a requirement, and no requirement without a decision. 12. Output may be
   several artifacts where the system has an interface, since a contract and a
   rationale are different kinds read by different people. 13. The command
   refuses on missing or unapproved requirements and stops after producing.

## Sources

All read 2026-09-20.

- `~/workspace/vlie/.claude/commands/design.md` - reading research and a frozen
  initial design as historical context only; problem, consumers, invariants,
  non-goals and failure modes; the questions why it must exist, what the
  simplest viable design is and what would be regretted later; at least three
  options for non-trivial decisions; and the chosen approach with rejected
  ones, trade-offs and revisit conditions.
- [github/spec-kit `plan.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/plan.md)
  - that spec-kit's `plan` is a design command producing `data-model.md`,
    `contracts/` and `quickstart.md`, and the precedent of a step whose output is
    several artifacts.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - a design carrying a
  file structure plan.
- [RES-0072-architecture-discipline.md](RES-0072-architecture-discipline.md) -
  the architecture description, its organisation by concern, and allowed
  dependencies as the checkable part.
- [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the questions a
  design must answer before it is approved.
