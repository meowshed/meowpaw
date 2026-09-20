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

Nothing is written down yet. What's here is the ground the record will stand
on: the licence, the constitution that governs work inside this repository, and
a gate that formats and lints prose.

The harness is built by its own method, so its artifacts come before its code,
and they arrive in the method's own order, starting with what already exists.

| Document               | Answers                                            |
| ---------------------- | -------------------------------------------------- |
| [CLAUDE.md](CLAUDE.md) | The constitution for working _in this repository_. |

## Licence

Apache License 2.0.
