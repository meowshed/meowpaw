---
id: EPC-1200
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1200
checked-at:
---

# The harness's quality attributes, held

Realises exactly one authorising record, ADR-1200. The epic is complete when
each quality attribute ADR-1200 addresses has its check or its recorded
evidence.

## Acceptance criteria

Taken from ADR-1200, from its list of how I will know it was realised, before
the tasks below were written:

1. Each read-only command leaves the tree's hashes unchanged, and prints the
   same text twice.
2. Every unit has a `requires.toml` naming a Claude Code version, and its page
   names the behaviours it relies on with their documentation.
3. Each remaining attribute ADR-1200 addresses has its evidence recorded in the
   task that closes it.
4. Every requirement ADR-1200 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1670 read-only commands write nothing, and an index is written atomically
      closes: REQ-1720, REQ-1722, REQ-1724, REQ-1728, REQ-1730, REQ-1732
      evidence: two fixtures, ten read-only commands and an atomic write, in
      #270.

- [ ] T-002 TSK-1680 each unit declares the platform it needs and the behaviours it relies on
      closes: REQ-1736, REQ-1740, REQ-1742

- [ ] T-003 TSK-1690 record the evidence for the attributes that already hold
      closes: REQ-1726, REQ-1734, REQ-1744, REQ-1746, REQ-1748, REQ-1750, REQ-1752, REQ-1754, REQ-1756, REQ-1758, REQ-1762, REQ-1766

## Coverage

ADR-1200 addresses 21 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The three tasks can run in parallel, and
T-001 alone tests the part a program settles.

## Not covered

REQ-1738, REQ-1759 and REQ-1764, as ADR-1200 says.
