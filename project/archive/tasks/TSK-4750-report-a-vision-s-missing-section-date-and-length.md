---
id: TSK-4750
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2450
closes: [REQ-0611, REQ-0614, REQ-0616, REQ-0618, REQ-0620, REQ-2856, REQ-2857]
issue: 959
projected: ba16745024b9
tracked: fed934b552d5
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Report a vision's missing section, date, restated requirement and length from `paw check`

`paw check`'s `shape` check reports a vision missing one of its four required
sections, and its `rules` check reports a date in the body, a requirement
stated as an obligation and a body over 2,000 words, as SPC-1230 states. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture vision with no What it will not do section, when
   `paw check` runs, then `shape` reports it, naming the section, and the same
   for Who it is for, Quality goals and Risks (REQ-0616, REQ-0618, REQ-0620).
   Closed by: a crate test naming REQ-0620, seen failing first.
2. Given a fixture vision whose body holds `2027-01-01`, `March 2027` or
   `Q3 2027`, when `paw check` runs, then `rules` reports each, naming the
   line, and the front matter's `revised` passes (REQ-2856). Closed by: a
   crate test naming REQ-2856.
3. Given a fixture vision with the sentence
   `The harness MUST log every run (REQ-0010).`, when `paw check` runs,
   then `rules` reports it (REQ-2857).
   Closed by: a crate test naming REQ-2857.
4. Given a fixture vision whose body has 2,001 words outside fenced code, when
   `paw check` runs, then `rules` reports it with the count, and at 2,000 it
   doesn't (REQ-0611). Closed by: a crate test naming REQ-0611.
5. Given a fixture record with a second vision file under any directory, when
   `paw check` runs, then `identifiers` reports `vision` as used twice, naming
   both files (REQ-0614). Closed by: a crate test naming REQ-0614.
6. Given this repository, when `paw check` runs, then it reports 0 findings.
   Closed by: its output in the pull request.

## What to do

Add the sections to the vision kind in `plugins/meow-flow/lib/layout.toml` and
the three rules to the `record` feature of `crates/meow/`. Confirm
`plugins/meow-flow/templates/vision.md` carries each required section, as it
does today, and keep it in step with the layout. Document the rules on
`plugins/meow-flow/README.md`.

## Depends on

- TSK-4740 (blocking): today's vision lacks the Quality goals and Risks sections, so this check fails the gate until the rewrite lands.

## Evidence

Criteria 1 to 5 are closed by the tests in
`crates/meow/tests/record_living.rs`, each seen failing first:
`a_vision_missing_a_section_is_reported_naming_it` (criterion 1, REQ-0616,
REQ-0618, REQ-0620), `a_vision_carrying_a_date_is_reported_with_its_line`
(criterion 2, REQ-2856), `a_vision_stating_a_requirement_is_reported`
(criterion 3, REQ-2857),
`a_vision_over_two_thousand_words_is_reported_with_its_count` (criterion 4,
REQ-0611) and `a_second_vision_is_reported_naming_both_files` (criterion 5,
REQ-0614). Criterion 6: `paw check` reports 0 findings in each of its seven
checks for this repository.

Every stage passed in pull request #1078.

## Left alone

Whether a claim is falsifiable, which is a judgement TSK-4760 gives the design
step.
