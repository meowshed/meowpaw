---
id: TSK-2140
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1390
closes: [REQ-2908]
issue: 451
projected: 974f193b0af8
---

# The verbs are named `format`, `lint`, `check`, `test` and `build`

`meow-verbs` 0.3.0 names the new verbs in its program, skill and page, reads
`fmt` and `typecheck` for one release with a notice, and every file naming a
verb names the new ones. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a profile declaring the new names, when `meow-verbs status` and
   `meow-verbs run format` run, then the five new names are listed and
   `format` runs its command. Closed by: fixtures.
2. Given a profile declaring `fmt`, when `meow-verbs status` runs, then
   `format` resolves from it and a notice names the key and 0.4.0; given
   `meow-verbs run typecheck`, then `check` runs with the same notice; given
   both names declared, then the new one wins and the notice names the key
   ignored. Closed by: fixtures, seen failing first.
3. Given the tree, when it is searched for `fmt` and `typecheck` as verbs,
   then only the program's reading of the old names and its fixtures remain.
   Closed by: the search's output.

## What to do

Rename the verbs in the native tool's `verbs` subcommand and the launcher's
fallback, keep a table of the old names read until 0.4.0, and print the
notice ADR-1410 describes. Rename them in the skill, its description, the
unit's page and manifest, this repository's profile, the profile template,
the tutorial, the introduction, the vision, `README.md` and SPC-1040, and in
`meow-core`'s cases that name a verb. `meow-verbs` moves to 0.3.0.

## Depends on

Nothing. ADR-1410 is approved.

## Evidence

`meow-verbs` 0.3.0 names the verbs `format`, `lint`, `check`, `test` and
`build` in its program, its launcher's fallback, its skill and description,
its page and manifest. It reads `fmt` and `typecheck` from a profile or the
command line with a notice naming 0.4.0, and where both names are declared the
new one wins and the notice names the key it ignored. This repository's
profile declares `format`, and the profile template, the tutorial, the
introduction, the vision, `README.md`, SPC-1040 and `meow-core`'s case name
the new verbs. The pages describing `meow-verbs` are restamped at 0.3.0.

Seven fixtures failed against `main`'s program and pass against this one:

```text
$ MEOW_VERBS_BIN=<main's meow-verbs> python3 -m unittest discover -s plugins/meow-verbs/tests
FAILED (failures=4, errors=3)
$ python3 -m unittest discover -s plugins/meow-verbs/tests
OK
$ plugins/meow-verbs/bin/meow-verbs run format lint test
summary: format passed, lint passed, test passed
```

The `meow-verbs` 0.2.0 installed on this machine reports `format` unresolved,
because it predates the rename, so this repository's own program ran the
verbs. A search for `fmt` and `typecheck` as verbs finds them only in the
program's table of old names and its fixtures; `fmt-check` names this
repository's own task and stays.

## Left alone

This repository's `mise` tasks, such as `fmt-check`, which name the
repository's own tasks and not the harness's verbs.
