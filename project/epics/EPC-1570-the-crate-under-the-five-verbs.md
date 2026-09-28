---
id: EPC-1570
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1610
checked-at:
---

# This repository binds its five verbs to the crate's own tools, after the crate passes them

Realises exactly one authorising record, ADR-1610. The epic is complete when
`meow-verbs run format lint check test build` in this repository runs the
crate's formatter, linter, type check, tests and build, each passing, and the
gate runs the same tasks.

## Acceptance criteria

Taken from ADR-1610, from its list of how I will know it was realised, before
the tasks below were written:

1. `cargo fmt --manifest-path crates/meow/Cargo.toml --check` and the clippy
   command in `crate-lint` each exit 0 on `main`.
2. `plugins/meow-verbs/bin/meow-verbs run format lint check test build`
   records five results, each with a non-empty command, and `check` and
   `build` no longer read as unresolved.
3. `plugins/meow-mise/bin/meow-mise check` reports 0 findings over the task
   runs the profile names, which include `crate-fmt`, `crate-lint`,
   `crate-check`, `crate` and `build`.
4. A line in `crates/meow/src` left unformatted on purpose makes
   `meow-verbs run format` exit 1, and a planted clippy finding, such as a
   collapsible `if`, makes `meow-verbs run lint` exit 1. Each is seen once
   and then reverted, and the kept evidence of those runs and of the passing
   run closes REQ-1186.
5. The CI run of the fourth task's change passes `mise run all` with the
   three new tasks in it.
6. REQ-1186, the one requirement ADR-1610 addresses, lands in exactly one
   closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 [P] TSK-2480 add `crate-check`, and bind `check`, `test` and
      `build` in `.meowpaw/profile.toml` and `mise.toml`

- [x] T-002 [P] TSK-2490 reformat `crates/meow/src` with `cargo fmt` and
      nothing else

- [x] T-003 TSK-2500 fix the 15 clippy findings in `crates/meow/src`
      depends: TSK-2490, because the reformat rewrites the lines the fixes
      touch, so the fixes written first would conflict with it

- [x] T-004 TSK-2510 add `crate-fmt` and `crate-lint`, run `cargo fmt` from
      `fmt`, and bind `format` and `lint`
      closes: REQ-1186
      depends: TSK-2480, TSK-2490 and TSK-2500, because the profile lines it
      edits come from TSK-2480, and a verb bound before the crate passes
      fails every pull request

## Coverage

ADR-1610 addresses one requirement, REQ-1186, and it lands in TSK-2510 alone,
because only that task's change leaves every verb reaching the crate. The
other three tasks close nothing and each leaves the gate green, which is
ADR-1610's reason for four changes. TSK-2510 by itself is the smallest set
that tests the decision, since its evidence runs all five verbs over the
crate.

## Not covered

- REQ-1188, which asks for helpers in the one language the plugin platform
  installs dependencies for, and which ADR-1610 neither withdraws nor
  applies.
- Linting or type-checking each feature alone, which ADR-1610 leaves until a
  warning reaches a shipped binary that the run with every feature missed.
- A supply-chain check of the crate's dependencies, and lint policy beyond
  clippy's default set, which ADR-1610 leaves open.
- How another repository binds its verbs for Rust, which a Rust pack decides
  for REQ-2332.
