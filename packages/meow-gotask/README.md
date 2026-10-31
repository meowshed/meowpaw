---
reader: someone installing or running meow-gotask on Pi
answers: what meow-gotask provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-gotask@0.6.1]
---

# @meowshed/meow-gotask

Reports the tasks Task (go-task) resolves in a repository, with where each came from and what stops a stage running it unattended, binds the stages to them, and never trusts a remote Taskfile, answers a prompt or writes into the repository. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-gotask
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

## Remote includes

Before it lists anything, the program reads your Taskfile and every local
Taskfile it includes for an include naming a URL or a `git::` source, and
names each one. Where there is one, it lists nothing and reports `unresolved:
remote include`, because listing would need Task to fetch and trust that file,
which is your decision.

## Bind your stages to your tasks

`meow-gotask bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself. Commit what it prints, so the stages run from
the declaration the repository holds:

```toml
[stages]
test = "task --force test"
# lint: task lint is blocked: ignores errors
```

It binds a stage only to the task of exactly its name, and only a task that
carries no block. Every binding runs the task with `--force`, which runs its
dependencies too, so a pass is never a skip. A stage whose task is `internal`
reads as internal, not as missing.

`meow-gotask check` reads your profile's `[stages]`, finds each `task <name>`
in a stage's command, and reports every block on that task, a task it can't
find, and a task that can skip run without `--force`. It also reports each
remote include in your Taskfiles, whether or not a stage uses it. It exits 0 on
no finding, 1 on a finding and 3 when it can't read the profile or Task.

`check` reads the profile, so it prints the profile's state,
`profile: absent`, `profile: unparseable` or `profile: parsed`, and
`unknown key: <path>` for each key no unit reads, which changes no exit
status.

## What it reports instead of a list

No command ever reports a state it couldn't read as an empty list; each exits
3 with one of these:

| Line                                                   | Means                                                               |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| `unresolved: not a Task repository`                    | Git tracks no Taskfile, at the root or below it; Task didn't run    |
| `unresolved: task not found`                           | `task` isn't on `PATH`                                              |
| `unresolved: <file> doesn't parse`                     | A Taskfile isn't valid YAML                                         |
| `unresolved: remote include`                           | A Taskfile includes a remote one, named above it                    |
| `unresolved: a remote Taskfile this listing can't see` | Task refused with 104 or 106 for an include the program didn't find |
| `unresolved: environment: ...`                         | Your Task is older than 3.53.1, the version the unit was tested on  |
| `unresolved: meow-gotask defect: ...`                  | Task rejected a flag this unit passes; report it                    |
| `unresolved: unrecognised shape: ...`                  | Task printed a listing this unit can't read                         |
| `unresolved: task failed ...`                          | Task failed another way; its last lines follow                      |

## What it costs you

The skill's description stays in context on every turn, within the 380
characters the unit's budget states. The program is a native binary shipped
inside the unit, and needs Task and git on the machine. On a machine the unit
carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-gotask --help` lists the subcommands, and `meow-gotask <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
