---
id: TSK-2420
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1550
closes:
  [
    REQ-2460,
    REQ-2462,
    REQ-2464,
    REQ-2465,
    REQ-2466,
    REQ-2467,
    REQ-2470,
    REQ-2472,
    REQ-2473,
    REQ-2476,
    REQ-2478,
    REQ-2479,
    REQ-2496,
    REQ-2500,
  ]
issue:
---

# Ship the mise pack with `status`'s task listing

`meow-mise status` detects mise, reports its version and trust state, and
lists the tasks it resolves with each one's origin and blocks, as SPC-1140
states. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a work tree with no detection marker, when `status` runs, then it
   reports `not a mise repository`, exits 3 and runs no mise command. Closed
   by: a fixture naming REQ-2472.
2. Given a repository with a committed task, a hidden one, a confirm one as
   a TOML key and as a file task header, one taking a required argument, one
   with `sources` and `outputs`, a parent directory's task and a
   `mise.local.toml` replacing a committed task, when `status` runs, then each
   carries its origin and blocks under `resolved in this work tree`. Closed
   by: fixtures naming REQ-2460, REQ-2464, REQ-2465, REQ-2470, REQ-2476,
   REQ-2478, REQ-2479 and REQ-2500, seen failing first.
3. Given an untrusted configuration holding an `exec` template, when `status`
   runs, then it reports `untrusted` with exit 3 and `mise trust --show` still
   reports it untrusted; given a trusted one, the `exec` file is named.
   Closed by: fixtures naming REQ-2466, REQ-2467 and REQ-2473.
4. Given a stand-in mise printing an unrecognised listing, or failing with
   `unexpected argument`, when `status` runs, then each is unresolved with
   exit 3, and the version is reported. Closed by: fixtures naming REQ-2462
   and REQ-2496.

## What to do

Add a `mise` feature and module to `crates/meow`, the unit under
`plugins/meow-mise` with its launcher, skill, README, budget, requirement
file and marketplace entry, and add it to `build-units` and the `test` verb.

## Depends on

Nothing. ADR-1580 is approved.

## Evidence

Not yet.

## Left alone

`bind`, `check` and what mise carries beyond tasks, which TSK-2430 and
TSK-2440 take; the ten requirements ADR-1580 postpones.
