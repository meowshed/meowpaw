---
id: TSK-2520
artifact: task
status: approved
revised: 2026-09-28
bug: BUG-1240
closes: [REQ-1186]
issue: 612
---

# Bring the shipped shell under `format` and `lint`, and test every launcher's fallback

`format` and `lint` check the shell every unit ships, as they check the crate,
and `test` fails when any launcher's no-binary branch reports a pass, so
REQ-1186 holds for all helper code. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given this change's tree, when `shfmt -f plugins crates/meow` runs, then
   it lists each file directly in a `plugins/<unit>/bin/`, each hook script
   starting with `#!` and `crates/meow/build-units`, at least twelve files.
   Closed by: `ShellFiles` in `tools/test_shell_verbs.py`.
2. Given `mise.toml`, when it is read, then it pins `shellcheck` and `shfmt`
   to exact versions, holds a `shell-fmt` task running `shfmt -i 2 -d` and a
   `shell-lint` task running `shellcheck` over that list, and `all` depends on
   both. Closed by: `ShellTasks` in `tools/test_shell_verbs.py`.
3. Given `mise.toml`, when `fmt` is read, then it also runs `shfmt -i 2 -w`
   over that list. Closed by: `ShellTasks.test_fmt_writes_the_shell`.
4. Given the profile, when `meow-verbs status` reads it, then `format` runs
   `mise run shell-fmt` and `lint` runs `mise run shell-lint`, each still
   ending with the crate's task. Closed by: `ShellBindings` in
   `tools/test_shell_verbs.py`.
5. Given a copy of a launcher with a badly indented block appended, when
   `shell-fmt`'s command runs over it, then it exits 1 naming the file, and
   it exits 0 on the copy as shipped. Closed by:
   `PlantedDefects.test_shell_fmt_fails_an_unformatted_launcher`.
6. Given a copy of a launcher with `planted= value` appended, when
   `shell-lint`'s command runs over it, then it exits non-zero naming SC1007,
   and it exits 0 on the copy as shipped. Closed by:
   `PlantedDefects.test_shell_lint_fails_a_space_after_equals`.
7. Given a tree with no shell file, when either task runs, then it exits
   non-zero, because a check over nothing is no pass. Closed by:
   `PlantedDefects.test_an_empty_tree_is_no_pass`.
8. Given the launcher of `meow-mise`, `meow-gotask`, `meow-licence` or
   `meow-author` copied alone into a directory, when each subcommand it
   accepts runs, then it exits 3 and prints `unresolved` or `unchecked`, the
   machine's name and the reinstall. Closed by: a `Launcher` fixture in each
   unit's tests, seen failing against a launcher whose fallback prints
   `0 findings` and exits 0.
9. Given a launcher planted as in criterion 5 and one planted as in criterion
   6, and separately the crate planted as TSK-2510 planted it, when
   `meow-verbs run format` and `meow-verbs run lint` run, then each exits 1,
   and its evidence is kept in `project/evidence/` before the plant is
   reverted. Closed by: the kept evidence files, which ADR-1610's fourth
   criterion names.
10. Given this change's tree, when `meow-verbs run format lint test` runs,
    then each passes, and the kept evidence cites REQ-1186. Closed by: the
    kept evidence of that run.

## What to do

Pin `shellcheck` and `shfmt` in `mise.toml` `[tools]`. Add `shell-fmt`, running
`files=$(shfmt -f plugins crates/meow) && test -n "$files" && shfmt -i 2 -d $files`,
and `shell-lint`, running the same list through `shellcheck`, and add both to
`all`. Append `shfmt -i 2 -w $(shfmt -f plugins crates/meow)` to `fmt`. In
`.meowpaw/profile.toml`, run `mise run shell-fmt` before `mise run crate-fmt`
in `format` and `mise run shell-lint` before `mise run crate-lint` in `lint`,
so the crate's task stays last, as `tools/test_verb_bindings.py` holds. Add
`tools/test_shell_verbs.py` and `tools/test_crate_verbs.py` to the `test`
verb's `unittest` line.

The list comes from `shfmt -f`, which picks a file by its shebang, so a
launcher added later is checked with no edit to the task. The indent, two
spaces, goes on the command line, because the files already use it and a
command line puts the whole policy in the one task that runs it, as ADR-1610
argued for `-D warnings`. Shellcheck runs with its default severity.

Fix what the tools report: write `system='' cpu='' exe=''` in each launcher,
which shellcheck accepts and which assigns the same empty strings, and let
`shfmt -w` split the two one-line `case` items in `crates/meow/build-units`.
Neither changes what a unit does, so no unit's version moves.

Write the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing. BUG-1240 and REQ-1186 are approved, and EPC-1570's tasks, which
added the crate's tasks this one sits beside, are closed.

## Evidence

Not yet.

## Left alone

Linting or type-checking each feature alone, which ADR-1610 accepts with a
reversal condition. The Windows branch of `signal_code` in
`crates/meow/src/verbs.rs`, which no local verb compiles: CI's build workflow
compiles it for both Windows targets on every pull request that touches the
crate, so a type error there fails a pull request, and a clippy finding there
doesn't. EPC-1570 and TSK-2510, which are approved and frozen: BUG-1240
records what they missed.
