---
id: TSK-1780
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3010, REQ-3011]
issue: 309
---

# A retired name is recorded and never reused

A retired name is recorded and never reused, as ADR-1240 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record carrying `unit:` or `status: proposed`, when `check front-matter` runs, then it reports the line and what replaced the name. Closed by: a fixture.
2. Given this repository, when `check front-matter` runs, then it reports nothing. Closed by: the check's output.

## What to do

Add a `[retired]` table to `lib/layout.toml` naming the retired field `unit` and statuses `proposed` and `current`, each with what replaced it. In `check front-matter`, report a record carrying a retired field or status, and a kind in the layout declaring one.

## Depends on

Nothing. ADR-1240 is approved.

## Evidence

`lib/layout.toml` gains a `[retired]` table recording the field `unit` and
the statuses `proposed` and `current`, each with what replaced it, taken from
this record's history. Two fixtures, each seen passing against the program and
failing against a stub that returns nothing: `check front-matter` reports a
decision with `status: proposed` as retired and replaced by draft, and one
carrying `unit:` as a retired field, each at its line; and a layout whose
specification kind declares `current` fails with "the kind specification
declares current, a retired name". This repository reports `front-matter: 0 findings`.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 104 tests in 6.878s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=101, errors=3)
```

## Left alone

A command that runs a migration, which ADR-1240 leaves.
