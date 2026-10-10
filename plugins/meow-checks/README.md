---
reader: someone choosing or running meow-checks
answers: what meow-checks does, what it adds to a session and how to run it
kind: reference
describes: [meow-checks@0.10.0]
---

# meow-checks

`meow-checks` runs your repository's checks the way the repository declared
them, and reports a check nobody declared as unresolved, never as passed. It
covers five stages, `format`, `lint`, `check`, `test` and `build`, and it
installs on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-checks@meowpaw
```

## Declare your stages

Put one command per stage in `.meowpaw/profile.toml` at the repository's root.
Each command runs through the shell from that root:

```toml
[stages]
format = "./scripts/format --check"
lint = "./scripts/lint"
test = "./scripts/run-tests"
```

Declare only the stages your repository has. A stage you leave out is reported
as unresolved, which is the honest answer: nothing ran, so nothing passed.

## What Claude Code does with them

When Claude Code formats, lints, type-checks, tests or builds, the
`meow-checks:verify` skill has it run the program in place of a command it
would otherwise choose. It first shows what each stage resolves to:

```text
format     resolved    ./scripts/format --check   (from .meowpaw/profile.toml)
check      unresolved  undeclared: the profile doesn't name it; declare it under [stages] in .meowpaw/profile.toml
```

Then it runs the stages the work needs and reports each as passed, failed or
unresolved. A failed stage comes with its exact command, its exit status and its
whole output, led by its last lines, where a failing tool puts its error. The
program exits 0 only when every stage it ran passed, 1 when one failed, 4 when
one was interrupted by a signal and none failed, and 3 when one was
unresolved. Each run is recorded as started before the stage runs, so a run
cut short reads as `interrupted`, or as `running` while another session's
run is still going, and nothing retries it on its own.

Each run is recorded, so a claim that a check passed can name its record
instead of pasting output. `run` appends every stage it runs to a ledger in your
state directory, `$XDG_STATE_HOME/meowpaw/evidence/`, or
`~/.local/state/meowpaw/evidence/` where that variable is unset and
`%LOCALAPPDATA%\meowpaw\evidence\` on Windows, never in the repository. Each
record keeps the command, the outcome, the whole output and the git tree id of
your working state before and after the stage, and `run` ends with one
`recorded: <stage> <record> at tree <tree id>` line per stage.

`meow-checks evidence [stage...]` tells you whether those results still hold:

```text
test: passed, record 3f9a1c0b2d4e, current at tree 6960e730d656
lint: passed, record 8b21e4f07a9c, stale: ran on tree 1c4d2e9f0a3b, and the tree is now 6960e730d656
```

It exits 0 when every stage's latest record passed on the tree as it is now, 1
when one failed, went stale or changed the tree during its run, and 3 when one
has no record, was unresolved or ran outside a git work tree, where no tree id
exists. The skill runs `format` first, cites records in this form, and calls
the work done only when `evidence` exits 0 or you accept what it reported.

The repository keeps no run output. Where a record or a pull request cites a
result, it cites the line `evidence` printed: the stage, the outcome, the record
and the tree id. `meow-checks tree <commit>` prints a commit's tree id, for
comparing a cited result with the commit that carries the work.
`evidence --keep` and `evidence --kept`, which kept and listed such files,
exit 2 and say so, for one release. Where a submodule has uncommitted changes,
no result is bound to a tree, and `evidence` names the submodule.

The ledger itself is your machine's run state, kept outside the repository.
`meow-checks state` prints where it is, how many records it holds, the oldest
and newest and the lock, and `state --purge` empties
it. A run drops records older than 30 days. `MEOWPAW_STATE_DIR` moves the state
directory, and `MEOWPAW_STATE=off` writes nothing outside the repository, in
which case nothing is recorded. `evidence --all` adds
the other work trees of the same repository, each by its path.

To run a stage over part of the work, such as one test, declare the form it
takes, with `{targets}` where the part goes:

```toml
[stages.test]
command = "./scripts/test"
subset = "./scripts/test {targets}"
```

Then `meow-checks run test -- tests/login` runs the subset form, with each
target quoted for the shell. A stage with no `subset` reports `no subset form`
and runs nothing, because running the whole work under the part's name would
tell you something narrower passed than did. `evidence` never counts a subset
run as the whole stage's result, and prints it beside that result as
`subset only`.

An unresolved stage is one of six kinds: undeclared, no profile, a profile
that doesn't parse, a declaration that isn't one command, no interpreter to
run the program, and, for a run over part of the work, no subset form.

`status` and `run` open with the profile's state: `profile: absent`,
`profile: unparseable` or `profile: parsed`. An unparseable profile adds
`profile error: line <n>: <message>`, the parser's message and the line it
gives, and leaves every stage unresolved. A parsed one adds
`unknown key: <path>` for each key no unit of the harness reads, such as
`unknown key: stages.tset` for a mistyped `test`, so you learn why a setting
had no effect. The key is ignored and the exit status stays what it would be
without it.

## What it costs you

The skill's description costs 332 characters in context on every turn. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, every
stage is reported unresolved, as "no interpreter".

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-checks/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description: [documentation](https://code.claude.com/docs/en/skills.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)
