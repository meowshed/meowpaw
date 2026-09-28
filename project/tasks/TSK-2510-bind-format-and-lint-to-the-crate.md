---
id: TSK-2510
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1570
closes: [REQ-1186]
issue: 605
projected: c285b90a2fb3
---

# Bind `format` and `lint` to the crate

This repository's `format` and `lint` verbs reach `crates/meow`, so all five
verbs check the crate and the evidence they keep closes REQ-1186, as
ADR-1610's fourth change decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given this change's tree, when `plugins/meow-verbs/bin/meow-verbs run
format lint check test build` runs, then it records five results, each
   with a non-empty command and a pass, `format` ending with `mise run
crate-fmt` and `lint` ending with `mise run crate-lint`. Closed by: the kept
   evidence of that run, citing REQ-1186.
2. Given this change's tree, when `plugins/meow-mise/bin/meow-mise check`
   runs, then it reports 0 findings over task runs that include
   `crate-fmt`, `crate-lint`, `crate-check`, `crate` and `build`. Closed by:
   its output in the pull request.
3. Given a line in `crates/meow/src` left unformatted on purpose, when
   `meow-verbs run format` runs, then it exits 1. Closed by: the kept
   evidence of that failing run, seen once and then reverted.
4. Given a collapsible `if` planted in `crates/meow/src`, when `meow-verbs
run lint` runs, then it exits 1 naming `collapsible_if`. Closed by: the
   kept evidence of that failing run, seen once and then reverted.
5. Given a line in `crates/meow/src` left unformatted on purpose, when `mise
run fmt` runs, then the line takes the formatter's form and `mise run
fmt-check` then exits 0. Closed by: the commands' output in the pull
   request.
6. Given this change, when CI runs it, then `mise run all` passes with
   `crate-fmt`, `crate-lint` and `crate-check` in it, and the pull request
   doesn't merge before that. Closed by: the pull request's CI run.
7. Given this change's tree, when `mise run crate-lint` runs on a clean
   target directory, then its wall time is recorded. Closed by: the timed
   run in the pull request, which ADR-1610 asks for because RES-0278 had only
   a lower bound.

## What to do

Add two tasks to `mise.toml`, and add both to the `depends` of `all`:

- `crate-fmt` runs `cargo fmt --manifest-path crates/meow/Cargo.toml
--check`.
- `crate-lint` runs `cargo clippy --quiet --manifest-path
crates/meow/Cargo.toml --all-features --all-targets -- -D warnings`.

Make the `fmt` task also run `cargo fmt --manifest-path
crates/meow/Cargo.toml`. In `.meowpaw/profile.toml`, append `&& mise run
crate-fmt` to `format` and `&& mise run crate-lint` to `lint`. Keep `-D
warnings` on the command line and add no `[lints]` table to the manifest,
because ADR-1610 keeps a warning from stopping `cargo build`.

If CI's toolchain lacks `rustfmt` or `clippy`, declare both components for
the pinned toolchain in `mise.toml` in this change, because RES-0278 couldn't
see the runner's components.

No unit's shipped behaviour changes, so no unit's version moves.

## Depends on

TSK-2480, because this task edits the profile and `mise.toml` lines that task
writes. TSK-2490 and TSK-2500, because a verb bound to the formatter or to
clippy before the crate passes them fails every pull request.

## Evidence

`mise.toml` gains `crate-fmt` and `crate-lint`, running the two commands
this task states, and `all` depends on both beside `crate-check`. The `fmt`
task runs `cargo fmt --manifest-path crates/meow/Cargo.toml` after Prettier.
`.meowpaw/profile.toml` appends `&& mise run crate-fmt` to `format` and `&&
mise run crate-lint` to `lint`. The manifest gains no `[lints]` table. `mise.toml` declares the `rustfmt` and
`clippy` components for the pinned toolchain, because CI's first run on this
branch failed in `crate-fmt` with `'cargo-fmt' is not installed for the
toolchain '1.98.1-x86_64-unknown-linux-gnu'`. SPC-1080
now says that `all` depends on every crate task apart from `build`, which CI
builds in its own workflow, where it said `all` depends on all five.

The ten checks failed at the cover commit, the branch's first commit, which
held the checks alone, and pass after this change. A diff of both check files
against that commit prints nothing.

```text
$ python3 -m unittest tools/test_verb_bindings.py tools/test_crate_verbs.py
Ran 18 tests
FAILED (failures=12)                             # cover commit, exit 1
Ran 18 tests
OK                                               # this change, exit 0
$ plugins/meow-mise/bin/meow-mise check
0 findings in 12 task runs the profile's verbs name   # exit 0
```

Criteria 3 and 4 ran once against the working tree, each with its defect
planted at the end of `crates/meow/src/main.rs` and reverted after:

```text
$ plugins/meow-verbs/bin/meow-verbs run format   # unformatted line planted
[crate-fmt] $ cargo fmt --manifest-path crates/meow/Cargo.toml --check
Diff in .../crates/meow/src/main.rs:108:
-fn   planted_by_tsk_2510 ( )->u8{ 1 }
+fn planted_by_tsk_2510() -> u8 {
summary: format failed                           # exit 1
$ plugins/meow-verbs/bin/meow-verbs run lint     # collapsible if planted
    = help: ... index.html#collapsible_if
[crate-lint] ERROR task failed
summary: lint failed                             # exit 1
```

Criterion 5 ran with the unformatted line planted: `mise run fmt` exited 0
and rewrote the line as `fn planted_by_tsk_2510() -> u8 {`, then `mise run
crate-fmt` and `mise run fmt-check` each exited 0. Criterion 7: `mise run
crate-lint` with `CARGO_TARGET_DIR` set to an empty directory took 2.67 s
wall time, 8.00 s user and 1.14 s system, and exited 0, on an Apple silicon
laptop with the 40 packages in `crates/meow/Cargo.lock`.

The kept evidence of `meow-verbs run format lint check test build`, all five
passing with non-empty commands, sits in
`project/evidence/`, committed with this change. Criterion 6 is the pull
request's CI run.

### Checks written before the change

Each criterion a program can check has a check in
`tools/test_verb_bindings.py` or `tools/test_crate_verbs.py`, and each check
failed on the parent revision, `main` after #609, because `mise.toml` has no
`crate-fmt` or `crate-lint` task and the profile binds neither.
`python3 -m unittest tools/test_verb_bindings.py tools/test_crate_verbs.py`
exited 1 and printed `Ran 18 tests` and `FAILED (failures=12)`: the 8 checks
TSK-2480 wrote passed, and the 10 below failed, two of them in two subtests.

- Criterion 1: `FormatAndLintTasks.test_crate_fmt_runs_the_formatter_check`,
  `FormatAndLintTasks.test_crate_lint_runs_clippy_denying_warnings`,
  `FormatAndLintBindings.test_format_ends_with_crate_fmt` and
  `FormatAndLintBindings.test_lint_ends_with_crate_lint`.
- Criterion 2:
  `MiseCheckWithFormatAndLint.test_meow_mise_check_passes_over_all_five_crate_tasks`.
- Criterion 3:
  `FormatCatchesAnUnformattedLine.test_crate_fmt_passes_the_clean_copy_and_fails_the_planted_one`.
- Criterion 4: `LintCatchesACollapsibleIf.test_crate_lint_fails_naming_collapsible_if`.
- Criterion 5: `FmtFormatsTheCrate.test_fmt_runs_cargo_fmt_without_check` and
  `FmtFormatsThePlantedLine.test_fmt_step_formats_the_line_and_crate_fmt_then_passes`.
- Criterion 6: `GateWithFormatAndLint.test_all_depends_on_the_three_crate_tasks`.

The checks for criteria 3, 4 and 5 plant their defect in a copy of
`crates/meow` and run the task's own command from `mise.toml` against the
copy's manifest, because planting it in the working tree would leave the tree
dirty if a run stopped halfway. Clippy's run takes minutes, so
`tools/test_crate_verbs.py` stays out of the `test` verb, like
`tools/test_crate_lint.py`.

Criterion 1 is partly judgement: a check can't run all five verbs, because
`test` runs `tools/test_verb_bindings.py` and would run the check again. The
checks hold the bindings, and the kept evidence of the five-verb run holds the
passes.

Criteria 3 and 4 are partly judgement for the same reason. The checks hold
that the task each verb ends with fails on the planted defect, and the kept
evidence of `meow-verbs run format` and `meow-verbs run lint` holds the exit
status of 1.

Criterion 5 names `mise run fmt-check`, which checks Markdown alone and so
passes whatever the crate holds. The check reads the criterion as the crate's
own check, `crate-fmt`, passing after `fmt` ran.

Criterion 6 is judgement: the pull request's CI run is the check, and no
program in the tree can see it.

Criterion 7 is judgement: it records a wall time and states no limit, so
nothing can pass or fail.

## Left alone

SPC-1080, which already states the five bindings. Each feature linted alone,
a supply-chain check and lint policy beyond clippy's default set, which
ADR-1610 leaves open.
