---
id: TSK-5075
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2332]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Rust pack

`meow-rust` is the language pack for Rust, detected from `Cargo.toml`, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Rust repository` and exits 3 (REQ-2332). Closed by: a
   crate test naming REQ-2332, seen failing first.
2. Given this repository, when `meow-rust bind` runs, then it prints a
   `[verbs]` table whose `format`, `lint`, `check`, `test` and `build`
   commands match the cargo commands the crate's gate runs through
   `mise.toml` (REQ-2332). Closed by: a crate test reading `mise.toml`.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Rust: documentation tests (REQ-2412), a pinned toolchain (REQ-2428), output kept outside the tree (REQ-2442), the generated files to commit and to ignore (REQ-2450) and a configured linter's rule groups (REQ-2432). Closed by: the crate tests naming
   each requirement.
4. Given `docs/README.md`, when the pack ships, then its row reads `shipped`.
   Closed by: `tools/check_docs.py`.

## What to do

Before implementing, check that the pack's own specification exists beside
SPC-1190, written through the spec step, with `paw ready implement` on this
task; where it doesn't, stop and report it, because this task decides
nothing the pack's document states: its bindings, its findings and its
settings table. Build the pack as a feature of `crates/meow/` on EPC-2565's
shared layer, with a program carrying `status`, `bind` and `check`, a skill
and a page, as SPC-1190's Boundary states. The pack binds each verb from the
tool the repository configured, and never from what is installed. Add a
fixture repository of the language to the crate's tests. The pack's README
states the toolchain versions it is current as of.

## Depends on

- TSK-5120 (blocking): the pack meets EPC-2565's rules on what it runs from
  its first release, so the shared layer comes first.
- TSK-5125 (blocking): the same, for what a pack reports it didn't check.
- TSK-5130 (blocking): the same, for what a pack never changes.
- TSK-5135 (blocking): the same, for what a pack keeps.
- TSK-5070 (not blocking): it adds the supported set's table, whose row this
  task moves to shipped; either can write the row.

## Evidence

Not yet.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
