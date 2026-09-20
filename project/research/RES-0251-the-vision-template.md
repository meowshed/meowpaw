---
id: RES-0251
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0035, RES-0253
---

# The vision template

## Summary

The vision is the only document with no upstream artifact, so what it contains
is a question about discipline, and nothing derives it. Two moves from the
product forms transfer: naming what the project is instead of, and naming who
it is for. The architecture form contributes what they lack, which is quality
goals in priority order with ties broken, and that is the vision's one real
contribution to daily work. Its failure mode is already in this project's
history: a claim nothing could check.

Research for what the vision contains. What a document describing what a
project is and where it is going has to hold, and which of the published forms
survive being used by an agent, where a marketing department uses them
differently.

One of nine template documents, one per artifact kind in the record.

It does not cover whether the project should have one or how it relates to the
other living documents, which is [RES-0035-vision.md](RES-0035-vision.md).

## The question

The vision is the only document in the record with no upstream artifact. Every
other kind is derived from something; this one is asserted.

That makes what it contains a question about discipline, and nothing derives
it: what stops it becoming a paragraph of ambition that nothing can contradict.

## Method

The published vision forms were fetched and read on 2026-09-20 - the elevator
pitch with its fixed slots and the vision board - and the architecture template
was fetched for its first and eleventh sections.

The failure modes were not taken from those sources. They come from this
project's own history, where an unfalsifiable claim of universality survived
until eighteen obligations were written to make it checkable.

Nothing was measured, and no existing vision was audited against this shape.

## Findings

### The product forms are about positioning, and two of their moves transfer

The widely used form is an elevator pitch with fixed slots: **for** a target
customer, **who** has a need or opportunity, **the** product is a **category**,
that delivers a key benefit. The fuller versions add _unlike_ a named
alternative, and _our product_ differing in a stated way.

Two things transfer to a technical project and one does not.

Naming the alternative transfers, and is the sharpest slot. A vision that
cannot say what it is instead of has not been positioned, and _doing nothing_
counts as the alternative. For this project the alternatives are six diverged
copies of a harness in six repositories, which is a far more useful statement
of purpose than any adjective.

Naming who it is for transfers. It bounds every downstream decision, and
its absence is what lets a project accumulate features for nobody.

The category slot does not transfer well. Filling in _is a specification-driven
development harness_ invites a claim of novelty that no requirement will ever
check, which is how a vision becomes unfalsifiable.

### The architecture form contributes the part the product forms lack

The architecture template opens with fundamental requirements and, explicitly,
quality goals - and later carries **risks and technical debt** as a section
of its own.

Quality goals are what the product forms have no place for and what an agent
most needs: not _what is this_ but _what must be true of it_, in a form the
requirements can refine. A vision that states _correctness over speed, and
reproducibility over convenience_ has decided something that will settle
arguments later; one that states _world-class quality_ has not.

Carrying known risks in the same document is the other contribution. A vision
listing only where the project is going is an advertisement; one that also
names what could stop it is a briefing.

### What a vision must not become, given what it is loaded into

An agent reads the vision here as context for everything else, which puts it
under the economics of any always-available document. What it says is paid for
whenever it is read, and what it says vaguely is worse than nothing, because it
displaces something specific.

So the failure modes to design against are not stylistic:

- **Unfalsifiable claims.** _Universal_ is the worked example from this
  project's own history: the vision claimed five languages, nothing made it
  binding, and no one could point at anything to say whether the claim was
  true. It took eighteen new obligations to make it checkable.
- **Duplicated obligations.** A vision that repeats requirements creates two
  copies that drift, and the one nobody checks is the one people read.
- **Roadmaps.** A dated plan in a living document is wrong on a schedule.

### What it must contain

Read against all of the above, six things, and a sentence or a short list
carries each of them:

1. What this is, in one sentence a stranger could repeat. 2. Who it is for,
   specifically enough to exclude someone. 3. What it is instead of, including
   doing nothing. 4. What must be true of it - the quality goals, in priority
   order, with ties broken. 5. What it is not - the non-goals, which is where
   scope arguments end. 6. What could stop it: the risks that are live now, and
   no register of every risk imaginable.

The order is deliberate: the first three position, the next two constrain, and
the last one is honest.

### The priority order in the quality goals is the load-bearing part

A list of qualities is not a decision; a list with ties broken is. _Correctness
over speed_ tells an implementer what to do when they conflict, which is the
only moment the statement matters.

This is the vision's one real contribution to daily work: every other document
says what must be true, and this is the only one that says which of two true
things wins.

### It is a projection, so updating it removes

The vision carries no history. It is rewritten freely because the history is in
the research and the decisions.

That gives it the same obligation the specification has: **an update removes
what is no longer intended.** A vision that only grows becomes a list of
everything the project has ever wanted, and the reader cannot tell which parts
are current.

### The sections it carries

| Section            | Holds                                        | Mandatory |
| ------------------ | -------------------------------------------- | --------- |
| Front matter       | Kind, status `live`, revision date           | Yes       |
| What this is       | One sentence                                 | Yes       |
| Who it is for      | Specific enough to exclude                   | Yes       |
| Instead of         | The alternatives, including doing nothing    | Yes       |
| What must be true  | Quality goals in priority order, ties broken | Yes       |
| What it is not     | Non-goals                                    | Yes       |
| What could stop it | Live risks                                   | Yes       |

No section for features, no roadmap, no dates.

## Conclusions

1. The vision names what the project is instead of, including doing nothing,
   because a project that cannot say that has not been positioned. 2. It names
   who it is for, specifically enough to exclude someone. 3. It states quality
   goals in priority order with ties broken, which is its one contribution to
   daily work: saying which of two true things wins. 4. It states non-goals,
   because that is where scope arguments end. 5. It names the risks that are
   live now, since a document listing only the destination advertises the
   project and briefs nobody. 6. It makes no claim nothing can check. A claim
   the vision makes is either made falsifiable by a requirement or is removed. 7. It repeats no requirement, because two copies drift and the unchecked one
   is the one people read. 8. It carries no roadmap and no dates, which in a
   living document are wrong on a schedule. 9. It avoids the category claim
   that invites novelty nothing will verify. 10. An update removes what is no
   longer intended, since it projects the current intent and records none of
   the past ambitions.

## Sources

All read 2026-09-20.

- [How to create a product vision using the elevator pitch](https://medium.com/@gautam.lavaneesh/how-to-create-product-vision-using-elevator-pitch-ef3a83862f9e)
  and [Creating vision and goals with an elevator pitch](https://www.scrum.org/resources/creating-vision-and-goals-elevator-pitch)
  - the fixed slots of for, who, the product and category, and the key benefit,
    with the fuller form naming the alternative and how the product differs.
- [The product vision board](https://www.prodpad.com/blog/product-vision-template/)
  - the vision board as a tool for aligning on the vision behind a product, and
    the fields it fixes.
- [arc42 overview](https://arc42.org/overview) - section one carrying
  fundamental requirements and especially quality goals, section ten carrying
  quality requirements as a tree and scenarios, and section eleven carrying
  known risks and technical debt.
- [RES-0035-vision.md](RES-0035-vision.md) - the vision as one of three living
  projections, carrying no history of its own and rewritten freely.
- [RES-0240 in this repository's decisions](../adrs/README.md) - the worked
  example of an unfalsifiable vision claim, where universality was asserted and
  nothing made it binding until eighteen obligations were written.
