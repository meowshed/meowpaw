---
id: TSK-2410
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1540
closes: [REQ-3192]
issue: 572
projected: cbe5fcd311d7
---

# The release refuses a breaking change without the version showing it

What ADR-1570 decides for this part. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a unit whose commits since its last tag include one marked
   breaking, when the release check runs, then it refuses a patch bump,
   accepts a minor bump at zero and a major bump above zero. Closed by: tests
   naming REQ-3192, seen failing first.
2. Given a breaking commit touching `crates/meow/`, when the check runs, then
   it holds every unit that ships the binary. Closed by: a test naming
   REQ-3192.

## What to do

Add the check as a script under `tools/` with its tests, run by the `test` verb, and call it from `.github/workflows/release.yml` before packing.

## Depends on

Nothing. ADR-1570 is approved.

## Evidence

Closes REQ-3192. `meow-verbs evidence --keep format lint test` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

`tools/check_release.py` is new, so no check existed to fail before it; its
six tests in `tools/test_check_release.py`, run by the `test` verb, cover
each criterion:

1. `test_a_breaking_change_with_a_patch_bump_is_refused`,
   `test_a_minor_bump_at_zero_shows_a_breaking_change` and
   `test_above_zero_only_a_major_bump_shows_it` (REQ-3192).
2. `test_a_breaking_change_to_the_native_tool_holds_every_unit_shipping_it`
   holds a unit that ships the binary and not one that doesn't (REQ-3192).

`test_a_unit_whose_name_holds_dash_v_reads_its_tags` holds a defect the first
run on this repository found: the tag parsing split on the `-v` inside
`meow-verbs`. Run on this repository, the check reports 0 units. The release
workflow runs it before packing, with the full history.

## Left alone

REQ-2532 and REQ-2544, which ADR-1570 postpones.
