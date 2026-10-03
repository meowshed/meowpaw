---
reader: someone choosing or running meow-licence
answers: what meow-licence does, what it adds to a session and how to run it
kind: reference
describes: [meow-licence@0.3.0]
---

# meow-licence

`meow-licence` adds the licence header your repository declares to each file
Claude Code creates, and checks that every file your repository tracks is
covered by the licensing it declares, and reports a repository that declares
nothing as undeclared, never as covered. It installs on its own, with no other
part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-licence@meowpaw
```

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

## Have Claude Code head new files

When Claude Code creates a file in a repository that declares licensing, the
`meow-licence:header` skill adds the header you declared, in the comment form
the file's format permits, or in a `<file>.license` file beside a file that
can't carry a comment. It writes the lines under `[licence]`, or where you
declare none, copies the header your files already carry. It skips a file an
annotation in `REUSE.toml` covers, never changes a header a file already
carries, and where you declare nothing, writes nothing and says so.

## Run the check

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs the check in your repository as:

```bash
meow-licence check
```

From your own shell or a verb, run the same launcher by its path in the
installed unit.

It prints one line per finding, then a count: a file nothing covers, a header
or an annotation naming a copyright and no licence identifier or the other way
round, and a text in `LICENSES/` out of step with the licences you use, where
you keep that directory. It exits 0 when it finds nothing, 1 on a finding,
and 3 when your repository declares no licensing or the check can't run. It
reports licensing alone, and never who wrote a file. It also names the
profile's state, as `meow-licence check: profile: parsed`, and each key no
unit reads, which changes no exit status.

## What it costs you

The skill's description costs 281 characters in context on every turn. The
check is a native binary shipped inside
the unit, so it needs nothing installed on the machine except git, which it
reads the tracked files through. On a machine the unit carries no binary for,
the check reports the repository as unchecked and exits 3.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-licence/requires.toml`, and git.
