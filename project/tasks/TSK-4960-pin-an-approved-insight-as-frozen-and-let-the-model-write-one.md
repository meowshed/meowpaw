---
id: TSK-4960
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2610
closes: [REQ-2142, REQ-2662]
issue: 905
projected: 99b20ef42752
tracked: 1d1d8d580071
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin an approved insight as frozen, and let the model write one unprompted

A crate test pins what `check_frozen` already does for an insight, and the
method skill's rule M11 says the model may write an insight draft with no
person's prompt, as SPC-1070 states under "The frozen check" and SPC-1090
under "Insights". It realises ADR-2610. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

Taken from ADR-2610's list of how it will be known realised:

1. Given a fixture repository with an approved insight at the base revision
   and a changed line in its body, when `paw check frozen --base <rev>` runs,
   then it reports the insight as changed after approval and exits 1
   (REQ-2662). Closed by: a crate test naming REQ-2662. The behaviour already
   holds, so the test is seen failing first against a fixture that removes
   the insight from the frozen kinds.
2. Given `plugins/meow-flow/skills/method/SKILL.md`, when a test reads rule
   M11, then it says the model writes an insight as a draft when the work
   taught something that holds past its case, with no person's prompt
   (REQ-2142). Closed by: a test under `plugins/meow-flow/tests/` naming
   REQ-2142, seen failing first, because M11 today says when to write one and
   not that no prompt is needed.

## What to do

Add the test to the `record` feature of `crates/meow/`, and change M11's
wording, held to SPC-1030 and the unit's `budget.toml`.

## Depends on

Nothing.

## Evidence

Both criteria are closed by tests seen failing first.

1. `an_approved_insight_changed_since_the_base_is_reported` in
   `crates/meow/tests/record_kinds.rs` (REQ-2662). The behaviour already
   held; the same test runs the fixture against a layout without the insight
   kind and expects exit 0, which is the failure the criterion asks to see.
2. `test_the_model_writes_an_insight_as_a_draft_with_no_prompt` in
   `plugins/meow-flow/tests/test_method_skill.py` (REQ-2142), failing before
   M11 was reworded, and M11 is changed identically in
   `packages/meow-flow/skills/method/SKILL.md`.

Every stage passed in pull request #PR.

## Left alone

REQ-2666, which asks an insight to carry its date and which ADR-2610 leaves
to a later decision, because CLAUDE.md says no field records when work
happened.
