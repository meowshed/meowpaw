---
id: TSK-2020
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1340
closes: [REQ-3166]
issue:
---

# The record's command is `paw`, with `meow-method` as a deprecated alias

A person runs the record's command as `paw`, as ADR-1350 decides, and
`meow-method` keeps working for one release while saying so. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given the clean fixture record, when `bin/paw check` runs, then it exits 0,
   and every usage line and message the program prints names `paw` and never
   `meow-method`. Closed by: the fixtures run through `bin/paw`, and a fixture
   asserting a usage line.
2. Given the same record, when `bin/meow-method check` runs, then standard
   error names `paw` and 0.31.0, and standard output and the exit status
   equal those of `bin/paw check`. Closed by: a fixture.
3. Given the unit's skills, hook and templates, `CLAUDE.md`, the profile, the
   specifications and the documentation, when they are searched for
   `meow-method` followed by a subcommand or `bin/meow-method`, then nothing
   is found outside the alias itself. Closed by: a fixture searching the
   unit, and `grep` over the rest.

## What to do

Make `bin/paw` the unit's launcher, turn `bin/meow-method` into the alias
ADR-1350 describes, make the `record` subcommand print `paw` in its usage
lines and messages, and change every place that runs the command. Keep the
index markers `<!-- meow-method index -->` as they are. Bump the unit's
version to 0.30.0.

## Depends on

Nothing. ADR-1350 is approved.

## Evidence

Not yet.

## Left alone

The unit's name, its skills and commands, and the index markers, which
ADR-1350 keeps.
