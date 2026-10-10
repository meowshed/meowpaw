---
id: TSK-5310
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2800
closes: [REQ-4602]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `paw approve` and `paw withdraw`

`paw approve` moves a draft to approved where the check reports nothing about it, and
`paw withdraw` writes a requirement's tombstone and status.

## Acceptance criteria

1. Given a draft that `paw check` accepts, when `paw approve <id>` runs, then the
   file's `status` is `approved` and no other line changed. Closed by: a test in
   `plugins/meow-flow/tests/test_record.py`.
2. Given a draft with a finding, when `paw approve <id>` runs, then it exits 1,
   names the finding and changes nothing. Closed by: a test in the same file.
3. Given an approved requirement, when `paw withdraw REQ-1 --by ADR-2 --replaced-by
REQ-3` runs, then the file carries the tombstone line naming REQ-3, the
   status `withdrawn`, and `paw check` accepts it. Closed by: a test in the same
   file.

## What to do

Add the subcommands to the record module, edit the front matter as structured
data and never by text substitution, and regenerate the indexes.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The project index's prose and the research synthesis, which a person writes.
