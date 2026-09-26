---
id: EPC-1180
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1180
checked-at:
---

# A record that grows by program

Realises exactly one authorising record, ADR-1180. The epic is complete when
the indexes are generated and checked for drift, identifiers are allocated by
the program, and the record is searched before anything is written.

## Acceptance criteria

Taken from ADR-1180, from its list of how I will know it was realised, before
the tasks below were written:

1. Adding a decision without regenerating the decisions index fails `check
index`, and `index adr --write` clears it.
2. `new requirement --topic the-method` prints an identifier no file carries,
   next to the topic's highest.
3. `find approval gate` lists identifiers and headings of records about
   approvals, and no document bodies.
4. The requirements index lists every requirement in the tree, counted before
   and after the migration.
5. Every requirement ADR-1180 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1620 generate each kind's index and check it for drift
      closes: REQ-0522, REQ-0523, REQ-0575, REQ-2870, REQ-2871, REQ-2872, REQ-2873
      evidence: four fixtures, and both indexes migrated with their counts, in
      #252.

- [x] T-002 TSK-1630 allocate the next identifier
      closes: REQ-0548, REQ-0550
      evidence: five fixtures, and the next identifiers on this repository,
      in #253.

- [x] T-003 TSK-1640 search the record, and search it first
      closes: REQ-0636, REQ-1600, REQ-1601, REQ-1602, REQ-1604, REQ-1606, REQ-1608
      evidence: three fixtures, `find` on this repository, and M7 to M9, in
      #254.

## Coverage

ADR-1180 addresses sixteen requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The three tasks can run in parallel, and
T-001 alone tests the decision. Measurable before the work finishes: the
requirements index's count against the tree's.

## Not covered

Generating the research and project indexes, and searching outside the
record, as ADR-1180 says.
