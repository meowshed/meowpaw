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
    then each passes. Closed by: the kept evidence of that run, which this
    task cites for REQ-1186.

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

Closes REQ-1186 for the shell. `mise.toml` pins `shellcheck` 0.11.0 and
`shfmt` 3.14.1 and adds `shell-fmt` and `shell-lint` with the commands this
task states, and `all` depends on both. `fmt` runs `shfmt -i 2 -w` after
`cargo fmt`. The profile runs `mise run shell-fmt` before `mise run
crate-fmt` and `mise run shell-lint` before `mise run crate-lint`, and the
`test` verb's `unittest` line gains `tools/test_shell_verbs.py` and
`tools/test_crate_verbs.py`. Each of the ten launchers now reads
`system='' cpu='' exe=''`, and `shfmt -w` split the two one-line `case`
items in `crates/meow/build-units`. SPC-1080 states the shell tasks and
their two failure paths.

### Checks written before the change

The checks went in first, in a commit of their own, on the branch after the
records. At that commit, `python3 -m unittest tools/test_shell_verbs.py`
exited 1 with `Ran 11 tests` and `FAILED (failures=14)`, and every check
failed, two of them in two subtests each: criteria 1 to 7, because no shell
task existed and the verbs bound none. The four `Launcher` fixtures for
criterion 8 pass against the launchers as shipped, because the launchers are
right, so I ran each against a copy of its launcher whose no-binary branch
prints `0 findings` and exits 0, through `MEOW_<UNIT>_BIN`:

```text
mise    exit 1  FAILED (failures=3)
gotask  exit 1  FAILED (failures=3)
licence exit 1  FAILED (failures=1)
author  exit 1  FAILED (failures=2)
```

After the change, `python3 -m unittest tools/test_shell_verbs.py
tools/test_verb_bindings.py tools/test_crate_verbs.py` exits 0 with
`Ran 29 tests`, `OK`, and each of the four units' fixtures passes under
`python3 -m unittest discover`. `mise run shell-fmt` and `mise run
shell-lint` each exit 0 on this tree. `tools/test_crate_verbs.py` takes
3 seconds on its first run in this worktree and 1 second after, which is why it now runs
in `test`.

### Planted defects, kept

Criterion 9 ran twice on the working tree, each plant reverted after its run.
A badly indented block and `planted= value` appended to
`plugins/meow-mise/bin/meow-mise` made `meow-verbs run format` exit 1 in
`shell-fmt` with shfmt's diff of that file, seen in
the run under #613, whose output is no longer kept, and `meow-verbs run lint` exit 1 in
`shell-lint` naming SC1007, seen in the run under #613, whose output is no longer kept. An
unformatted function and a nested `if` appended to `crates/meow/src/main.rs`
made `format` exit 1 in `crate-fmt`, seen in
the run under #613, whose output is no longer kept, and `lint` exit 1 in `crate-lint` on
`clippy::collapsible_if`, seen in the run under #613, whose output is no longer kept. The
last two are the failing runs ADR-1610's fourth criterion names, which
TSK-2510 recorded only as transcripts.

Criterion 10 is the kept evidence of `meow-verbs run format lint test` on this
change's tree, in `project/evidence/` and committed with it.

Criterion 1 reads the file list from the tree and not from shfmt, so a shell
file that `shfmt -f` missed fails it. Criterion 7 asserts exit 1 with nothing
printed, because a tool missing from the path exits 127 and says so, and a
check that accepted any non-zero exit would pass on that.

## Left alone

Linting or type-checking each feature alone, which ADR-1610 accepts with a
reversal condition. The Windows branch of `signal_code` in
`crates/meow/src/verbs.rs`, which no local verb compiles: CI's build workflow
compiles it for both Windows targets on every pull request that touches the
crate, so a type error there fails a pull request, and a clippy finding there
doesn't. EPC-1570 and TSK-2510, which are approved and frozen: BUG-1240
records what they missed.
