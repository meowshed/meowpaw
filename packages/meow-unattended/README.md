---
reader: someone installing or running meow-unattended on Pi
answers: what meow-unattended provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-unattended@0.6.1]
---

# @meowshed/meow-unattended

Prints the posture an unattended run is held to from the [unattended] table a repository declares: the permission mode, the gates the run may decide, its release command and whether it may amend an approved record, with each deny rule and what the rules don't stop. It writes nothing, starts nothing and keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-unattended
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

## Declare the posture

A run's authority comes from this table and never from what a session would
default to:

```toml
[git]
trunk = "main"

[unattended]
permission_mode = "dontAsk"
gates = ["review", "merge"]
release = false
amend_approved = false
```

| Key               | Holds                                                                                           | Where it's absent  |
| ----------------- | ----------------------------------------------------------------------------------------------- | ------------------ |
| `permission_mode` | The mode the session must be in: one of `dontAsk`, `acceptEdits` or `auto`                      | unresolved, exit 3 |
| `gates`           | The gates the run may decide, each a step of the chain or `merge`; an empty list decides none   | unresolved, exit 3 |
| `release`         | The release command, run from the repository's root once after a merge, or `false` for none     | unresolved, exit 3 |
| `amend_approved`  | Whether the run may edit an approved requirement or decision in place, which the record forbids | `false`            |

The start command checks `permission_mode` against the mode the session is in
and refuses a mismatch with both modes named, because a run can't change the
session's mode and a mode it didn't declare is a posture nobody chose.
`bypassPermissions` is refused. `release = false` declares that the repository
has no release, and the run then releases nothing. `[git] trunk` has to be
declared, because the push rule needs a branch to protect.

## Print it

Run the launcher by its path in the installed unit, from the repository:

```bash
meow-unattended plan
```

It exits 0 for a resolved posture, 3 for an unresolved one and 2 for a usage
error, and it reports every refusal it finds before it exits, so one run names
every key a repository has to fix.

## What the deny rules don't stop

A Bash deny matches the command's text, so a push hidden in a script passes
it. A merge through the code host's interface needs no push, so no deny rule
stops it, and the checks the run makes before a merge hold it. A new record
whose front matter supersedes or withdraws an approved one retires it without
editing its file, so no deny rule stops that either.

## What it reports instead of a plan

Each refusal is a line starting `unresolved:` and the exit status is 3:

| State                                                  | Reported as                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| No profile, or no `[unattended]` table                 | `unresolved: no [unattended] table in .meowpaw/profile.toml`             |
| The profile isn't valid TOML                           | `unresolved: the profile doesn't parse: <reason>`                        |
| A required key is missing                              | `unresolved: [unattended] <key> is not declared`, once for each          |
| `permission_mode` is `bypassPermissions` or not listed | `unresolved: [unattended] permission_mode <value> is refused`            |
| A gate outside the steps and `merge`                   | `unresolved: [unattended] gates names <value>, which is not a gate`      |
| `gates` isn't a list of strings                        | `unresolved: [unattended] gates <value> is not a list of strings`        |
| `release` is neither a string nor `false`              | `unresolved: [unattended] release <value> is not a command or false`     |
| `amend_approved` isn't `true` or `false`               | `unresolved: [unattended] amend_approved <value> is not true or false`   |
| The profile declares no `[git] trunk`                  | `unresolved: [git] trunk is not declared, so the push rule has no trunk` |

On a machine where the core unit's binary isn't found, the launcher reports
that and names `meow-core`, which ships the shared binary.

## What it costs you

The unit ships no skill, so it keeps nothing in context on every turn, and its
budget states zero characters. It runs the shared binary that `meow-core`
ships, and needs git on the machine.

## Read a subcommand's help

`meow-unattended --help` lists the subcommands, and `meow-unattended <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
