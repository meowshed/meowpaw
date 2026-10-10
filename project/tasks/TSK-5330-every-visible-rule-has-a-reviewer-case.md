---
id: TSK-5330
artifact: task
status: done
revised: 2026-10-10
bug: BUG-1100
closes: [REQ-4800, REQ-4802, REQ-4804]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Give every visible rule of the writing standard a reviewer case and fail the gate on a gap

The reviewer's labelled set gets a case for each of the 60 rules a text can
show, a list names the 5 rules no text can show, and a test fails with each rule
that has neither. Running the cases is an evaluation and stays out of this task.

## Acceptance criteria

1. Given the writing standard's 65 rules, when the unit's tests run, then each
   rule has a case tagged `rule-<ID>` or an entry in
   `plugins/meow-prose/evals/rule-cases.toml`, and the test names every rule
   that has neither. Closed by: `test_every_rule_has_a_case_or_an_entry` in
   `plugins/meow-prose/tests/test_rule_cases.py`.
2. Given a rule identifier added to the standard with no case, when the test
   runs, then it fails and names the identifier. Closed by:
   `test_a_rule_with_no_case_is_named` in the same file.
3. Given an entry in the list for a rule that has a case or doesn't exist, when
   the test runs, then it fails, because a stale entry hides a gap. Closed by:
   `test_an_entry_names_a_rule_with_no_case` in the same file.
4. Given each case tagged `rule-<ID>`, when its prompt is read, then it names
   the text to review and its grader names the rule in the form the other
   graders use. Closed by: `test_a_rule_case_is_shaped_like_the_others`.

## What to do

Write the test first, in a commit of its own where it fails on the 56 rules
that have no case, then the 56 cases and the list. Each case is a directory
under `plugins/meow-prose/evals/` named `rule-<id>-<slug>` with a `prompt.md`
and a grader `names-the-defect.md`, as `hype-words` is. Tag the four earlier
cases that name a rule, so the test reads them. Keep the rule read to the
`- X0.` form the standard uses, and read both files the standard keeps its
rules in.

## Depends on

Nothing.

## Evidence

1. `python3 -m unittest plugins/meow-prose/tests/test_rule_cases.py` ran five
   tests and exited 0. The test failed on all 56 rules in the commit that added
   it and passes with the 56 cases tagged `rule-<ID>` and the five entries in
   `plugins/meow-prose/evals/rule-cases.toml`: criteria 1 to 4.
2. The `format`, `lint`, `check` and `test` stages passed, and `paw check` and
   `paw check frozen --base origin/main` reported no findings.

## Left alone

The reviewer's measured rate on the new cases, which is an evaluation the owner
postponed, and the 21 pattern pairs, which test patterns and stay untagged.
