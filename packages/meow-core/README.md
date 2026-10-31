---
reader: someone installing or running meow-core on Pi
answers: what meow-core provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-core@0.11.0]
---

# @meowshed/meow-core

Shapes every reply Pi makes to you: the action first, a failure as cause, location and fix, and no preamble, recap or offer of further help. It replaces your own output style while it is enabled. Distributed as a Pi package.

## What you get

Replies lead with the command, the path or the line. A failure arrives as its
cause, its location and its fix, with no dismay in front of it. Nothing opens
by announcing what is about to happen, and nothing closes by recapping it or
offering further help. Where a run stops, the last line names the command that
resumes it.

Nothing is dropped for the sake of brevity. A verification report keeps every
stage, a review keeps every finding, a gap list keeps every question, and a
hedge that carries real uncertainty stays, because deleting it manufactures
confidence you have not earned.

## The secrets rule

The style's last rule says never to read, print or transmit a repository's
secret material, and never to place it in an artifact, a commit or a reply,
because what reaches one of them is published and can't be taken back. It
never yields, and the block a subordinate agent is given carries it too.

## What it costs you

The unit declares its style as one that replaces the output style you
selected for yourself, because a reply shape that a person can switch off is
switched off in the report that most needs it. Pi discovers the
style but doesn't yet apply it by itself, so select it once with
`/output-style meow-core:meow`, and it stays selected across sessions.

It keeps the platform's own software engineering instructions, so you lose none
of them by enabling it.

## Install it

```bash
pi install npm:@meowshed/meow-core
```

The npm tarball carries the all-features paw executable for every platform
(REQ-4612), so the install makes no request and needs no checkout. Every
other meowpaw package's launcher falls back to this binary, so the core
package is the one install every layer sits beside. A git-source install
downloads the binary in its `postinstall` instead.

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script; the person
installing it runs `node install-meow.mjs` by hand to fill the platform
directory the checkout ignores.

## Hooks

`write-root` stops nothing: at the start of a session it records where the unit is installed, so the other units find the shared binary.

`reply-shape` is a Claude Code hook and runs nowhere in this package, which delivers the reply shape through its extension.
