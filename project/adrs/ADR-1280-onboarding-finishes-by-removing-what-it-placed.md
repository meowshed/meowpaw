---
id: ADR-1280
artifact: adr
status: done
revised: 2026-09-26
addresses:
  [REQ-3114, REQ-3116, REQ-3118, REQ-3120, REQ-3122, REQ-3124, REQ-3126]
supersedes: []
---

# 1280. Onboarding finishes by removing what it placed, once the report is approved

## Decision

`meow-method onboarding remove` finishes a conversion. It reads the approved
onboarding report and removes from the working tree each document the report
marks migrated, superseded or discarded, keeping each one marked cited:

- It refuses to run while the report isn't approved, and removes nothing.
- It refuses to remove a migrated or superseded document whose destination
  names no artifact that exists, and says which.
- It prints the number of documents before and after, and each path it
  removed, and it commits nothing, so the removal is a change of its own that
  a person reviews.

`/meow-method:onboard` gains two rules: a record the repository keeps in a
format of its own, such as a folder of decision records or a task list,
migrates to the artifact kind that holds it; and every requirement or decision
it recovers is written as a draft, which a person's approval affirms. Its last
step names `onboarding remove` as what follows the report's approval.

After this decision a repository converts from its documents to the method
completely: its old documents are either in the record, cited from it, or
gone with a reason. What still doesn't work: the forge's issues and pull
requests aren't read, which ADR-1290 and ADR-1300 add.

## Why

RES-0277 found that once a person approves the report, a migrated, superseded
or discarded document left in place is a second source of truth, while a
cited one must stay because the citation points at it. RES-0037 found that
nothing is deleted before it is placed, and RES-0265 that a bulk removal needs
a count before and after and belongs in a change of its own. RES-0277 found a
record kept in a repository's own format to be the strongest evidence of its
decisions.

The strongest objection: a model could delete the files as the report says,
with no command. It could, and a program refuses on an unapproved report and a
missing destination every time, where a model follows a rule most of the
time; a deletion is the one step a person can't undo by reading a diff.

## Alternatives

| Option                                 | Better at                       | Why it lost                                                     |
| -------------------------------------- | ------------------------------- | --------------------------------------------------------------- |
| A command reading the approved report  | Refuses the same way every time | Chosen                                                          |
| The onboard command deletes as it goes | One step                        | Deletes before a person approves where each document went       |
| Leave the old documents for the person | Nothing to build                | Two sources of truth, and the conversion is never finished      |
| Do nothing                             | Costs nothing                   | A ported repository keeps both its old documents and its record |

## What it costs

A subcommand with its refusals and its count, and two rules in the onboard
command.

## What would reverse it

- Converted repositories keep wanting their old documents, and removal
  becomes moving them to a history branch.

## Consequences

- `meow-method onboarding remove` exists, and removes only on an approved
  report.
- `/meow-method:onboard` migrates an existing record and writes recovered
  records as drafts.

## How I will know it was realised

1. Fixtures show `onboarding remove` refusing on a draft report, refusing a
   migrated document whose destination doesn't exist, keeping a cited
   document, and removing the rest with a count before and after.
2. Each rule ADR-1280 places in the onboard command maps to its requirement in
   the task that closes it.
3. Every requirement ADR-1280 addresses lands in exactly one closed task.

## What this does not settle

- Reading a forge's issues and pull requests, which ADR-1290 and ADR-1300
  take.
