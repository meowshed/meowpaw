---
id: RES-0252
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0071, RES-0253
---

# The specification template

## Summary

Both published forms describe a document written once about a system being
built, and this one is rewritten for as long as the system exists. Five of the
twelve architecture sections carry over, and the rest belong elsewhere in this
method. The rule behind that division is that a specification states what is
true now and everything about why belongs to a decision. Describing the present
means updating removes as well as adds.

Research for the shape of a specification document: which sections it has, what
the two published forms put in them, and what changes because this
specification describes the present rather than a proposed change.

One of nine template documents, one per artifact kind in the record.

It does not cover how finely the specification divides, which is
[RES-0071-specification-granularity.md](RES-0071-specification-granularity.md),
nor the command that writes one, which is
[RES-0153-spec-command.md](RES-0153-spec-command.md).

## The question

The published forms are both for a document written once about a system being
built. This one is rewritten for as long as the system exists, and divides by
the system's own parts.

So the question is which sections survive that change of lifetime, and which
are artefacts of writing a specification before there is anything to describe.

## Method

We fetched and read the architecture template on 2026-09-20 for its twelve
sections and what each holds. We fetched the requirements standard's template
documentation for what it fixes and what it leaves to the project.

The standard's own text was not obtained; the statement that section order is
the project's to choose comes from the vendor documentation describing it.

The granularity rules come from research already in this corpus rather than
from a new source. Nothing was measured.

## Findings

### The architecture form is a fixed question set, and that is its whole value

Twelve sections: introduction and goals, constraints, context and scope,
solution strategy, building block view, runtime view, deployment view,
crosscutting concepts, architectural decisions, quality requirements, risks and
technical debt, glossary. The building block view is _"usually the most
extensive section"_ and is hierarchically refined.

For a document about a part of a system, five of those carry over directly and
the rest belong elsewhere in this method.

| Section                  | Here                                             |
| ------------------------ | ------------------------------------------------ |
| Context and scope        | Yes - what this part is, and its boundary        |
| Building block view      | Yes - what it is made of, refined                |
| Runtime view             | Yes - what happens when it runs                  |
| Crosscutting concepts    | Yes, where they are this part's                  |
| Quality requirements     | Yes, as refinements of the shared baseline       |
| Constraints              | Yes, where they bind this part                   |
| Introduction and goals   | No - the vision holds this                       |
| Solution strategy        | No - decisions hold this                         |
| Architectural decisions  | No - referenced, not restated                    |
| Deployment view          | Where it is the subject, as a part of its own    |
| Risks and technical debt | No - the vision and the defect record hold these |
| Glossary                 | Once for the project, not per part               |

The rule behind that column is the one this method already uses: **a
specification states what is true now, and why or how it was chosen belongs to
a decision.** A specification restating its decisions creates two copies, and
the one nobody checks is the one people read.

### The requirements form contributes attributes rather than sections

The requirements-engineering standard defines a family of specification
documents and leaves the section order to the project. _"Organization of the
content such as the order and section structure may be selected in accordance
with the project's information management policies."_

What it fixes instead is that every statement is traceable and every
requirement carries its attributes. That is the part this method takes: the
trace is what makes the specification correct, and the file boundary is a
convenience for readers.

So the template is permitted to be shorter than either published form, provided
the trace holds.

### Describing the present changes three things

Every statement is in the present tense and is true now. A specification
that says _will_ is a plan; one that says _used to_ is a history. Both belong
elsewhere.

Updating removes. A living document that only grows becomes a superset of
every state the system has ever been in. This is the obligation most often
skipped, because adding is easy to review and removing looks like loss.

The document never completes, which removes the usual specification failure of
being written once and abandoned, and introduces a different one: nobody
notices when it stops being true. That is what the corpus check for coverage in
both directions is for - no statement without a requirement in force, and no
requirement in force without a statement.

### One subject a reader can name

The division test from the granularity research is the template's first rule:
**a specification document has one subject a reader can name**. A reader with a
question about that subject finds the answer in one document.

Which gives the title rule: the title is the subject, not a folder name. A
document called _Core_ fails the test; one called _Verb resolution_ passes it.

### Nesting, and the part that trips people

The division nests: a part with parts is described at both levels. The
template question that follows is what the parent document holds that the
children do not.

The answer that works: **the parent holds what is true of the part as a whole
and the contract between its children**, and nothing that belongs to one child.
A parent that summarises its children is a third copy that drifts.

### The sections it carries

| Section                   | Holds                                                                 | Mandatory        |
| ------------------------- | --------------------------------------------------------------------- | ---------------- |
| Front matter              | Identifier, kind, status `live`, revision date, the part it describes | Yes              |
| Title                     | The subject, nameable in a phrase                                     | Yes              |
| What this is              | One paragraph: the part's job and its boundary                        | Yes              |
| What it is made of        | The structure, refined where it nests                                 | Yes              |
| How it behaves            | The runtime view: what happens when it is used, including on failure  | Yes              |
| Interfaces                | What it offers and what it requires, where either is a contract       | Where applicable |
| Constraints and qualities | The refinements of the shared baseline that bind this part            | Where applicable |
| Decisions                 | Links to the decisions that shaped it, never restated                 | Yes              |

Nothing else. No rationale, no history, no roadmap, no requirement text
duplicated from the requirements.

### What the template must refuse

A statement with no requirement in force behind it, because a specification
is not where a new obligation is introduced.

A requirement in force that nothing states, which is the same check in the
other direction and is the one that silently fails.

A restated decision.

A tense other than the present.

A summary of a child document.

## Conclusions

1. A specification document has one subject a reader can name, and its
   title is that subject rather than a folder name.
2. It describes the present in the present tense, and a statement about the
   future or the past belongs to a decision or to history.
3. Updating removes as well as adds, because a living document that only
   grows becomes a superset of every state the system has had.
4. It states what the part is, what it is made of, how it behaves, and what
   it offers and requires - and nothing about why it was chosen.
5. Decisions are linked and never restated, since a second copy drifts and
   the unchecked one is the one people read.
6. Quality statements refine the shared baseline rather than reinventing
   it, and a deviation says so.
7. A parent document holds what is true of the whole and the contract
   between its children, and never summarises a child.
8. Coverage is checked in both directions: no statement without a
   requirement in force, and no requirement in force without a statement.
9. Section order is the project's to choose, as the standard permits, so
   the template is shorter than either published form and the trace is what
   makes it correct.
10. Goals, strategy, risks and the glossary live elsewhere - in the vision,
    the decisions, the defect record and one project-wide place.

## Sources

All read 2026-09-20.

- [arc42 overview](https://arc42.org/overview) - the twelve sections and what
  each contains, with the building block view named as usually the most
  extensive and hierarchically refined, and crosscutting concepts, quality
  requirements, risks and technical debt, and the glossary as sections of their
  own.
- [ISO/IEC/IEEE 29148 requirements specification templates](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
  - the family of specification documents the standard defines, the requirement
    attributes it fixes, and the statement that section order and structure may
    be chosen according to the project's own information management policies.
- [RES-0071-specification-granularity.md](RES-0071-specification-granularity.md)
  - division by the system's own parts, the nesting rule, the one-subject test,
    and the trace as what makes the specification correct while the file boundary
    serves the reader.
- [RES-0153-spec-command.md](RES-0153-spec-command.md) - the present-tense
  rule, that updating removes, and the coverage check in both directions.
