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

## Status

The vision is written and nothing else is. It says what this is, who it's for,
what it won't do, and what would count as it having worked - which a method
that refuses to build unauthorised work has to settle about itself before it
settles anything else.

| Document                               | Answers                                                                              |
| -------------------------------------- | ------------------------------------------------------------------------------------ |
| [project/vision.md](project/vision.md) | What this is, who it's for, what it won't do, and how you'd judge whether it worked. |
| [CLAUDE.md](CLAUDE.md)                 | The constitution for working _in this repository_.                                   |

## Licence

Apache License 2.0.
