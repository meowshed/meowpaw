---
id: EPC-1570
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1610
checked-at: "#596"
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

## Verified

I checked this under #596 on `main` after #610, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs run format lint check
test build` exits 0 and records five results, each passing with its command,
and `meow-verbs evidence --keep format lint test` keeps this change's own
results in `project/evidence/`, as the pull request cites. The crate's 29 tests
pass under `mise run crate`. Every criterion is met:

| Criterion                                                                    | Evidence on `main` after #610                                                                                                                                                                                                                               |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `cargo fmt --check` and the clippy command in `crate-lint` each exit 0    | `cargo fmt --manifest-path crates/meow/Cargo.toml --check` exits 0, and the `crate-lint` command, `cargo clippy --quiet ... --all-features --all-targets -- -D warnings`, exits 0 with no output                                                            |
| 2. Five results, each with a non-empty command, `check` and `build` resolved | The run prints `summary: format passed, lint passed, check passed, test passed, build passed`, with `check` running `mise run crate-check` and `build` running `mise run build`                                                                             |
| 3. `meow-mise check` reports 0 findings over the task runs the profile names | `plugins/meow-mise/bin/meow-mise check` prints `0 findings in 12 task runs the profile's verbs name` and exits 0, and the profile names `crate-fmt`, `crate-lint`, `crate-check`, `crate` and `build`                                                       |
| 4. A planted defect fails `format` and `lint`, then is reverted              | A badly spaced function appended to `crates/meow/src/main.rs` makes `meow-verbs run format` exit 1 with `Diff in ... main.rs:109`, and a nested `if` there makes `meow-verbs run lint` exit 1 on `clippy::collapsible_if`; `git status` shows both reverted |
| 5. The fourth task's CI run passes `mise run all` with the three new tasks   | CI run 36449273915 on #610 concludes `success`, and its log shows `crate-fmt`, `crate-lint` and `crate-check` each finishing                                                                                                                                |
| 6. REQ-1186 lands in exactly one closed task                                 | `paw show REQ-1186` derives it as closed by TSK-2510 alone, and TSK-2480, TSK-2490 and TSK-2500 close nothing                                                                                                                                               |

The first CI run on #610, 36448919479, failed `crate-fmt` with `'cargo-fmt' is
not installed for the toolchain '1.98.1-x86_64-unknown-linux-gnu'`, which is
the premortem ADR-1610 wrote. The change then declared `rustfmt` and `clippy`
as components of the pinned toolchain in `mise.toml`, as the decision said it
would, and the second run passed. So the gap the decision named as unobserved
is now observed and closed.

The planted defects in criterion 4 are also how I judged that the checks would
fail if REQ-1186 were violated. Nothing checks each feature alone, which
ADR-1610 accepts and SPC-1080 states.

### Documentation

SPC-1080's section on the checks the crate passes states each verb, its task
and the command it runs on the crate, and it matches `mise.toml` and
`.meowpaw/profile.toml`. No unit's shipped behaviour changed, so no unit page
or version moved. The `test` verb checked the pages.

### Postponements

ADR-1610 postpones no requirement, so none needs revisiting.

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
