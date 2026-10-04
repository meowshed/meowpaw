---
id: TSK-2020
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1340
closes: [REQ-3166]
issue: 402
projected: d0afbc78b9e2
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

`bin/paw` is the unit's launcher, and `bin/meow-method` is the alias: it
prints to standard error that the command is now `paw` and that 0.31.0 removes
the old name, then runs `paw` with the same arguments. The `record`
subcommand names `paw` in every usage line and message, and the index markers
keep `meow-method`. The skills, the hook, the templates, `CLAUDE.md`, the
profile, the specifications and `docs/meow-method.md` run `paw`. The unit is
at 0.30.0.

Three fixtures in `Named`, each naming REQ-3166, failed against the tree
before the change, with a `paw` launcher copied from the old one:

```text
$ python3 -m unittest plugins/meow-method/tests/test_record.py -k Named
FAIL: test_every_usage_line_and_message_names_paw
FAIL: test_nothing_the_unit_ships_runs_the_old_name
FAIL: test_the_alias_says_it_is_deprecated_and_runs_paw
FAILED (failures=3)
```

After the change, through the repository's verbs:

```text
$ plugins/meow-verbs/bin/meow-verbs run test fmt lint
== test: `crates/meow/build-units && ... && plugins/meow-method/bin/paw check && ...`
passed, exit status 0 after 8.1s
Ran 126 tests in 4.571s
OK
== fmt: `mise run fmt-check`
failed, exit status 127: mise: not found
== lint: `mise run lint && ...`
failed, exit status 127: mise: not found
```

`fmt` and `lint` failed only because `mise` isn't installed on the machine
that ran them, so their commands ran directly: `prettier --check '**/*.md'`
reports the same three files it reported before this change, none of them
touched here; `markdownlint-cli2 '**/*.md'` reports 0 issues; `style`,
`prompts`, `kernel`, `standalone` and `budget` pass; and `cargo test` over the
crate passes.

## Left alone

The unit's name, its skills and commands, and the index markers, which
ADR-1350 keeps.
