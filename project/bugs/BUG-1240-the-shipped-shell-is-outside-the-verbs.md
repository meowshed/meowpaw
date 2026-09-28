---
id: BUG-1240
artifact: bug
status: approved
severity: minor
violates: REQ-1186
enters: implement
found: 2026-09-28
revised: 2026-09-28
issue: 612
---

# The shell every unit ships is outside the `format` and `lint` verbs

REQ-1186 asks for helpers to pass the same verbs as any other code the harness
ships, and the verbs reach only one of the two languages the helpers are
written in. Each unit's launcher, the hook script
`plugins/meow-method/hooks/notice` and `crates/meow/build-units` are POSIX
shell, and no verb formats or lints them. `test` reaches the launchers through
each unit's fixtures, and four units' fixtures never run the launcher with no
binary beside it.

## Reproduction

On `main` after #611, on macOS on arm64 with shellcheck 0.11.0 and
shfmt 3.14.1, on 2026-09-28. Each step starts from a clean checkout with
`crates/meow/build-units` run.

1. `grep -rn 'shellcheck\|shfmt' mise.toml .meowpaw tools .github` prints
   nothing, so no task a verb names runs a shell formatter or linter.
2. `shfmt -f plugins crates/meow` lists twelve files: ten launchers in
   `plugins/<unit>/bin/`, `plugins/meow-method/hooks/notice` and
   `crates/meow/build-units`. `shellcheck` over them exits 1 with SC1007
   twice in each launcher, on `system= cpu= exe=`, and `shfmt -i 2 -d` over
   them exits 1 with a diff in `crates/meow/build-units`. The verbs pass on
   the same tree.
3. In `plugins/meow-mise/bin/meow-mise`, replace
   `echo "meow-mise $1: unresolved: $reason"` and `exit 3` with
   `echo "meow-mise $1: 0 findings"` and `exit 0`. With no binary beside it,
   `sh plugins/meow-mise/bin/meow-mise check` prints
   `meow-mise check: 0 findings` and exits 0.
4. With that plant in place, `plugins/meow-verbs/bin/meow-verbs run lint test`
   prints `summary: lint passed, test passed`. A reviewer of EPC-1570 ran this
   step on a scratch clone. I ran the unit's 38 fixtures from `main` against
   a copy of the unit carrying the plant, and 37 passed. The one that failed,
   `test_this_repositorys_profile_is_clean`, found no profile because the
   copy sat outside the repository, and would fail the same way with no
   plant.

## What the system does

`format` runs Prettier's check and `crate-fmt`, and `lint` runs the Markdown,
prompt, kernel, standalone, budget, licence and mise checks and
`crate-lint`. None of them reads a shell file. The fixtures of `meow-git`,
`meow-github`, `meow-flow`, `meow-scm` and `meow-verbs` each run their
launcher with no binary and assert what it reports. The fixtures of
`meow-mise`, `meow-gotask`, `meow-licence` and `meow-author` don't, so step 4
passes: a launcher that reports a helper it couldn't run as a clean pass
fails no verb. SPC-1080 states that a launcher with no binary reports every
check as unrun and never as passed, and nothing checks that for those four.

## What it should do, and why

`format` and `lint` should fail on a badly formatted or linted shell file a
unit ships, as they fail on the crate, and `test` should fail when any
launcher's no-binary branch reports a pass. REQ-1186 asks for this. RES-0023
defines a helper as an executable a unit ships in `bin/`, and the launcher is
that executable, sitting on every helper's path. It also holds the fallback
that reports a missing helper, which RES-0023 makes part of the helper
contract.

## Triage

It enters at implement. REQ-1186 is in force and violated, and ADR-1610 already
chose how this repository binds a verb: a task in `mise.toml`, named by the
profile through `mise run`, so `meow-mise check` reads it. The fix follows
that pattern for a second language and needs no new decision. ADR-1610 and
EPC-1570 covered `crates/meow` alone and didn't list the shell under what
they left out, so REQ-1186 was recorded as closed by TSK-2510 while half of
the helper code stayed outside the verbs.

The same review found that ADR-1610's fourth criterion names kept evidence of
the failing `format` and `lint` runs, and `project/evidence/` holds none: the
failing runs appear only as transcripts in TSK-2510 and EPC-1570. It also
found that `tools/test_crate_verbs.py`, which plants a defect in a copy of
the crate, runs in no verb. TSK-2510 kept it out because clippy "takes
minutes", and on this machine the file runs in 3 seconds the first time in a
fresh worktree and 1 second after. Both belong to the same requirement's closing evidence, so the task
below closes them with this defect and doesn't open a second record.

Minor, because no shipped behaviour is wrong today: each launcher's fallback
reports correctly and the SC1007 findings are empty assignments written with
a style shellcheck warns about. The cost is a future regression that no verb
would catch.

## Closed by

TSK-2520. `tools/test_shell_verbs.py` checks that `format` and `lint` run the
shell tasks and that each task fails a planted defect, and a `Launcher`
fixture in each of the four units' tests runs the launcher with no binary and
asserts exit 3. They join the `test` verb as regression checks.

## Tasks

- [x] T-001 TSK-2520 bring the shipped shell under `format` and `lint`, in
      `mise.toml`, `.meowpaw/profile.toml` and each launcher, and test every
      launcher's no-binary branch
