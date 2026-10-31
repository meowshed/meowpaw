---
reader: someone installing or running meow-mise on Pi
answers: what meow-mise provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-mise@0.6.1]
---

# @meowshed/meow-mise

Reports the tasks mise resolves in a repository, with where each came from and what stops a stage running it unattended, binds the stages to them, and never grants trust, answers a prompt or writes a file. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-mise
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

## Bind your stages to your tasks

`meow-mise bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself. Commit what it prints, so the stages run from
the declaration the repository holds:

```toml
[stages]
test = "mise run --force test"
# lint: task lint is blocked: hidden
```

It binds a stage only to the task of exactly its name, so a task named `tests`
or `unit` is never bound to `test`, and only a task that carries no block.
Every binding runs the task with `--force`, so a task mise would skip as fresh
runs, and a passing stage is never a skip. Each stage it leaves unbound is a
comment with the reason.

`meow-mise check` reads your profile's `[stages]`, finds each `mise run <task>`
in a stage's command, including each part of a chain joined by `&&`, `||` or
`;`, and reports every block on that task, a task it can't find, and a task
that can skip as fresh run without `--force`. It exits 0 on no finding, 1 on a
finding and 3 when it can't read the profile or mise, so you can run it in
your own gate.

`check` reads the profile, so it prints the profile's state,
`profile: absent`, `profile: unparseable` or `profile: parsed`, and
`unknown key: <path>` for each key no unit reads, which changes no exit
status.

## What it reports instead of a list

`status` exits 0 when it reports the tasks in every directory and 3 when it
can't in one, and no command ever reports a state it couldn't read as an
empty list. `bind` and `check` read the root alone, because they read the
root profile's stages:

| Line                                  | Means                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------- |
| `unresolved: not a mise repository`   | Git tracks no mise configuration file or task directory; mise didn't run  |
| `unresolved: mise not found`          | mise isn't on `PATH`                                                      |
| `unresolved: untrusted <directory>`   | mise needs the configuration trusted; read it, then run the command shown |
| `unresolved: environment: ...`        | Your mise is older than 2026.9.11, the version the unit was tested on     |
| `unresolved: meow-mise defect: ...`   | mise rejected a flag this unit passes; report it                          |
| `unresolved: unrecognised shape: ...` | mise printed a listing this unit can't read                               |
| `unresolved: mise failed ...`         | mise failed another way; its last lines follow                            |

Listing the tasks runs mise over your configuration, and on a trusted
configuration mise evaluates its templates, which can run code. The report
names each committed configuration file whose templates call `exec`.

## What it costs you

The skill's description stays in context on every turn, within the 380
characters the unit's budget states. The program is a native binary shipped
inside the unit, and needs mise and git on the machine. On a machine the unit
carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-mise --help` lists the subcommands, and `meow-mise <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
