---
id: RES-0153
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0071, RES-0011
---

# `/meow:spec`

## Summary

Nobody in the survey has this step in this sense. Every other harness's
specification command produces a record of a proposed change, and this one
describes the system as it now stands. That distinction is why it exists - a
pile of change records answers what was decided and cannot answer what the
system does now without reading all of them in order. It divides by the
system's own parts, and updating it removes as often as it adds.

The step that writes the living specification: what the system must do now,
divided by the system's own parts, traced to the requirements in force.

It is the only step in the chain whose output is not a record. Everything else
freezes when it is finished; this document is rewritten for as long as the
project exists.

## Who has an equivalent

Nobody, in this sense.

Every surveyed harness has a command called `spec` or `specify`, and in all of
them it produces a _record of a change_ - what this feature must do - rather
than a description of the system as it now stands. spec-kit's `specify` writes
a feature specification; cc-sdd's `spec-requirements` writes requirements for a
change; meowctl's `/spec` writes a change document.

The internal precedent is meowctl's `docs/spec/`, which holds one living
document per component, elaborated by many changes over time. That is the shape
this step produces, and it is the only place in the survey where a
specification describes the present, where every other one is a proposal.

The distinction is the reason the step exists. A pile of change records answers
_what did we decide_ and cannot answer _what does this do now_ without reading
all of them in order.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The division is by part, and the parts are the project's

The specification is too large to be one document in any project large enough
to need one, so it divides. It divides by **the system's own parts**, and the
repository declares what its parts are.

Packaging is the wrong divider and was the first attempt. A project may be
split into parts and still install as one thing; a monolith with a dozen
modules has one unit of installation and a specification that plainly needs
dividing. And keying on packaging bakes a deployment decision into the place
that is supposed to be free of it.

A contract spanning several parts gets a document of its own, as a first-class
section that needs no exception.

The division nests: a part with parts is described at both levels, and nothing
flattens or scatters it.

## The test for a division is a reader

Two halves. **A specification document has one subject a reader can name**, and
a reader with a question about that subject finds the answer in one document,
never assembling it from three.

A division that fails the first is a folder with a file extension. One that
fails the second is a filing system.

Neither standard consulted gives a size limit, and neither should.

## Why granularity can be revised without the specification becoming wrong

Every statement traces to a requirement in force, and every requirement in
force is stated somewhere. So moving a statement between documents cannot lose
it and cannot duplicate it.

The file boundary is a convenience for readers; the trace is what makes the
specification correct. That is what allows the division to be revised later
without an interval in which the specification is wrong.

The one thing that cannot be revised is an identifier. A specification
document's identifier is permanent once cited, so identifiers are allocated to
subjects, since a package may be renamed and a subject is what the reader was
asking about.

## What the step does on a change

This is the part that distinguishes it from every record-producing step. The
command runs when a decision has been realised, and its job is to **update the
description of the present** - which means deleting sentences as often as
adding them.

A living document that only grows is a change log with a misleading title. The
step that does not remove what is no longer true produces a specification that
is a superset of every state the system has ever been in.

## What it must refuse

A statement with no requirement behind it, because a specification is not where
a new obligation is introduced.

A requirement in force that nothing states, which is the coverage question in
the other direction.

A history. _We used to do X, now we do Y_ belongs in the decision that changed
it. The specification says what is true now.

## Conclusions

1. The specification describes the present, and is the only living artifact the
   chain produces. 2. It divides by the system's own parts, which the
   repository declares, and never by how the system is packaged. 3. A contract
   spanning several parts gets its own document, as a first-class section that
   needs no exception. 4. The division nests, so a part with parts is described
   at both levels. 5. A specification document has one subject a reader can
   name, and a reader with a question about it finds the answer in one
   document. 6. The trace makes the specification correct and the file boundary
   serves the reader, so granularity can be revised without an interval of
   incorrectness. 7. Identifiers are allocated to subjects, because an
   identifier is permanent and a package name is not. 8. Updating removes as
   well as adds, since a living document that only grows is a change log with
   the wrong title. 9. No statement without a requirement in force, and no
   requirement in force without a statement. 10. History belongs in the
   decision that changed things, and the description of the present carries
   none of it.

## Sources

All read 2026-09-20.

- [RES-0071-specification-granularity.md](RES-0071-specification-granularity.md)
  - the division by parts, where packaging divides nothing, the nesting, the
    two-part reader test, the trace as what makes the specification correct, and
    identifiers allocated to subjects. -
    [RES-0011-artifact-lifecycle.md](RES-0011-artifact-lifecycle.md) - the
    permanent-against-living distinction and what a living document owes. -
    `~/workspace/meowctl/docs/spec/` - the internal precedent of one living
    specification document per component, elaborated by many changes over time. -
    [github/spec-kit](https://github.com/github/spec-kit) and
    [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - specification commands
    that produce a record of a change and describe no system, read here as the
    contrast that defines this step.
