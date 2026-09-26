# meow-verbs

`meow-verbs` runs your repository's checks the way the repository declared
them, and reports a check nobody declared as unresolved, never as passed. It
covers five verbs, `fmt`, `lint`, `typecheck`, `test` and `build`, and it
installs on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-verbs@meowpaw
```

## Declare your verbs

Put one command per verb in `.meowpaw/profile.toml` at the repository's root.
Each command runs through the shell from that root:

```toml
[verbs]
fmt = "./scripts/format --check"
lint = "./scripts/lint"
test = "./scripts/run-tests"
```

Declare only the verbs your repository has. A verb you leave out is reported
as unresolved, which is the honest answer: nothing ran, so nothing passed.

## What Claude Code does with them

When Claude Code formats, lints, type-checks, tests or builds, the
`meow-verbs:verify` skill has it run the program in place of a command it
would otherwise choose. It first shows what each verb resolves to:

```text
fmt        resolved    ./scripts/format --check   (from .meowpaw/profile.toml)
typecheck  unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
```

Then it runs the verbs the work needs and reports each as passed, failed or
unresolved. A failed verb comes with its exact command, its exit status and its
whole output, led by its last lines, where a failing tool puts its error. The
program exits 0 only when every verb it ran passed, 1 when one failed and 3
when one was unresolved.

An unresolved verb is one of five kinds: undeclared, no profile, a profile
that doesn't parse, a declaration that isn't one command, and no interpreter
to run the program.

## What it costs you

The skill's description costs 332 characters in context on every turn. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, every
verb is reported unresolved, as "no interpreter".

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-verbs/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description: [documentation](https://code.claude.com/docs/en/skills.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)

## Where the rules come from

The decision is
`project/adrs/ADR-1070-the-five-verbs-resolve-from-the-profile.md`, and the
unit is specified in `project/specs/SPC-1040-the-five-verbs.md`.
