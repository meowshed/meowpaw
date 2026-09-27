---
reader: someone choosing or running meow-mise
answers: what meow-mise does, what it adds to a session and how to run it
kind: reference
describes: [meow-mise@0.1.0]
---

# meow-mise

`meow-mise` reports the tasks mise resolves in your repository: where each one
came from and what would stop a check running it unattended. It never trusts
a configuration, answers a prompt, runs a task or writes a file. It installs
on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-mise@meowpaw
```

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-mise status
```

From your own shell, run the same launcher by its path in the installed unit.

It prints mise's version and each directory's trust state, then every task
mise resolves in this work tree, which may differ from what your repository
declares. mise also reads parent directories, your own configuration and
`mise.local.toml`, so each task carries its origin: `repository` for a file
git tracks, `work tree only` for a file inside the work tree that git doesn't
track, and `outside` for a file beyond it. A task a committed file declares
and another file replaces says so.

Under a task, `blocked:` names what stops a check running it unattended:

| Block               | Means                                                   |
| ------------------- | ------------------------------------------------------- |
| `hidden`            | Its author marked it private                            |
| `asks for a person` | It sets `confirm`, as a TOML key or a `#MISE` header    |
| `needs <args>`      | It takes a required argument, read without running it   |
| `not committed`     | It comes from a file git doesn't track, or was replaced |
| `unknown <field>`   | mise's listing didn't say, so the program can't tell    |

A task declaring `sources` and `outputs` carries `can skip as fresh`: mise
exits 0 on a task it skipped, so a green result from it may be a previous
run's.

## What it reports instead of a list

It exits 0 when it reports the tasks and 3 when it can't, and it never reports
a state it couldn't read as an empty list:

| Line                                  | Means                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------- |
| `unresolved: not a mise repository`   | No mise configuration file or task directory; mise didn't run             |
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

## What it needs

Claude Code 2.1.280 or later, the version this unit was tested on, declared in
`plugins/meow-mise/requires.toml`; mise 2026.9.11 or later; and git.
