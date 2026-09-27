---
id: TSK-2110
artifact: task
status: approved
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

Not yet.

## Left alone

The skill, which TSK-2120 adds.
