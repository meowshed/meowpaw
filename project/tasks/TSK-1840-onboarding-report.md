---
id: TSK-1840
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1260
closes: [REQ-1556, REQ-3096]
issue: 329
---

# The onboarding report places every document, and the check holds it

The onboarding report places every document, and the check holds it, as ADR-1260 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a report missing a tracked document, placing one twice, naming an unknown outcome, or discarding one with no reason, when `check coverage` runs, then it reports each. Closed by: fixtures.
2. Given a report placing every document once, when `check coverage` runs, then it reports nothing on the report. Closed by: a fixture.
3. Given an Adoption section with no numbered steps, when `check rules` runs, then it reports it. Closed by: a fixture.

## What to do

Add the kind `onboarding` to `lib/layout.toml`, file `onboarding.md` at the root, statuses draft, approved and superseded, sections Verbs, Conventions, Documents, Gaps and Adoption, opening with Verbs, and the rule `adoption-in-steps`. Write `templates/onboarding.md` and add it to `template` and the templates' index. In `check coverage`, where the report exists, compare the repository's tracked documents outside the record with the Documents table: one row each, an outcome of migrated, cited, superseded or discarded, and a destination or reason.

## Depends on

Nothing. ADR-1260 is approved.

## Evidence

`lib/layout.toml` gains the kind `onboarding`, `onboarding.md` at the
record's root, opening with Verbs, and `templates/onboarding.md` holds its
five sections with a Documents table and numbered Adoption steps. Four
fixtures, each seen passing against the program and failing against a stub
that returns nothing, run over a repository holding `docs/guide.md` and
`notes.txt` outside the record:

- A report placing both, one migrated and one discarded with its reason,
  passes `check coverage`.
- Dropping the row for `notes.txt` reports it as not placed, and adding a
  second row reports it placed twice at the second row's line.
- The outcome `archived` is reported as outside the four, and a discard with
  an empty reason as having no destination or reason.
- An Adoption section with no numbered step fails `check rules`.

The documents are those git tracks or doesn't ignore, in six document
formats, outside the record's root and `.meowpaw/`.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 112 tests in 7.336s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=109, errors=3)
```

## Left alone

Measuring whether a model recovers statements faithfully, which waits for
evaluation.
