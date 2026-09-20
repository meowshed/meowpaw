---
id: RES-0071
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# How finely the specification divides

## Summary

The specification had been divided one document per unit of installation, and
that key is wrong. A project may be split into parts and still install as one
thing, and packaging is a property not every project has. The
architecture-description standards divide by concern instead and treat
deployment as one concern among several. The test for a division is a reader -
one nameable subject, and one document per question.

Research for the granularity of the specification tree. The method currently
divides it one document per unit of installation, plus one per contract that
spans several. That key is wrong, and this document is about what replaces it.

It covers why packaging is the wrong divider, what the architecture-description
standards divide by instead, and what test decides whether a division is right.
It does not cover what a specification contains, which is
[RES-0011-artifact-lifecycle.md](RES-0011-artifact-lifecycle.md), nor that it
is project-level, which is [RES-0035-vision.md](RES-0035-vision.md).

## The question

A living specification says what the system must do now. It is too large to be
one document in any project large enough to need a specification, so it
divides.

The question is what it divides by, and the answer has to hold for a project
that ships as thirty installable plugins and for one that ships as a single
binary.

## Method

The two architecture-description standards were fetched and read on
2026-09-20 for how each organises a description and what each says about
deployment's place in it.

The internal precedent was read from its working tree: one repository already
keeps a living specification document per component.

Nothing was run. The conclusion that the old key fails was reached by applying
it to this project and to a hypothetical monolith, which is reasoning rather
than measurement.

## Findings

### Packaging is not a property every project has

The current key fails on the ordinary case. **A project may be split into parts
and still install as one thing.** A monolith with a dozen modules has one unit
of installation and a specification that plainly needs dividing; keyed on
installation it would be one document, which is the state the division existed
to avoid.

It fails on this project too, in a subtler way. The unit of installation here
is the plugin, and **the plugin catalogue is explicitly a proposal that nobody
has decided**. Keying the normative documents on an undecided packaging means
the specification churns whenever packaging is reconsidered, and every
identifier allocated against it is allocated against a guess.

It also bakes a decision into the wrong artifact. A requirement states what
must be true and never how to achieve it, and packaging is a how. A
specification tree keyed on packaging has decided the deployment shape in the
place that is supposed to be free of it.

The clause that was meant to patch this - _plus one per contract that spans
several_ - is the admission. If a substantial share of the specification cannot
be filed under any package, the package is not the key.

### The standards divide by concern, and treat packaging as one concern among several

ISO/IEC/IEEE 42010 organises an architecture description around **viewpoints**
and **views**. A viewpoint specifies how to construct one view: it names the
stakeholders, their concerns, and the techniques used. A view is the system
seen through one viewpoint. The binding rule is that **every identified concern
must be framed by at least one viewpoint**.

The examples the standard gives of viewpoints - operational, logical,
deployment, process, information - put deployment on the same footing as the
rest. It is a way of looking at the system, not the way the description is
organised.

`arc42` makes the same choice concretely. Its twelve sections divide by
question, and no section belongs to a package: context and scope, solution
strategy, building block view, runtime view, deployment view, **crosscutting
concepts**, decisions, quality requirements. The building block view - the
decomposition of the system's own modular structure - is the most extensive
section, and it refines hierarchically where a flat list would stop.
Crosscutting concepts are a section of their own, not an exception bolted onto
a module list.

Two things transfer. **The decomposition follows the system's own structure**,
which the project names, and how the system is distributed decides nothing. And
**nesting is normal**: a part with parts is described at both levels, and
nothing forces it into one file or scatters it across many.

### A part is what the project says it is

The word that survives translation across projects is not plugin, package,
service or module. It is whatever the project calls the pieces it is built
from, and the only party that knows is the project.

That is the same shape the method already uses for artifact locations: the
harness fixes what an artifact kind means and the repository declares where it
lives. Here the harness fixes that the specification divides by part and that
contracts spanning parts get their own documents, and the repository declares
what its parts are.

For this harness those parts happen to be close to the plugins, and that
coincidence belongs to this project, and no rule produces it. For a monolith
they are modules. For a service the parts may be one.

### A reader decides whether a division is right

Neither standard gives a size limit, and neither should. What both imply is
sharper: a view exists because a stakeholder has a concern, and a document
exists because somebody would go looking for it.

That gives a usable test with two halves. **A specification document has one
subject a reader can name**, and **a reader with a question about that subject
finds the answer in one document, and never assembles it from three**. A
division that fails the first is a folder; one that fails the second is a
filing system.

The bidirectional trace is what keeps the division honest without constraining
it. Every statement traces to a requirement in force and every requirement in
force is stated somewhere, so moving a statement between documents cannot lose
it and cannot duplicate it. **The file boundary is a convenience for readers;
the trace is what makes the specification correct.** That is why granularity
can be revised later without the specification becoming wrong in the interval.

### What the parts are here, by way of illustration

Read against the decisions already taken, this harness divides into concerns
that are not the plugin list: the verb contract, the artifact model, the chain,
gates and evidence, reporting, delegation, the record's checks, distribution.
Several of those are implemented by more than one plugin and several plugins
implement more than one.

That mismatch is the finding. Where the parts and the packages coincide, keying
on either gives the same tree; where they diverge, the parts are what a reader
asks about.

## Conclusions

1. The specification divides by the system's own parts, and how it is
   distributed decides nothing. A project may be split into parts and still
   install as one thing, and packaging is a property not every project has. 2.
   The repository declares what its parts are. The harness fixes that the
   division is by part; naming the parts is the project's, like every other
   path it declares. 3. A contract spanning several parts gets a document of
   its own. It is a first-class section, which is how the standards treat
   crosscutting concepts, and no exception is needed for it. 4. The division
   nests. A part with parts is described at both levels rather than flattened
   into one document or scattered across many. 5. A specification document has
   exactly one subject a reader can name. A document whose subject cannot be
   stated in a phrase is a folder with a file extension. 6. A reader with a
   question about one subject finds the answer in one document. Where the
   answer is spread across three, the division is wrong whatever the file sizes
   say. 7. Deployment is a subject like any other, described where it is the
   subject, and it organises nothing. 8. The trace is what makes the
   specification correct, and the file boundary is for readers. Every statement
   traces to a requirement in force and every requirement in force is stated
   somewhere, so the granularity can be revised without the specification
   becoming wrong in the interval. 9. Granularity is revisable and identifiers
   are not. A specification document's identifier is permanent once cited, so a
   division that will be revised allocates identifiers to subjects, where a
   package name will not survive.

## Sources

All read 2026-09-20.

- [ISO/IEC/IEEE 42010 architecture
  description](https://quality.arc42.org/standards/iso-42010) and [ISO/IEC/IEEE
  42010 conceptual model](http://www.iso-architecture.org/42010/cm/) -
  viewpoints as specifications for constructing a view, naming stakeholders,
  concerns and techniques; the rule that every identified concern is framed by
  at least one viewpoint; and the example viewpoints - operational, logical,
  deployment, process, information - which place deployment among the others
  and never above them. - [arc42 overview](https://arc42.org/overview) - the
  twelve sections divided by question, where no section belongs to a package;
  the building block view as the most extensive section, hierarchically refined
  over the system's own modular structure; and crosscutting concepts as a
  section of its own. - `~/workspace/meowctl/docs/spec/` - the internal
  precedent of one living specification document per component, elaborated by
  many changes over time, recorded in [RES-0035-vision.md](RES-0035-vision.md).
