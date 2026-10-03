---
id: TSK-4975
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2535
closes: [REQ-0667]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Report a conflict across a declared kind's order

`paw check` reads a declared kind's optional `outranks` list and reports two
artifacts of ranked kinds that cite each other and disagree on a front matter
field, naming both and the order, without choosing, as SPC-1070 states under
"Kinds a repository declares". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture kind `narrative` that outranks `research`, a `NAR-0001` and a `RES-0001` citing each other and stating different values for one front matter field, when `paw check` runs, then it reports the conflict naming both files and the order, and changes neither (REQ-0667). Closed by: a crate test naming REQ-0667, seen failing first.
2. Given the same pair agreeing on every field, when `paw check` runs, then it reports no conflict. Closed by: a crate test.
3. Given an `outranks` entry naming no kind, when `paw check` runs, then it reports the unknown kind. Closed by: a crate test.

## What to do

Add the comparison to the `record` feature of `crates/meow/` as part of an
existing check or a named one, and document it on
`plugins/meow-flow/README.md`. The report is a finding and never a fix.

## Depends on

- TSK-4970 (blocking): the declarations it reads `outranks` from.

## Evidence

Not yet.

## Left alone

How a conflict is settled, which the person decides, because ADR-2600 asks
for the conflict to be reported and not resolved.
