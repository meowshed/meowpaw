---
reader: someone choosing or running meow-git
answers: what meow-git does, what it adds to a session and how to run it
kind: reference
describes: [meow-git@0.5.0]
---

# meow-git

`meow-git` is a pack for repositories that use `git`. It refuses a commit on
the trunk you declare, and before a push runs it checks every commit the push
would publish: the message against your commit convention, and the signature
where you require one. It installs on its own, and it checks the message with
`meow-scm`, which installing this pack enables.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-git@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone. It also enables `meow-scm`, whose message check the push guard runs, and keeps `meow-scm` enabled while this pack is on.

## Declare your policy

Put it under `[git]` in `.meowpaw/profile.toml`:

```toml
[git]
trunk = "main"
require_signatures = true
```

## What it does

When Claude Code runs `git commit` on the trunk, the pack refuses it and says
to take a branch. On any other branch the commit runs.

When Claude Code runs `git push`, the pack reads every commit reachable from
the current head that no remote-tracking branch already has, and refuses the
push if any of them fails, naming each failing commit:

```text
meow-git: refused the push; 1 problem in the 2 commits it would publish:

3f2a91c fix: stop the retry loop
    signature: the commit is unsigned
```

A message is checked with `meow-scm check-message` against the convention you
declared under `[commits]`. Where `meow-scm` isn't installed, the pack says
the message check is unrun, and never that it passed.

Where you require signatures, only a good signature from a key your repository
trusts passes. A commit that is signed but can't be verified here, because the
key or the list of allowed signers is missing, is reported as unverifiable, and
never as unsigned. A commit that fails can still be amended, because nothing
has left the machine.

Without a `[git]` table, the pack refuses nothing on commit, still checks
messages on push, and says the trunk and the signing policy are undeclared.

Each hook's report names the profile's state, as
`meow-git push-guard: profile: parsed`, and each key no unit reads, as
`meow-git push-guard: unknown key: git.trnk`. An unknown key refuses
nothing.

## What it costs you

Nothing in context: the pack is two hooks, and each runs only on its own
command. A push takes one message check and one signature check per commit.
The program is a native binary shipped inside the pack, so it needs nothing
installed on the machine; on a machine the pack carries no binary for, it denies the
commit or the push and names `claude plugin install meow-core@meowpaw`.

## Branch names

The push guard refuses a push from a branch whose name carries a date, such as
`2026-09-26` or `20260926`, or the author's name, because the code host already
stores both. Name the branch for the change instead, such as
`fix/1234-read-the-trunk`; an issue number followed by other numbers isn't
read as a date.

## Read a subcommand's help

`meow-git --help` lists the subcommands, and `meow-git <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## Hooks

`commit-guard` stops a commit on the declared trunk; the `meow-scm:commit` skill says why, and `mise run layers` fails a trunk with a commit GitHub didn't make.
`push-guard` stops a push of a commit whose message or signature fails the declared convention; the `meow-scm:commit` skill says why, and `mise run layers` fails a branch whose commits fail it.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-git/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- `PreToolUse` command hooks filtered by an `if` rule, which Claude Code applies as a best-effort filter: [documentation](https://code.claude.com/docs/en/hooks.md)
