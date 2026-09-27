---
reader: someone choosing or running meow-verbs
answers: what meow-verbs does, what it adds to a session and how to run it
kind: reference
describes: [meow-verbs@0.6.0]
---

# meow-verbs

`meow-verbs` runs your repository's checks the way the repository declared
them, and reports a check nobody declared as unresolved, never as passed. It
covers five verbs, `format`, `lint`, `check`, `test` and `build`, and it
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
format = "./scripts/format --check"
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
format     resolved    ./scripts/format --check   (from .meowpaw/profile.toml)
check      unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
```

Then it runs the verbs the work needs and reports each as passed, failed or
unresolved. A failed verb comes with its exact command, its exit status and its
whole output, led by its last lines, where a failing tool puts its error. The
program exits 0 only when every verb it ran passed, 1 when one failed and 3
when one was unresolved.

Each run is recorded, so a claim that a check passed can name its record
instead of pasting output. `run` appends every verb it runs to a ledger in your
state directory, `$XDG_STATE_HOME/meowpaw/evidence/`, or
`~/.local/state/meowpaw/evidence/` where that variable is unset and
`%LOCALAPPDATA%\meowpaw\evidence\` on Windows, never in the repository. Each
record keeps the command, the outcome, the whole output and the git tree id of
your working state before and after the verb, and `run` ends with one
`recorded: <verb> <record> at tree <tree id>` line per verb.

`meow-verbs evidence [verb...]` tells you whether those results still hold:

```text
test: passed, record 3f9a1c0b2d4e, current at tree 6960e730d656
lint: passed, record 8b21e4f07a9c, stale: ran on tree 1c4d2e9f0a3b, and the tree is now 6960e730d656
```

It exits 0 when every verb's latest record passed on the tree as it is now, 1
when one failed, went stale or changed the tree during its run, and 3 when one
has no record, was unresolved or ran outside a git work tree, where no tree id
exists. The skill runs `format` first, cites records in this form, and calls
the work done only when `evidence` exits 0 or you accept what it reported.

A result a record cites is kept in the repository, where anyone can check it:
`meow-verbs evidence --keep [verb...]` copies each current record, with its
whole output, to `<record>.txt` under `evidence/` in your record's folder,
`project/evidence/` unless `[record] root` moves it, or under the
`evidence_dir` you declare under `[verbs]`. The file opens with
`meow-verbs evidence 1` and the record's verb, command, targets, outcome, exit
status, tree id and time. A stale record isn't kept. After writing, it asks git
whether the file is ignored: an ignored file is named with its rule and left
in place, exiting 1, and where git can't answer it exits 3. The tree id leaves
that directory out, so keeping a record doesn't make it stale, and
`meow-verbs tree <commit>` prints a commit's tree id the same way, for
comparing a kept record with the commit that carries it. Read a kept file
before you commit it, because it holds whatever the verb printed.

To run a verb over part of the work, such as one test, declare the form it
takes, with `{targets}` where the part goes:

```toml
[verbs.test]
command = "./scripts/test"
subset = "./scripts/test {targets}"
```

Then `meow-verbs run test -- tests/login` runs the subset form, with each
target quoted for the shell. A verb with no `subset` reports `no subset form`
and runs nothing, because running the whole work under the part's name would
tell you something narrower passed than did. `evidence` never counts a subset
run as the whole verb's result, and prints it beside that result as
`subset only`.

An unresolved verb is one of six kinds: undeclared, no profile, a profile
that doesn't parse, a declaration that isn't one command, no interpreter to
run the program, and, for a run over part of the work, no subset form.

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
