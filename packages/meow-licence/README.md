---
reader: someone installing or running meow-licence on Pi
answers: what meow-licence provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-licence@0.7.1]
---

# @meowshed/meow-licence

Adds the licence header a repository declares to each file Pi creates, never rewrites one, and checks that every tracked file is covered by the licensing declared in REUSE.toml, in .meowpaw/profile.toml or in its files' headers. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-licence
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

## Declare your licensing

Declare it in any of three ways, and combine them if you like:

- a `REUSE.toml` at the repository's root, whose annotations cover files in
  bulk;
- a `[licence]` table in `.meowpaw/profile.toml`, listing your header's lines;
- a header in each file: an `SPDX-FileCopyrightText` line and an
  `SPDX-License-Identifier` line within its first 20 lines, or in a file
  beside it named `<file>.license`.

```toml
[licence]
header = [
  "SPDX-FileCopyrightText: 2026 A Person <a@example.org>",
  "SPDX-License-Identifier: Apache-2.0",
]
```

A licence text, in `LICENSES/` or in a file named `LICENSE`, `LICENCE` or
`COPYING`, needs no declaration, and neither does `REUSE.toml`.

## Have Pi head new files

When Pi creates a file in a repository that declares licensing, the
`meow-licence:header` skill adds the header you declared, in the comment form
the file's format permits, or in a `<file>.license` file beside a file that
can't carry a comment. It writes the lines under `[licence]`, or where you
declare none, copies the header your files already carry. It skips a file an
annotation in `REUSE.toml` covers, never changes a header a file already
carries, and where you declare nothing, writes nothing and says so.

## What it costs you The

check is a native binary shipped inside
the unit, so it needs nothing installed on the machine except git, which it
reads the tracked files through. On a machine the unit carries no binary for,
the check reports the repository as unchecked and exits 3.

## Read a subcommand's help

`meow-licence --help` lists the subcommands, and `meow-licence <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
