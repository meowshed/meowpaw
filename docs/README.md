---
reader: someone deciding which parts of meowpaw to install
answers: what meowpaw is, which page covers each part and how to install one
kind: introduction
describes:
  [
    meow-core@0.6.1,
    meow-git@0.2.3,
    meow-github@0.5.0,
    meow-flow@0.41.0,
    meow-prose-gate@0.2.2,
    meow-prose@0.5.0,
    meow-scm@0.4.2,
    meow-verbs@0.7.1,
  ]
---

# meowpaw

`meowpaw` is a harness for Claude Code: units you install into Claude Code that
make it report what it checked, what it couldn't check and what it decided, so
you can trust a report without re-reading the work behind it. Each unit
installs on its own.

## Quick start

Add the marketplace, install `meow-verbs`, which runs your repository's
checks, and declare one check. Run this from the repository's root. If
`.meowpaw/profile.toml` already exists, add the `[verbs]` table to it by hand
instead of running the last line, because that line replaces the file:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-verbs@meowpaw
mkdir -p .meowpaw && printf '[verbs]\ntest = "./scripts/test"\n' > .meowpaw/profile.toml
```

Replace `./scripts/test` with the command your repository runs its tests
with. Claude Code then runs that command when it tests, and reports every
check you didn't declare as unresolved. The [tutorial](tutorial.md) walks
through the same steps in an empty repository.

## Pages

Every page, who it is for and what it answers:

<!-- check_docs index -->

| Page                                                    | For                                                                                                   | Answers                                                                                         | Kind            |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | --------------- |
| [meow-author](../plugins/meow-author/README.md)         | someone choosing or running meow-author                                                               | what meow-author does, what it adds to a session and how to run it                              | reference       |
| [meow-code](../plugins/meow-code/README.md)             | someone choosing or running meow-code                                                                 | what meow-code does, what it adds to a session and how to use it                                | reference       |
| [meow-core](../plugins/meow-core/README.md)             | someone choosing or running meow-core                                                                 | what meow-core does, what it adds to a session and how to run it                                | reference       |
| [meow-flow](../plugins/meow-flow/README.md)             | someone choosing or running meow-flow                                                                 | what meow-flow does, what it adds to a session and how to run it                                | reference       |
| [meow-git](../plugins/meow-git/README.md)               | someone choosing or running meow-git                                                                  | what meow-git does, what it adds to a session and how to run it                                 | reference       |
| [meow-github](../plugins/meow-github/README.md)         | someone choosing or running meow-github                                                               | what meow-github does, what it adds to a session and how to run it                              | reference       |
| [meow-gotask](../plugins/meow-gotask/README.md)         | someone choosing or running meow-gotask                                                               | what meow-gotask does, what it adds to a session and how to run it                              | reference       |
| [meow-licence](../plugins/meow-licence/README.md)       | someone choosing or running meow-licence                                                              | what meow-licence does, what it adds to a session and how to run it                             | reference       |
| [meow-markdown](../plugins/meow-markdown/README.md)     | someone choosing or running meow-markdown                                                             | what meow-markdown does, what it adds to a session and how to run it                            | reference       |
| [meow-method](../plugins/meow-method/README.md)         | someone who has meow-method installed and sees its notice                                             | why meow-method is a stub now, and how to move to meow-flow                                     | reference       |
| [meow-mise](../plugins/meow-mise/README.md)             | someone choosing or running meow-mise                                                                 | what meow-mise does, what it adds to a session and how to run it                                | reference       |
| [meow-prose](../plugins/meow-prose/README.md)           | someone choosing or running meow-prose                                                                | what meow-prose does, what it adds to a session and how to run it                               | reference       |
| [meow-prose-gate](../plugins/meow-prose-gate/README.md) | someone choosing or running meow-prose-gate                                                           | what meow-prose-gate does, what it adds to a session and how to run it                          | reference       |
| [meow-scm](../plugins/meow-scm/README.md)               | someone choosing or running meow-scm                                                                  | what meow-scm does, what it adds to a session and how to run it                                 | reference       |
| [meow-unattended](../plugins/meow-unattended/README.md) | someone choosing or running meow-unattended                                                           | what meow-unattended plans, what it writes and what its deny rules don't stop                   | reference       |
| [meow-verbs](../plugins/meow-verbs/README.md)           | someone choosing or running meow-verbs                                                                | what meow-verbs does, what it adds to a session and how to run it                               | reference       |
| [troubleshooting](troubleshooting.md)                   | someone whose meowpaw unit just refused, blocked or reported something they didn't expect             | what each message a unit prints means, why it appeared and what fixes it                        | troubleshooting |
| [tutorial](tutorial.md)                                 | someone new to meowpaw, on macOS or Linux, who wants to see what it does before using it on real work | how to get from an empty repository to a first check that Claude Code runs and reports honestly | tutorial        |

<!-- /check_docs index -->

## Adopt any part of it

You can install any combination of units, and no unit needs another to work. A
unit that does more with another installed says so, and reports what it can't
do without it: `meow-git` checks commit messages with `meow-scm` where that
unit is installed, and reports the check as unrun where it isn't. Nothing a
unit installs changes your repository: the only files the harness writes there
are ones you ask for, such as `.meowpaw/profile.toml`, and keeping a record of
decisions with `meow-flow` is optional.

Each unit that runs a program ships it for macOS, Linux and Windows on arm64
and x86_64, so it needs nothing else installed. A later release reaches you
when you run `claude plugin marketplace update meowpaw`, or by itself once you
turn on auto-update for `meowpaw` in the **Marketplaces** tab of `/plugin`.

## Planned

These parts are planned, and no unit ships them yet, so no page describes
them:

- packs that resolve the five verbs `meow-verbs` runs, `format`, `lint`,
  `check`, `test` and `build`, for a language or a task runner without
  your declaring each command;
- packs for version control tools other than git, and for trackers other than
  GitHub;
- runs that carry the method forward unattended, within the gates a
  repository declares.

## Not written

- `how-to`: each unit's page carries the tasks for that unit, and the
  tutorial walks through the first one, so a separate guide would repeat them.
- `explanation`: the reasons behind each unit's design are written for the
  people building the harness, and each unit's page states what a user needs
  of them.
