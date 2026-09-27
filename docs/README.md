---
reader: someone deciding which parts of meowpaw to install
answers: what meowpaw is, which page covers each part and how to install one
kind: introduction
describes:
  [
    meow-core@0.6.1,
    meow-git@0.2.2,
    meow-github@0.4.1,
    meow-method@0.30.2,
    meow-prose-gate@0.1.2,
    meow-prose@0.3.5,
    meow-scm@0.4.1,
    meow-verbs@0.2.2,
  ]
---

# Documentation

How to use what `meowpaw` ships. The record of what must be true and why lives
under `project/`, and this hierarchy stays separate from it.

| Page                                                    | What it covers                                                                     |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| [meow-core](../plugins/meow-core/README.md)             | The kernel, and the reply shape it imposes                                         |
| [meow-prose](../plugins/meow-prose/README.md)           | The writing standard, loaded before Claude writes                                  |
| [meow-prose-gate](../plugins/meow-prose-gate/README.md) | A hook that blocks a publish carrying a defect any reader can point to             |
| [meow-verbs](../plugins/meow-verbs/README.md)           | The five verification verbs, run as the repository declared them                   |
| [meow-scm](../plugins/meow-scm/README.md)               | The commit convention, checked before a message is used                            |
| [meow-git](../plugins/meow-git/README.md)               | A pack that refuses a commit on the trunk and checks a branch before it is pushed  |
| [meow-method](../plugins/meow-method/README.md)         | Runs the method's nine steps, and checks the record they write                     |
| [meow-github](../plugins/meow-github/README.md)         | Reads a GitHub repository's issues, pull requests and comments, and writes nothing |

Each unit ships its page inside itself, and a unit's catalogue entry links to
that page.

## Adopt any part of it

Each unit is a working harness on its own, and you can install any
combination of them. No unit runs another unit's files, which a check holds,
so removing one leaves the rest working. A unit that could do more with
another installed says so and names it, and reports what it can't do without
it. Nothing a unit installs changes your repository: the only files the
harness writes there are ones you ask for, such as `.meowpaw/profile.toml`,
and the record is optional.

## Install

Add the marketplace and install the units you want by name:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-verbs@meowpaw
```

Each unit comes with its binaries for macOS, Linux and Windows on ARM64 and
x64, so it needs neither Rust, Python nor Node.js. A later release reaches you when you run
`claude plugin marketplace update meowpaw`, or by itself once you turn on
auto-update for `meowpaw` in the **Marketplaces** tab of `/plugin`.
