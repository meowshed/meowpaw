---
id: TSK-4700
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2440
closes: [REQ-2734]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Report a constitution over its target length from `paw check`

`paw check` counts the lines of `CLAUDE.md` at the repository's root and, over
200, prints an advice line after the checks' findings that changes no count
and no exit status, as SPC-1220 states under "Its length". One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture repository whose `CLAUDE.md` has 449 lines and a clean
   record, when `paw check` runs, then it prints
   `CLAUDE.md: over its target of 200 lines at 449; cut it` and exits 0
   (REQ-2734). Closed by: a crate test naming REQ-2734, seen failing first.
2. Given the same fixture with a record finding, when `paw check` runs, then
   it exits 1 and every check's count of findings is the same as without the
   advice. Closed by: a crate test.
3. Given a fixture with a 200-line `CLAUDE.md`, or none, when `paw check`
   runs, then it prints nothing about the constitution. Closed by: a crate
   test.

## What to do

Add the count to the `record` feature of `crates/meow/`, reading `CLAUDE.md`
at the repository's root and never under the record's root. Pin the line in
`paw check`'s output test. Document it on `plugins/meow-flow/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Cutting this repository's `CLAUDE.md`, which TSK-4730 does, so the advice
line appears in this repository's gate until that task lands.
