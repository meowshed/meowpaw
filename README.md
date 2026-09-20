# meowpaw

A universal, specification-driven harness for Claude Code, shipped as a plugin
marketplace.

`meowpaw` is what's left when you take the working parts of six harnesses -
`meowctl`, `meowg1k`, `vlie`, `hephaestus`, `meowhub`, `meowary` - drop
everything specific to one language, one engine or one household, and keep the
method. Nothing ships that a requirement doesn't describe, every requirement
traces to the check that proves it, and a human approves wherever approval is
the whole value.

Universal means two things here. The method knows nothing about your stack, so
a Rust workspace, a Godot game, a Compose deployment and a Markdown knowledge
base all move through the same nine steps. The parts that _must_ know your
stack - how to format, how to lint, how to run one test - arrive as small packs
answering a fixed contract.

## The method

Every unit of work, in any repository, moves through the same nine steps, and
each one writes a single artifact:

```text
research -> requirements -> design -> spec -> epic
         -> implement -> document -> verify -> review
```

The vision, the constitution and the specification are living documents. They
describe the present and you rewrite them freely, because the history already
lives in the records. Everything else is a record - research, requirements,
decisions, epics, tasks, defects - open while it's a draft and frozen once
approved, so a later truth becomes a new record and never an edit to an old
one.

Design produces decision records. An epic realises exactly one authorising
record, a decision or a defect, which is what makes it finite and what it
projects onto when you use a tracker.

Documentation comes before review, so review covers it. Review runs last, and
its verdict names the step the work returns to.

A step refuses to run when its input is missing or unapproved, and that refusal
is the only thing enforcing the order. Trivial work skips the chain: the
harness classifies the request first and tells you which class it picked,
because a harness that demands nine steps for a typo is one you'd work around.

## Status

125 research documents cover the six private harnesses, ten public ones, the
agent platform, eleven toolchains, the runners, the external tools, the
commands and skills the harness will ship, the design lenses, a template for
every artifact kind, and the gaps we found by reading the corpus against
itself.

Nothing is required of anyone yet. Requirements come from this research, and
they're next.

| Document                               | Answers                                                                                                                                                                                                                     |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [project/research/](project/research/) | What exists - six private harnesses, ten public ones, the platform, the toolchains, what a skill costs - and what the evidence says a new harness has to do. Indexed by [RES-0001](project/research/RES-0001-synthesis.md). |
| [project/vision.md](project/vision.md) | What this is, who it's for, what it won't do, and how you'd judge whether it worked.                                                                                                                                        |
| [CLAUDE.md](CLAUDE.md)                 | The constitution for working _in this repository_.                                                                                                                                                                          |

## Licence

Apache License 2.0.
