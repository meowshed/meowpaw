---
id: TSK-2110
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1380
closes: [REQ-1022, REQ-3058, REQ-3062, REQ-3064]
issue: 444
projected: e970c9c5561b
---

# `meow-licence check` fails on a file nothing covers, and this repository covers every file

A new unit, `meow-licence`, ships a `check` in the native tool that reads a
repository's licensing declarations and reports each file nothing covers,
each declaration missing half of its statement and each licence text out of
step with what is used, and this repository passes it. One task, one branch,
one pull request, one review.

## Acceptance criteria

1. Given this repository, when `plugins/meow-licence/bin/meow-licence check`
   runs, then it exits 0. Closed by: its output, and the `lint` verb running
   it.
2. Given a fixture repository with a tracked file nothing covers, a header
   carrying a copyright and no identifier, an unused text in `LICENSES/`, and
   one declaring nothing, when the check runs on each, then it exits 1, 1, 1
   and 3 and names the file and the failure as SPC-1120 words it. Closed by:
   fixtures naming REQ-3058, REQ-1022 and REQ-3062, seen failing first.
3. Given the check's output on any repository, when it is read, then it states
   licensing alone and names no author and no build. Closed by: a fixture
   naming REQ-3064.

## What to do

Create `plugins/meow-licence/` with a manifest, a page, a budget, a
`requires.toml` and a launcher like the other units', and add a `licence`
subcommand to the native tool behind its own feature, built by
`crates/meow/build-units`. Implement the check as SPC-1120 states it, reading
`REUSE.toml`, the profile's `[licence]` table, headers in a file's first 20
lines and `.license` files beside a file. Add the unit to the catalogue.

In this repository, extend `REUSE.toml` to cover `crates/meow/Cargo.lock`, and
run the check from the `lint` verb.

## Depends on

Nothing. ADR-1400 is approved.

## Evidence

`plugins/meow-licence/` holds the unit at 0.1.0: a manifest, a page, a budget
of nothing on every turn, a `requires.toml` and the launcher `bin/meow-licence`,
which runs the native tool's new `licence` subcommand, built behind its own
feature by `crates/meow/build-units`. The catalogue lists the unit, and
`claude plugin validate` passes on the catalogue and on the unit. SPC-1080
names the new subcommand.

Nine fixtures, eight naming their requirement, failed against a program that
prints nothing, apart from the one showing the report names no author, which
a silent program also meets; it fails only if the check starts echoing a
copyright holder. All nine pass against the check:

```text
$ MEOW_LICENCE_BIN=/usr/bin/true python3 -m unittest discover -s plugins/meow-licence/tests
FAILED (failures=8)
$ python3 -m unittest discover -s plugins/meow-licence/tests
Ran 9 tests
OK
$ plugins/meow-licence/bin/meow-licence check
1823 files, 0 licensing findings
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

On this repository the check first reported two files, not the one ADR-1400
names: `crates/meow/Cargo.lock` and `.meowpaw/profile.toml`. The lock file is
generated, so `REUSE.toml` covers it, and the profile carries a header. The
`lint` verb runs the check, and the `test` verb its fixtures.

Two cases the specification left open are settled in SPC-1120: `REUSE.toml`
and a `.license` file are declarations and need none, and a licence text is a
file named `LICENSE`, `LICENCE` or `COPYING` with no extension or a text
format's, so a source file named `licence.rs` still needs its header. A crate
test failed on the first version, which exempted that file.

## Left alone

The skill, which TSK-2120 adds.
