---
id: TSK-4770
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2460
closes: [REQ-0610, REQ-0612, REQ-0628, REQ-0632]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a live record, a specification that carries history, and a withdrawal that names nothing

`paw check` fails a record of a kind other than the vision and the
specification that declares `status: live`, a specification carrying struck
text, a tombstone heading or a phrase naming an earlier version, and a
withdrawn record whose first line names no identifier, as SPC-1070 states
under "The layout". One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture requirement with `status: live`, when `paw check` runs,
   then it fails naming the file, and an index file in a kind's directory with
   `status: live` passes (REQ-0610). Closed by: a crate test naming REQ-0610,
   seen failing first.
2. Given a fixture specification with a `~~struck~~` line, one with a heading
   `## Withdrawn requirements`, and one with the sentence "This previously
   read the profile twice", when `paw check` runs, then it fails each, naming
   the line (REQ-0612, REQ-0632). Closed by: a crate test naming REQ-0632.
3. Given a fixture withdrawn requirement whose first line under its title is
   "No longer needed.", when `paw check` runs, then it fails naming the file,
   and one whose first line is `**Withdrawn by ADR-1800. Replaced by
REQ-3320.**` passes (REQ-0628). Closed by: a crate test naming REQ-0628.
4. Given this repository's record, when `paw check` runs, then it reports 0
   findings, a prediction I record before the work: every one of the 68
   withdrawn requirements opens with an identifier today. Closed by: its
   output in the pull request.

## What to do

Add the three rules to the layout in `plugins/meow-flow/lib/layout.toml`, the
phrase list included, and to the `record` feature of `crates/meow/`. Start the
phrase list with "previously", "no longer", "used to", "an earlier version"
and "was replaced", and keep it in the layout so a new phrase is one line.
Where the specifications here trip a phrase in ordinary present-tense use,
reword the specification or narrow the phrase, and say which in the pull
request. Document the rules on `plugins/meow-flow/README.md`.

A living document cites no withdrawn requirement, as SPC-1070 states, so the
rule finds no Withdrawn section to keep; no specification carries one today.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The constitution, which isn't under the record's root, and the per-task
status in an epic, which TSK-4780 handles.
