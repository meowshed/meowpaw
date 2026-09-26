---
id: TSK-1630
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0548, REQ-0550]
issue:
---

# Allocate the next identifier

Allocate the next identifier, as ADR-1180 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a topic whose highest requirement is REQ-0010, when `new requirement --topic t` runs, then it prints REQ-0012, and REQ-0014 once REQ-0012 exists. Closed by: a fixture.
2. Given a withdrawn REQ-0012, when `new requirement --topic t` runs, then it doesn't print REQ-0012. Closed by: a fixture.
3. Given decisions up to ADR-0010, when `new adr` runs, then it prints ADR-0020. Closed by: a fixture.

## What to do

Add `new <kind> [--topic <topic>]` to `meow record` as SPC-1100 states it: a requirement's next free number above its topic's highest, stepping by two, a new topic's block a hundred above the highest, other kinds' next block of ten, research's next number, and never an identifier any file carries.

## Depends on

Nothing. ADR-1180 is approved.

## Evidence

Not yet.

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
