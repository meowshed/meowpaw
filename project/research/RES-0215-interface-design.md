---
id: RES-0215
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0201
---

# The `interface-design` skill

## Summary

Two rules survive the strip from a product-specific standard, and both attack
the same failure: a surface organised around what the system has, and never
around what someone wanted to know. A surface answers one question stated in
the asker's words, and one that answers four is four surfaces. And the data is
named before the shape, because an interface promising an answer the system
cannot produce fails at the end of the work, where naming the data first fails
at the start.

Research for one design lens: every surface answers one question somebody
actually asked, and the data is named before the shape.

Its siblings are the other four lenses, listed in
[RES-0017-design-lenses.md](RES-0017-design-lenses.md).

## The question

The donor standard is the most product-specific of the five, and two of its
rules are general enough to survive the strip. Both are about the same failure:
a surface organised around what the system has, and never around what someone
wanted to know.

## Method

The donor standard was read in full from its working tree on 2026-09-20 and
quoted directly, and the surrounding voice standard was read for the one line
that generalises.

We read the rest of that standard - its design system, chart heuristics and
specific steps - and deliberately took none of it. This document records that,
so a later reader does not assume we missed it.

No external source was consulted, and nothing was tested. We reason about this
harness's own surfaces here, and reviewed none of them.

## Findings

### A surface answers one question, stated in the words the asker used

The donor rule, quoted:

> If you can't name a proposed screen as a question, it isn't designed yet. If
> it answers four questions, it is four screens.

This applies to anything with a surface: a command-line subcommand, an API
endpoint, a report, a dashboard panel, a chat reply.

The failure it prevents is the **entity-shaped interface** - a screen called
_Transactions_, an endpoint called `/users`, a report called _Status_ - which
answers nothing in particular and therefore answers everything badly. The name
is the test: an entity is a noun, and a question is not.

The second half of the rule is the operational one. Four questions is four
surfaces, and the instinct to combine them is what produces the dashboard
nobody reads.

### Name the data before the shape

If the view the interface reads does not exist, the work starts with the data
and not with the component. Where the system computes nothing of its own, _a
number no view produces is not available at any price_.

Generalised: **establish what can be known before designing how it is shown.**
The alternative is an interface promising an answer the system cannot support,
discovered at the end, when the layout is finished and the number is missing.

### This harness's surfaces, read through the lens

The lens applies to the harness's own output, and doing so is instructive
because the harness has several surfaces that are easy to make entity-shaped.

The status command survives it: _where does the work stand_ is a question.
The diagnostic command survives it: _can this repository be worked on_ is a
question, and keeping it separate from the first is this rule enforced - two
questions, two commands.

The gate's three outcomes apply this rule to a result, where the lens usually
applies it to a screen. Pass, fail and unresolved answer _did it run and did it
succeed_, and collapsing unresolved into failure answers two questions with one
word.

A report that listed everything the harness knows would be the entity-shaped
failure, and it is the one a status command drifts towards over time.

### What does not transplant

The donor material's design system, its chart heuristics and its ten specific
steps are product work and belong to a domain pack if anywhere.

One line from its surroundings generalises, and it belongs in the writing
skill: **the product's voice is a documented standard, and it applies to the
product and never to the repository.** Specifications, decision records and
commits stay plain whatever the product sounds like.

## Conclusions

1. Every surface answers exactly one question, stated in the words the person
   asking would use. 2. A surface that cannot be named as a question is not
   designed yet, and one that answers four questions is four surfaces. 3. An
   entity-shaped surface is a finding, since a noun answers nothing in
   particular. 4. The data is named before the shape, because an interface
   promising an answer the system cannot produce fails at the end of the work,
   where naming the data first fails at the start. 5. A number no view produces
   is not available at any price, so the work starts with what can be known. 6.
   The rule applies to every surface the harness has, including a command's
   output and a result's vocabulary. 7. Two questions are two commands, which
   is why reporting where the work stands and whether the repository can be
   worked on are separate. 8. A product's voice applies to the product and
   never to the repository, which belongs to the writing standard, and not to
   this lens.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/docs/standards/ui-design-process.md` - that a screen
  which cannot be named as a question is not designed yet and one answering
  four questions is four screens; naming the data before the layout; that a
  number no view produces is not available at any price; and the design-system
  and chart material that does not transplant.
- `~/workspace/meowhub/docs/standards/agent-persona.md` - the product voice as
  a documented standard applying to the product and not to the repository.
- [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the five lenses and
  what survived the strip from their donor project.
