---
id: TSK-2440
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1550
closes: [REQ-1316, REQ-2354, REQ-2468, REQ-2474, REQ-2492, REQ-2504]
issue: 581
projected: 6646840e88ad
---

# Bind the verbs to their tasks and check the profile's bindings

`meow-mise bind` prints a `[verbs]` table binding each verb to the task named
exactly as it, run with `--force`, and `meow-mise check` reports every block
on a task a profile's verb runs, as SPC-1140 states. One task, one branch,
one pull request, one review.

## Acceptance criteria

1. Given tasks `test`, `tests`, `unit` running the tests and a blocked
   `lint`, when `bind` runs, then it prints `test = "mise run --force test"`,
   binds nothing else and prints each unbound verb's reason. Closed by:
   fixtures naming REQ-1316, REQ-2354, REQ-2468, REQ-2474 and REQ-2492, seen
   failing first.
2. Given a profile whose `test` runs a skippable task without `--force`, when
   `check` runs, then it exits 1 naming the finding; on this repository's
   profile it exits 0. Closed by: fixtures naming REQ-2468.
3. Given a repository, when `status`, `bind` and `check` have run, then
   `git status --porcelain --ignored` reads as before, and no
   `mise.local.toml` exists. Closed by: a fixture naming REQ-2504.

## What to do

Add `bind` and `check` to the `mise` module, and describe both in the skill
and the README.

## Depends on

TSK-2420, which ships the unit and `status`.

## Evidence

Closes REQ-1316, REQ-2354, REQ-2468, REQ-2474, REQ-2492 and REQ-2504. Of the
12 fixtures in the `Bind`, `Check` and `WritesNothing` classes, 11 failed
first against the unit TSK-2430 left. `WritesNothing` passed then too, since a
program without `bind` or `check` writes nothing either, so it holds REQ-2504
only now that both commands exist. All 38 in the file pass. The `lint` verb
now runs `meow-mise check`, which reports 0 findings in the 7 task runs this
repository's verbs name. `meow-verbs evidence --keep format lint test` exits 0
on this change's own tree, each result kept in `project/evidence/`, as the
pull request cites.

## Left alone

This repository's own profile, which keeps its hand-written verbs; `bind`
never writes it.
