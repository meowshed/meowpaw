---
reader: someone installing or running meow-git on Pi
answers: what meow-git provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-git@0.5.0]
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
