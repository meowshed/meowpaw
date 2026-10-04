---
id: ADR-1350
artifact: adr
status: done
revised: 2026-09-26
addresses: [REQ-3166]
supersedes: []
---

# 1350. The record's command is `paw`, and `meow-method` stays one release as a deprecated alias

**Amended by ADR-1390.** The unit is `meow-flow`, its skills and commands are
named for it, and the index markers become `<!-- meow-flow index -->`. The
`bin/meow-method` alias never shipped, and none ships. `meow-method` 0.30.0
ships as a stub that says where the unit went, and `meow-flow` ships at
0.31.0. The command stays `paw`.

## Decision

`meow-method` ships its command as `bin/paw`. A person, a skill, a hook and
the profile run `paw check`, `paw status`, `paw show` and the rest, and every
message the command prints names itself `paw`. The unit keeps the name
`meow-method`, and so do its skills, its commands such as `/meow-method:run`,
and the markers the record's indexes carry.

`bin/meow-method` stays as an alias for one release. It prints to standard
error that the command is now `paw`, naming the release that removes the
alias, and then runs `paw` with the same arguments, so its output and exit
status are `paw`'s. Release 0.30.0 of the unit announces the rename, and
0.31.0 removes the alias.

After this decision a person types `paw` where they typed `meow-method`, and
a script that still calls `meow-method` works, and says it has to change,
until 0.31.0. What still doesn't work: nothing tells a script's author before
it runs, and after 0.31.0 an unchanged script finds no command.

## Why

The owner decided the name on 2026-09-26: `meow-method` is long to type for
the command the method runs most, and `paw` completes the product's name
rather than repeating the unit's. The command is part of the harness's public
interface (REQ-2992), and a deprecation is announced in one release and
removed in a later one (REQ-3004, RES-0264), so the old name can't simply
disappear.

The messages move with the command because a message that names a command
the person didn't run sends them looking for the wrong one. The index markers
don't move, because they are the record's shape, not the command's name, and
changing them would migrate every index under ADR-1240 for nothing a reader
sees.

The strongest objection: two names for one command, even briefly, is exactly
the kind of alias that outlives its window. It is, and the alias names its
removal release in every message it prints, so leaving it past 0.31.0 is a
visible failure rather than a quiet one.

## Alternatives

| Option                                          | Better at                                          | Why it lost                                                                 |
| ----------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------- |
| Do nothing                                      | No change for anyone who learnt `meow-method`      | The owner decided the name                                                  |
| Rename, with a deprecated alias for one release | A script keeps working, and says it has to change  | Chosen                                                                      |
| Rename with no alias                            | One name from the first day, and nothing to remove | Breaks every script calling `meow-method` without warning, against REQ-3004 |
| Rename the shared native binary `meow` instead  | One name for the tool every unit carries           | Nobody types that binary; the owner named the command a person runs         |
| Rename the unit to `paw`                        | One name for the unit and its command              | The owner kept the unit's name, and its install instructions would all move |

## What it costs

Every document, skill, hook and fixture that names the command changes once.
A repository whose profile or scripts call `meow-method` changes them within
one release. The alias is a second file to keep until 0.31.0.

## What would reverse it

- A platform that installs a unit's commands by the unit's own name only, so
  that `paw` can't be reached where `meow-method` can.

## Consequences

- `plugins/meow-method/bin/paw` is the launcher; `bin/meow-method` becomes
  the alias.
- The native tool's `record` subcommand prints `paw` in every usage line and
  message.
- The skills, the hook, the templates, `CLAUDE.md`, the profile, the
  specifications and the documentation name `paw`.
- A task in 0.31.0 removes the alias.

## How I will know it was realised

1. `plugins/meow-method/bin/paw check` checks the record, and every message
   and usage line it prints names `paw`.
2. `plugins/meow-method/bin/meow-method check` prints to standard error that
   the command is `paw` and that 0.31.0 removes the alias, and its standard
   output and exit status equal `paw`'s.
3. No skill, hook, template, specification, documentation page, `CLAUDE.md`
   or the profile runs `meow-method` as a command.
4. REQ-3166 lands in exactly one closed task.

## What this does not settle

- The names of the other units' commands, such as `meow-verbs` and
  `meow-scm`, which keep theirs.
- The name of the native binary every unit carries, which stays `meow`.
- The task that removes the alias in 0.31.0, which is written when 0.30.0 is
  released.
