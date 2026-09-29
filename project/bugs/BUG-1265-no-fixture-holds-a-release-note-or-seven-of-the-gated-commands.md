---
id: BUG-1265
artifact: bug
status: approved
severity: minor
violates: REQ-3182
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue:
---

# No fixture shows the prose gate holding a release note, or seven of the ten commands it reads

`plugins/meow-prose-gate/tests/test_gate.py` holds a text back only for
`git commit`, `gh pr create` and `gh issue create`. No fixture runs
`gh release create` or `gh release edit`, or passes a text through `--notes`
or `--notes-file`, and none runs `gh pr edit`, `gh pr comment`,
`gh pr review`, `gh issue edit` or `gh issue comment`. The program holds each
of them today, so a change that stopped holding one would still pass every
fixture. EPC-1590's criterion 5 asks for a fixture for each command the gate
reads, so the criterion is unmet.

## Reproduction

`main` after #696, with `meow-prose-gate` 0.2.0, on macOS on arm64.

1. List the commands `plugins/meow-prose-gate/hooks/hooks.json` routes to
   `meow-prose-gate check`: ten `if` patterns, from `git commit *` to
   `gh release edit *`.
2. Search `plugins/meow-prose-gate/tests/test_gate.py` for `release`,
   `--notes`, `pr edit`, `pr comment`, `pr review`, `issue edit` and
   `issue comment`.

## What the system does

The search finds none of the seven. The fixtures pass a text through `-m`,
`-F`, `--body` and `--body-file`, and through no other argument. The program
itself holds every form: I fed the launcher a hook event for each of the ten
commands with the idiom `low-hanging fruit` in `-m`, `--body` or `--notes`,
and a body in `--body-file` or `--notes-file` for four of them, and each
exited 2 with a finding quoting the span. The same idiom in
`gh pr merge --squash --body` exited 0, as ADR-1600 accepts.

## What it should do, and why

A fixture should hold a text back for each of the ten commands the hook
routes, and for each argument the program reads the text from, `--notes` and
`--notes-file` included. REQ-3182 asks the harness to check every text before
it publishes it, and a form no fixture holds can stop being checked without
any check failing.

## Triage

It enters at cover, because the requirement is right and the program meets it:
the checks miss what REQ-3182 asks. Minor, because each command is held today
and only the guard against a regression is missing.

## Closed by

A fixture in `plugins/meow-prose-gate/tests/test_gate.py` for each of the ten
commands and for `--notes` and `--notes-file`, each asserting exit 2 and a
span found verbatim in the command.

## Tasks

- [ ] T-001 TSK-2575 add a fixture for each gated command and each text
      argument, in `plugins/meow-prose-gate/tests/test_gate.py`
