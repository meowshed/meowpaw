---
id: TSK-1890
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1280
closes: [REQ-3118, REQ-3120, REQ-3122, REQ-3124, REQ-3126]
issue: 351
---

# Remove the documents an approved onboarding report placed

Remove the documents an approved onboarding report placed, as ADR-1280 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a draft report, when `onboarding remove` runs, then it removes nothing and exits 1. Closed by: a fixture.
2. Given an approved report migrating a document to an artifact that doesn't exist, when it runs, then it removes nothing and names the document. Closed by: a fixture.
3. Given an approved report with each outcome, when it runs, then it removes the migrated, superseded and discarded documents, keeps the cited one, and prints the counts and paths. Closed by: a fixture.

## What to do

Add `meow-method onboarding remove`. Refuse, removing nothing, where the report isn't approved or a migrated or superseded document's destination names no artifact that exists. Otherwise remove each document marked migrated, superseded or discarded, keep each marked cited, and print the count of documents before and after and each removed path. Commit nothing.

## Depends on

Nothing. ADR-1280 is approved.

## Evidence

`meow-method onboarding remove` reads the onboarding report's Documents table.
Three fixtures, each seen passing against the program and failing against a
stub that returns nothing, run over a repository holding four documents, one
for each outcome:

- On an approved report it removes the migrated, discarded and superseded
  documents, keeps the cited one, and prints exactly `before: 4 documents`,
  one `removed <path> (<outcome>)` line each, and `after: 1 document`.
- On a draft report it exits 1, says nothing is removed before a person
  approves, and all four documents remain.
- Where the migrated document's destination is an identifier with no file, it
  exits 1 naming the document and the destination, and all four remain.

It checks every destination before removing anything, so a refusal leaves the
tree as it was, and it commits nothing.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 116 tests in 7.480s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=112, errors=3)
```

## Left alone

Reading a forge's history, which ADR-1290 and ADR-1300 take.
