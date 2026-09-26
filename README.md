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

126 research documents are written, and 1,053 requirements are drawn from them.
Each requirement carries one obligation, cites the research it came from, and
declares what would verify it.

Nothing is designed and nothing is built. No decision is in force, so nothing
here says how any of this works, and no plugin exists yet. The harness is built
by its own method, so its artifacts come before its code, and they're what you
read and argue with today.

## Read in this order

| Document                                                | Answers                                                                                                                                                                                                                     |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [project/vision.md](project/vision.md)                  | What this is, who it's for, what it won't do, and how you'd judge whether it worked.                                                                                                                                        |
| [project/research/](project/research/)                  | What exists - six private harnesses, ten public ones, the platform, the toolchains, what a skill costs - and what the evidence says a new harness has to do. Indexed by [RES-0001](project/research/RES-0001-synthesis.md). |
| [project/requirements/](project/requirements/README.md) | What the harness must do: one obligation per file, traced to the research behind it.                                                                                                                                        |
| [project/README.md](project/README.md)                  | The record: which kinds accumulate, where each lives, and what's written so far.                                                                                                                                            |
| [CLAUDE.md](CLAUDE.md)                                  | The constitution for working _in this repository_.                                                                                                                                                                          |

## The proposed plugins

```text
packs   language   meow-rust  meow-go  meow-python  meow-typescript
                   meow-csharp  meow-lua  meow-neovim  meow-godot
                   meow-starlark  meow-scheme  meow-markdown
        runner     meow-mise  meow-task
        tool       meow-git  meow-jj  meow-gh  meow-linear
                   meow-qmd  meow-repomix  meow-worktrunk

practice           meow-research   meow-memory   meow-loop

method             meow-flow    meow-design   meow-review   meow-scm
                   meow-prose  meow-editing

kernel             meow-core
```

Everything above the packs knows nothing about your stack. A language pack
teaches the kernel five verbs - `fmt`, `lint`, `typecheck`, `test`, `build` -
authors that tool's configuration, and adds the idioms a reviewer needs. A
runner pack reads the tasks your project already declares. A tool pack teaches
the harness an external command-line tool, and every one of those is optional.

Which plugins exist, and how many, comes out of the design, and the design
hasn't run. What's proposed here is the layering - a kernel, a method layer, a
practice layer, and packs - so that you install the kernel and the few plugins
you need instead of the whole catalogue.

## Install

Download the released marketplace file, add it, and install the plugins you
want by name:

```bash
curl -fsSLo marketplace.json https://github.com/meowshed/meowpaw/releases/download/marketplace/marketplace.json
claude plugin marketplace add ./marketplace.json
claude plugin install meow-core@meowpaw
```

[`docs/README.md`](docs/README.md) lists every plugin with its page. A later
release reaches you when you download the file again and run
`claude plugin marketplace update meowpaw`.

A [dotmeow](https://github.com/meowshed/dotmeow) component will do this on a
machine it manages. None exists yet.

## Licence

Apache License 2.0.
