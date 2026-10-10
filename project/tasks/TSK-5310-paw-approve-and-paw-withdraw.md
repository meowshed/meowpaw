---
id: TSK-5310
artifact: task
status: done
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

Pull request 885. The tests are in `plugins/meow-flow/tests/test_record.py`,
class `WriteCommands`:

- Criterion 1: `test_approve_changes_the_status_line_and_nothing_else`.
- Criterion 2: `test_approve_refuses_a_draft_with_a_finding_and_changes_nothing`
  and `test_approve_refuses_a_record_that_is_not_a_draft`.
- Criterion 3: `test_withdraw_writes_the_tombstone_and_the_status` and
  `test_withdraw_refuses_a_replacement_that_does_not_exist`.

One fixture written first was wrong: a draft task has to meet the draft rules,
which ask for an Acceptance criteria section, and a commit of its own gives the
fixture one. `meow-checks run format lint check test` ran on the final tree.

## Left alone

The project index's prose and the research synthesis, which a person writes.
