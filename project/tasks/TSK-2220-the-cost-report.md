---
id: TSK-2220
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1440
closes: [REQ-1072, REQ-1074]
issue: 493
projected: b5a1f3492e0d
---

# `meow-author cost` reports each unit's cost and use, in the gate

`meow-author` gains `cost`, which reports what each unit keeps in context on
every turn against its budget and names `/skill-doctor` for each skill's use,
and this repository's `budget` task runs it. One task, one branch, one
pull request, one review.

## Acceptance criteria

1. Given this repository, when `meow-author cost` runs, then it prints each
   unit's characters against its budget and exits 0. Closed by: its output,
   and the `budget` task running it.
2. Given fixtures with a unit over its budget, a unit with no
   `budget.toml`, and a description over 1,536 characters, when it runs, then
   it exits 1 naming each. Closed by: fixtures naming REQ-1072, seen failing
   first.
3. Given any repository, when `meow-author cost` runs, then its report names
   `/skill-doctor` as where each skill's use is reported. Closed by: a fixture
   naming REQ-1072.

## What to do

Port `tools/check_budget.py` to a `cost` command of the native tool's
`author` subcommand, capping a description and its `when_to_use` together, and
end its report by naming `/skill-doctor` for each skill's use. Read none of the
platform's session transcripts. Point the `budget` task at it and
delete the script. State the command on `meow-author`'s page.

## Depends on

Nothing. ADR-1460 is approved.

## Evidence

`meow-author cost` ports `tools/check_budget.py` to the `author` subcommand:
it reports each unit's permanent characters against its budget, capping a
description and its `when_to_use` together, fails on an overrun, a missing
budget or a description over the cap, and ends by naming `/skill-doctor` for
each skill's use. It reads no session transcript. On this repository it
reports the same number for every unit as the script it replaces, and the
`budget` task runs it through `cargo`, in the `lint` verb and `mise run all`.
The script is gone, the budget files name "the budget check" where they named
it, and `meow-author` is at 0.3.0 with its page stating the command.

Four fixtures in `Cost`, three naming REQ-1072 and one REQ-1074, failed
against `main`'s program and pass against this one:

```text
$ MEOW_AUTHOR_BIN=<main's meow-author> python3 -m unittest ... -k Cost
FAILED (failures=4)
$ python3 -m unittest discover -s plugins/meow-author/tests
OK
$ mise run budget
12 units, 0 budget failures
How often each skill is used: run /skill-doctor in Claude Code, which reports each skill's cost and invocations.
```

## Left alone

The skill's rules, which TSK-2230 adds.
