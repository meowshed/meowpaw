---
reader: someone installing or running meow-git on Pi
answers: what meow-git provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-git@0.7.1]
---

# @meowshed/meow-git

Refuses a git commit on the trunk the repository declares, and checks every commit a push would publish for the declared commit convention and for a good signature, before the push runs. It keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-git
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Declare your policy

Put it under `[git]` in `.meowpaw/profile.toml`:

```toml
[git]
trunk = "main"
require_signatures = true
```

## Branch names

The push guard refuses a push from a branch whose name carries a date, such as
`2026-09-26` or `20260926`, or the author's name, because the code host already
stores both. Name the branch for the change instead, such as
`fix/1234-read-the-trunk`; an issue number followed by other numbers isn't
read as a date.

## Rebuild a stack

When a branch low in a stack changes, run `meow-git restack` with the stack's
branches from the bottom up to rebase each onto the one below it, the first
onto the trunk you declare under `[git]`:

```bash
meow-git restack feat/read-the-base feat/report-the-checks feat/review-one-layer
```

It rebases a branch only where its base moved, and where you require
signatures it signs every commit it writes again. It pushes nothing. For each
branch it rewrote, it prints `updated:` and the push that publishes it, with
the lease naming the remote-tracking revision it read before the rewrite, so
the push replaces only the revision you last saw. A conflict aborts that
rebase, so neither side is lost, prints `conflict:` with the branch and its
files, and exits 1. Wherever it stops, it prints `updated:` for each branch it
rewrote and `not updated:` for each it didn't reach. If a branch has
uncommitted changes or is checked out in another working tree, it rewrites
nothing and names that branch.

The pack is current as of git 2.56.0, observed on 2026-10-24.

## Read a subcommand's help

`meow-git --help` lists the subcommands, and `meow-git <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## Hooks

`commit-guard` stops a commit on the declared trunk; the `meow-scm:commit` skill says why, and `mise run layers` fails a trunk with a commit GitHub didn't make.
`push-guard` stops a push of a commit whose message or signature fails the declared convention; the `meow-scm:commit` skill says why, and `mise run layers` fails a branch whose commits fail it.
`irreversible-guard` asks the person before each push in a session they attend, and never answers for them; rule M25 of the `meow-flow:method` skill says why, and `mise run test-crate` fails a guard whose second push doesn't ask again.
