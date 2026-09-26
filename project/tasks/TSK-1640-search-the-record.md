---
id: TSK-1640
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0636, REQ-1600, REQ-1601, REQ-1602, REQ-1604, REQ-1606, REQ-1608]
issue: 254
---

# Search the record, and search it first

Search the record, and search it first, as ADR-1180 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record, when `find approval gate` runs, then it prints identifier and heading lines ranked by the words matched, at most twenty, and no body text. Closed by: a fixture.
2. Given the `method` skill, when the prompt check runs, then it passes and the rules block carries the three rules. Closed by: the check's output and the labels.

## What to do

Add `find <word>...` to `meow record` as SPC-1100 states it, and add rules to the `method` skill: search the record with `find` before writing, follow or amend a decision found, and write a durable finding back into an artifact, each with its reason.

## Depends on

Nothing. ADR-1180 is approved.

## Evidence

`meow record find <word>...` ranks the record's artifacts by how many of the
words their identifier, title and conclusion carry, prints one line each,
identifier, kind, status and heading, at most twenty, and never a body. The
`method` skill gains three rules:

| Requirement | Carried by                                                             |
| ----------- | ---------------------------------------------------------------------- |
| REQ-1600    | M7: search before you write                                            |
| REQ-1601    | M7: specific words, independent searches at once                       |
| REQ-1602    | `find` prints headings; M7 reads a body with `show` only when relevant |
| REQ-1606    | M8: follow or amend a decision found                                   |
| REQ-1608    | M9: write a durable finding back                                       |
| REQ-1604    | M9: the record is the only memory the method keeps                     |
| REQ-0636    | `find` answers growth with search, and nothing is deleted              |

```text
$ meow-method find approval gate
REQ-0204 requirement, approved: The command that drives the chain MUST stop at every approval gate, exactly as the individual step would.
ADR-1130 decision, approved: The chain runs as steps that a program gates
ADR-1170 decision, approved: An approval is a stored status that a check holds frozen, and a session opens with what waits for one
BUG-1150 defect, approved: The crate's tests could share a temporary directory, so the gate failed at random
EPC-1100 epic, approved: The method's chain, gated by the record

$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 81 tests in 4.848s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=78, errors=3)
```

The prompt check reports 50 shipped prompts and 0 failures, and meow-method
loads 385 of its 500 characters on every turn. An earlier line here quoted a
prompt-check failure fixed before the merge; EPC-1180's verification corrected
it.

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
