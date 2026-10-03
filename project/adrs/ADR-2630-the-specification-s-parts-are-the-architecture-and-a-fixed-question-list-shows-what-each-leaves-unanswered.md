---
id: ADR-2630
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2250, REQ-2252, REQ-2254]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2630. The specification's parts are the architecture, and a fixed question list shows what each leaves unanswered

## Decision

The architecture description is the specification, organised by the parts
the repository declared for it, and not a second document beside it
(REQ-2250). The spec template gains a short section of fixed questions, each
answered or marked `unanswered`: what the part is for, what it depends on,
what depends on it, where its data lives, what crosses a trust boundary, how
it fails and how it is deployed (REQ-2252). A question with no answer stays
in the document marked `unanswered`, so a reader sees the gap instead of
missing it.

The design step names each concern a decision raises, such as performance,
security or upgrade, and the spec step frames each in at least one view of a
part, which is a section or a diagram that addresses it. `paw check` reports a
concern a decision names that no specification section cites (REQ-2254).

Once this is accepted, the specification answers the same questions for
every part, and a missing answer shows. What still doesn't work: whether an
answer is right is a judgement, so review holds it.

## Why

RES-0072 found that a project with an architecture document and a
specification keeps two structures that disagree, that a fixed list of
questions makes a missing answer visible where free prose hides it, and that
a concern no view frames is assumed covered. It takes the vocabulary from
ISO/IEC/IEEE 42010 and the idea of a fixed question set from arc42. The seven
questions are my choice from arc42's set, cut to the ones a plugin harness
has.

## Alternatives

| Option                      | Better at                      | Why it lost                                                  |
| --------------------------- | ------------------------------ | ------------------------------------------------------------ |
| Do nothing                  | No new section                 | No reader can tell which questions a part's spec leaves open |
| A separate architecture doc | One place for the whole system | It is the second structure REQ-2250 rules out                |
| All of arc42's sections     | Complete by a known template   | Most sections have nothing to say for a plugin harness       |

## What it costs

Each of the twenty specifications gains the question section, and the first
pass marks many answers `unanswered`.

## What would reverse it

- A question in the list stays `unanswered` in every part for a year, which
  would show it isn't one this project asks.

## Consequences

The spec template gains the questions. `paw check` gains the concern rule.
A task adds the section to each specification.

## How I will know it was realised

1. Every specification carries the question section, with each answered or
   marked `unanswered` (REQ-2252).
2. `paw check` reports a fixture decision naming a concern no specification
   cites (REQ-2254).

## What this does not settle

- How a diagram is drawn, which ADR-2620 decides.
