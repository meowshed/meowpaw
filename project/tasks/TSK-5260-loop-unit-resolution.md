---
id: TSK-5260
artifact: task
status: done
revised: 2026-10-10
bug: BUG-1410
closes: [REQ-0894]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Let the loop's start command find its unit where the binary ships in another package

The loop's start command resolves the unit it passes to `--plugin-dir` from an
override, from the program's own unit, or from a sibling directory whose
manifest names `meow-loop`, so the command starts on the install layout
ADR-2810 ships, where the binary sits in the core package.

## Acceptance criteria

1. Given a program whose own unit's manifest names `meow-core` and a sibling
   directory `meow-loop` whose manifest names `meow-loop`, when the start
   command resolves its unit, then it returns that sibling. Closed by: a test
   in `crates/meow/src/runloop.rs`.
2. Given `MEOW_LOOP_UNIT` naming a directory whose manifest names `meow-loop`,
   when the start command resolves its unit, then it returns that directory
   before it looks at the program's own unit. Closed by: a test in
   `crates/meow/src/runloop.rs`.
3. Given `MEOW_LOOP_UNIT` naming a directory whose manifest names another
   unit, and no sibling that qualifies, when the start command resolves its
   unit, then it returns nothing and the command refuses with its existing
   message. Closed by: a test in `crates/meow/src/runloop.rs`.
4. Given the program sits at `<unit>/bin/<target>/meow` and the unit's own
   manifest names `meow-loop`, when the start command resolves its unit, then
   it returns that unit as it does today. Closed by: a test in
   `crates/meow/src/runloop.rs`.

## What to do

Resolve the unit in this order, and keep the check that a candidate's manifest
names `meow-loop`, because a call that names another directory loads no hook
(REQ-0894): the override `MEOW_LOOP_UNIT`, the program's own unit, then the
sibling `meow-loop` of the program's own unit. The in-session `guard`
subcommand stays as it is, because it never resolves a unit.

## Depends on

Nothing.

## Evidence

Pull request 873. The tests are in `crates/meow/src/runloop.rs`:

- Criterion 1:
  `the_unit_is_the_sibling_where_the_binary_ships_in_another_package`.
- Criterion 2: `the_override_is_taken_before_the_programs_own_unit`.
- Criterion 3: `a_directory_that_names_another_unit_is_refused`.
- Criterion 4:
  `the_programs_own_unit_is_returned_where_it_names_meow_loop`.

`meow-checks run format lint check test build` passed on every verb at one
tree, after a first run that failed `format` and `test` on rustfmt's diff of
the new tests, fixed in its own commit, and reported `lint` as `unchecked`
because the new worktree had no `meow-licence` binary until `build` made it.

## Left alone

The git guard's launcher lookup in `crates/meow/src/git.rs`, which finds
`meow-scm` and not the loop's unit, and SPC-1201, which covers the Claude Code
session and not Pi.
