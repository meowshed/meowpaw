---
id: RES-0073
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Diagrams in documents

## Summary

A diagram is written as text in the document and never embedded as an image,
because a text definition diffs and an image drifts from its source silently.
Only one notation renders where this corpus is read, with no build step and no
plugin. The platform's rendering documentation says nothing about alternative
text, and that silence is the finding. Whatever a diagram asserts is stated in
prose beside it, so the fact survives a reader who receives the source and
never the picture.

Research for how the harness draws. It covers which notation survives the way
this corpus is read and reviewed. It also covers what a diagram may be the only
source of, and what one has to carry to be usable by somebody who cannot see
it.

It does not cover what the architecture description contains, which is
[RES-0072-architecture-discipline.md](RES-0072-architecture-discipline.md).

## The question

The corpus is plain Markdown, read on a forge and in an editor with no plugin,
and reviewed as a diff. A picture is the right form for a structure, a sequence
and a state machine, and the wrong form for everything the method uses prose
for.

So: what may be drawn, in what, and what must remain written down beside it.

## Method

We fetched and read the platform's rendering documentation on 2026-09-20 for
which syntaxes render natively and what limitations it states. We fetched the
comparison material and the published benchmarks for the trade-offs between the
three notations.

The absence of any statement about alternative text was checked by reading the
page rather than inferred, which is why it is recorded as an absence.

Nothing was rendered or measured here; the performance figures are the
benchmark's.

## Findings

### One notation renders where this corpus is read, and the others need a build step

The constraint is not aesthetic. The artifacts must render on a forge and in an
editor with no plugin installed, which rules out anything requiring a
generated image or an extension.

GitHub renders four syntaxes natively in Markdown files, issues, pull requests
and wikis: **Mermaid**, GeoJSON, TopoJSON and ASCII STL. Of those only Mermaid
is a diagram notation for software.

The comparison is one-sided on this axis and honest about the rest. Mermaid is
the only format that renders inline with no build step, no plugin and no
generated image. PlantUML is not natively supported and needs a plugin, a
continuous-integration step that produces images, or an external renderer. D2
likewise needs a build step.

The other two are better at things Mermaid is not. PlantUML's coverage is
meaningfully wider for deployment and component diagrams - the
boxes-inside-boxes-with-interfaces pattern. D2 produces better-looking output
and renders fastest of the four in published benchmarks, with PlantUML slowest
by an order of magnitude.

None of that outweighs rendering where the document is read. A diagram behind a
build step is a diagram nobody sees during review, which is the moment it is
needed.

### A diagram in text is reviewable; a diagram in an image is not

The property that matters more than the notation: a text-based diagram
definition diffs cleanly, and a change to it is reviewed the same way a change
to code is reviewed.

An exported image is a binary blob. It cannot be diffed, its source drifts from
it silently, and a review of a change to it is a review of two pictures side by
side. Every argument this method makes about evidence, drift and review applies
to a picture as much as to a paragraph.

### The notation is separable from the abstraction

The C4 model is deliberately notation independent and tooling independent: it
fixes the levels - system, container, component, code - and leaves the drawing
open.

That split is what lets a rule about notation be a decision that can change
without touching the architecture description. What must not change is which
level a diagram is at; which tool draws it is a packaging question.

### Nothing in the platform's documentation addresses what a reader who cannot see it gets

The rendering documentation names four syntaxes and one limitation - a
third-party Mermaid plugin may conflict - and says nothing about alternative
text, accessibility or fallbacks.

That silence is the finding. A rendered diagram in a Markdown file has no alt
text mechanism. A reader using a screen reader, a reader in a plain-text client
and a model reading the file all receive the source, and none of them the
picture. The source is readable, but it is a description of shapes rather than
a statement of what the shapes mean.

The consequence for this method is narrow: whatever a diagram asserts has to be
stated in prose beside it. That is not an accessibility courtesy bolted on. It
is the rule the method already applies to evidence: a claim that exists only in
a form nobody can check is no claim. It is also what keeps a diagram from
becoming the only place a fact lives.

## Conclusions

1. A diagram is written as text in the document, never embedded as an
   image. A text definition diffs cleanly and is reviewed like code; an image
   cannot be diffed and drifts from its source silently.
2. The default notation is the one that renders where the corpus is read,
   with no build step, no plugin and no generated file. On the platform this
   corpus lives on, that is Mermaid.
3. A notation needing a build step is not used for a document in the
   record. It may be used where the output is published elsewhere, and the
   cost is stated.
4. The notation is declared per repository and is separable from what is
   drawn, because the abstraction levels are fixed and the drawing is not.
5. A diagram names the abstraction level it is at, and does not mix two.
6. Everything a diagram asserts is stated in prose beside it. A diagram is
   never the only place a fact lives, because the fact has to survive a reader
   who gets the source rather than the picture.
7. A diagram is used where a picture is the right form: a structure, a
   sequence, a state machine, a dependency. It is not used to carry an
   obligation, which belongs in a requirement, or a reason, which belongs in a
   decision.
8. A diagram is checked like any other content. It is part of the document,
   so the document's checks apply to it, and a diagram that fails to parse is a
   failing check rather than a rendering curiosity.

## Sources

All read 2026-09-20.

- [Creating diagrams on GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
  - the four syntaxes that render natively in Markdown files, issues, pull
    requests and wikis; the single stated limitation about third-party plugins;
    and the absence of any statement about alternative text or fallbacks.
- [Mermaid versus PlantUML in 2026](https://dev.to/levi_liu/mermaid-vs-plantuml-in-2026-which-to-pick-for-engineering-docs-59dm)
  and [Best diagram-as-code tools 2026](https://infrasketch.net/blog/best-diagram-as-code-tools-2026)
  - that Mermaid is the only format rendering inline on a forge with no build
    step; that PlantUML needs a plugin, a build step or an external renderer and
    has wider coverage for deployment and component diagrams; that D2 needs a
    build step and produces better-looking output; and that a text definition
    diffs cleanly so a diagram change is reviewed like a code change.
- [D2 benchmarks](https://github.com/d2lang/d2-benchmarks) - reproducible
  end-to-end rendering measurements across D2, Mermaid, Graphviz and PlantUML,
  with D2 fastest and PlantUML slowest by roughly two orders of magnitude.
- [The C4 model](https://c4model.com/) - fixed abstraction levels with
  deliberate independence from notation and tooling.
