---
id: TSK-5005
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2545
closes: [REQ-2254]
issue:
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

Not yet.

## Left alone

Whether the section that frames a concern says anything true about it, which
review holds.
