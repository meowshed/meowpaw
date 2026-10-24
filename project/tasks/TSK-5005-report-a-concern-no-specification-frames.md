---
id: TSK-5005
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2545
closes: [REQ-2254]
issue: 981
projected: 6053e1bc2dd9
tracked: ff958da565d2
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Report a concern a decision names that no specification frames

`paw check` reads each decision's `concerns:` and reports one that no section
heading of a specification names, as SPC-1090 states under "The questions a
specification answers". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture decision with `concerns: [upgrade]` and no specification with a section heading naming `upgrade`, when `paw check` runs, then it reports a finding naming the decision and the concern and exits 1 (REQ-2254). Closed by: a crate test naming REQ-2254, seen failing first.
2. Given the same fixture with a specification holding `### Upgrade`, when `paw check` runs, then it reports nothing about the concern. Closed by: a crate test.
3. Given a withdrawn or superseded decision naming a concern framed nowhere, when `paw check` runs, then it reports nothing, because the decision is no longer in force. Closed by: a crate test.

## What to do

Add the rule to the `record` feature of `crates/meow/`, inside an existing
check or as a named one, matching the concern against heading words without
regard to case. Document it on `plugins/meow-flow/README.md` and in
SPC-1070's failure table, which already names the finding.

## Depends on

- TSK-5000 (blocking): the `concerns:` field in the layout.

## Evidence

Criterion 1 is closed by `a_concern_no_specification_heading_names_is_a_finding` in `crates/meow/tests/concerns.rs` (REQ-2254), seen failing first. Criterion 2 is closed by `a_concern_a_specification_heading_names_is_no_finding` and `a_heading_inside_a_fence_frames_nothing`. Criterion 3 is closed by `a_decision_no_longer_in_force_is_not_asked_to_frame_its_concern`. `a_decision_with_no_concern_is_asked_for_nothing` holds that a decision without a concern is asked for nothing.

The rule is the named check `concerns-framed` in the `rules` group, listed for the decision kind in `lib/layout.toml`. A `draft` or `done` decision is held to it as well as an `approved` one, which the task leaves open; `withdrawn`, `superseded` and `rejected` are not. SPC-1070's failure table already names the finding and needed no change.

Every stage passed in pull request #1078.

## Left alone

Whether the section that frames a concern says anything true about it, which
review holds.
