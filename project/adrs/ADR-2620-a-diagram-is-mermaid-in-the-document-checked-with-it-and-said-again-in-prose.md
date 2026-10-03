---
id: ADR-2620
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [REQ-2290, REQ-2292, REQ-2294, REQ-2296, REQ-2300, REQ-2302, REQ-2304]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2620. A diagram is Mermaid in the document, checked with it, and said again in prose

## Decision

A diagram is text in a fenced block in the document that carries it, and
never an embedded image (REQ-2290). The default notation is Mermaid, because
GitHub renders it in Markdown with no build step, no plugin and no generated
file (REQ-2292). A repository declares its notation in the profile under
`[docs] diagrams`, and a notation that needs a build step is refused for the
record and allowed elsewhere only with its cost stated in that document
(REQ-2294, REQ-2296).

Everything a diagram asserts is also stated in the prose beside it, because a
reader who gets the source and not the picture still needs the fact
(REQ-2300). A diagram carries no obligation, which belongs in a requirement,
and no reason, which belongs in a decision (REQ-2302).

`meow-markdown` gains a check that parses each Mermaid block with the Mermaid
command-line tool, and a block that fails to parse fails the `check` verb
(REQ-2304). It also fails an image link to a `.png` or `.svg` in a record
document.

Once this is accepted, a diagram is reviewed as text and checked like code.
What still doesn't work: no check can tell whether the prose says everything
the diagram does, so review holds REQ-2300.

## Why

RES-0073 found that an image drifts from its source with no diff to show it,
that the notation which renders where the corpus is read needs no build, and
that a reader of the raw file sees only the source. GitHub is the render
target this repository declares in `[markdown] target`, and GitHub renders
Mermaid.

## Alternatives

| Option                    | Better at          | Why it lost                                                   |
| ------------------------- | ------------------ | ------------------------------------------------------------- |
| Do nothing                | No new check       | A diagram that doesn't parse renders as broken text unnoticed |
| PlantUML                  | A richer notation  | It needs a server or a build step to render                   |
| ASCII art in a code block | Renders everywhere | No parser checks it, and it can't be redrawn by a tool        |

## What it costs

The `check` verb needs the Mermaid command-line tool, which pulls a headless
browser, so the gate takes longer and installs more.

## What would reverse it

- GitHub stops rendering Mermaid, or the repository's declared render target
  changes to one that doesn't.

## Consequences

`meow-markdown` gains the parse check and the image rule. ADR-2370's key
table gains `[docs] diagrams`.

## How I will know it was realised

1. A fixture document with a Mermaid block that doesn't parse fails the
   `check` verb (REQ-2304).
2. A fixture record with an embedded `.png` fails (REQ-2290).
3. A profile declaring a notation with a build step is refused for the record
   (REQ-2294).

## What this does not settle

- Which diagrams the specification should carry. That is ADR-2630's
  architecture description.
