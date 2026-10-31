---
id: BUG-1730
artifact: bug
status: approved
severity: minor
violates: REQ-3080
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue: 1145
projected: 559b6bf4a636
tracked: 0c0faf933817
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The doctor test reads an error as the output of `paw status`

`doctor_and_paw_status_answer_different_questions` runs `paw status` with no
layout, so it checks an error message for forbidden words and holds nothing
about what `paw status` prints.

## Reproduction

macOS, Darwin, arm64, this repository at `6276d0c0`:

1. Check the repository out in a directory whose path contains `resolved`.
2. Run `cargo test --manifest-path crates/meow/Cargo.toml --all-features --test doctor`.

## What the system does

The test fails with `paw status names resolved`, quoting
`paw status: the record was not checked: <checkout>/crates/meow/lib/layout.toml:
No such file or directory`. The word came from the checkout's own path. In any
other checkout the same error contains no forbidden word, and the test passes
with no status read.

## What it should do, and why

REQ-3080 says `doctor` and `paw status` answer different questions, and the test
is what holds that for `paw status`. The test should run `paw status` against
the layout the unit ships and fail where the record wasn't checked, because a
check that passes on an error can't fail for the reason it exists.

## Triage

Enters at implement, because REQ-3080 states the behaviour and only the test
fails to hold it. Minor, because `paw status` itself breaks nothing, and the gate
fails only in a checkout with an unlucky path.

## Closed by

`crates/meow/tests/doctor.rs::doctor_and_paw_status_answer_different_questions`
now passes `MEOW_LAYOUT` and asserts the record was checked, so the test fails
on an error and reads real status output in every checkout.

## Plan

1. Pass the shipped layout to `paw` in `crates/meow/tests/doctor.rs`, and assert
   the status output isn't the not-checked error.
