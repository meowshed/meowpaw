---
reader: someone installing or running meow-scm on Pi
answers: what meow-scm provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-scm@0.8.0]
---

# @meowshed/meow-scm

Checks a commit message against the convention the repository declares in .meowpaw/profile.toml and against a ban on crediting a tool, before the message is used, and reports an undeclared convention as undeclared, never as met. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-scm
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

## Declare your convention

Put it under `[commits]` in `.meowpaw/profile.toml` at the repository's root:

```toml
[commits]
subject_limit = 72
trailers = ["Signed-off-by"]
may_name = ["Ada Lovelace <ada@example.org>"]

[commits.types]
feat = "minor"
fix = "patch"
docs = "none"
```

Each type says what it means for a release: `major`, `minor`, `patch` or
`none`. The subject limit is 72 where you don't declare one, and every trailer
you name must appear on every message. `may_name` lists each person, as
`Name <address>`, who agreed to be named in a trailer, and
`meow-scm convention` prints the list.

## What it costs you The

program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, the
check reports the message as unchecked and exits 3.

## The sign-off records the route

Where a message carries `Signed-off-by` trailers, the check compares the first
with the commit's author as git reports it, and refuses one naming anybody
else, because the chain starts with the author's own statement. Each later
sign-off names someone the change passed through, so it is a trailer naming a
person, and passes only where it names the author or someone `may_name`
lists. Where git reports no author, the check says the sign-off wasn't
compared.

A trailer names a person when its value has the form `Name <address>`, such as
`Co-authored-by`, `Reviewed-by` or `Acked-by`. Three trailers record where
something came from and are exempt: `Signed-off-by` naming the author,
`Cherry-picked-from` and `Fixes`.

The sign-off route and the person rule read only the message's last
paragraph, because git reads trailers from there, and they match a key in any
case. The check for a trailer the convention requires still reads every line
after the subject, with the key as you declared it.

## Read a subcommand's help

`meow-scm --help` lists the subcommands, and `meow-scm <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
