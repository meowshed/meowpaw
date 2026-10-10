---
id: ADR-2880
artifact: adr
status: done
revised: 2026-10-10
addresses: [REQ-4600, REQ-4602]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2880. The record keeps its files and gains commands for its writes

## Decision

The record stays one artifact for each file, as plain Markdown, and the tool
gains three commands that make the writes which cross files (REQ-4600):
`paw approve <id>...` moves a draft to `approved` where `paw check` reports
nothing about it, `paw done <task> --pr <number>` stores `done` in a complete
task, marks it in its epic or defect with the pull request, and stores `done`
in the epic and the decision when it was the last open task, and `paw withdraw
<requirement> --by <decision> --replaced-by <id>...` writes the tombstone and
the status. Each command changes the lines it owns and regenerates the indexes
(REQ-4602).

A hand edit stays valid. The commands are tested against `paw check`, and a
result that check rejects is a defect in the command.

Once this is accepted, nothing in the tree has changed. Once EPC-2800 lands, a
task is closed in one step. What still doesn't work: a pull request number the
person doesn't give, and prose such as the project index's narrative, which
stays a person's.

## Why

RES-0348 found that reading 2,060 files takes 2.4 seconds and that 256 of 506
commits since 2026-09-20 touch three or more record files, with 14 corrections
for a status, mark or index left out. A database would remove that by giving up
the per-file diff that `paw check frozen` and review read, and the rule that the
record is usable without the tool (REQ-0030).

## Alternatives

| Option                      | Better at                | Why it lost                                                        |
| --------------------------- | ------------------------ | ------------------------------------------------------------------ |
| Do nothing                  | No work                  | The writes stay by hand, with 14 corrections in three weeks        |
| One flat database in a file | One atomic write         | One diff for every change, and a conflict on every parallel branch |
| SQLite                      | Queries and transactions | A binary git can't diff, and a tool needed to read the record      |

## What it costs

Three commands to keep in step with the templates and the check, and a second
way to write a record. A command that drifts from the check fails the gate
through its own tests, and the hand edit remains.

## What would reverse it

- A measured read cost, such as a full check over a minute, or conflicts in the
  index pages on most parallel branches. While reads take seconds and the
  indexes are generated, the files stay.

## Consequences

EPC-2800 carries two tasks, `approve` with `withdraw`, and `done`. The method
unit's steps say to use the commands once they exist.

## How I will know it was realised

1. `paw done TSK-0001 --pr 12` on a fixture of one epic with one open task
   leaves the task, the epic, the decision and the index in the state `paw check`
   accepts (REQ-4600).
2. The same fixture, with every command's result diffed against its input,
   differs only in the lines the command owns (REQ-4602).

## What this does not settle

- Syncing the record with a tracker, which is a separate decision.
- A command for prose the project index carries.
