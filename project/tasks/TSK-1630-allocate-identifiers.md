---
id: TSK-1630
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0548, REQ-0550]
issue: 253
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

`meow record new <kind> [--topic <topic>]` prints the next identifier: a
requirement's next free number above its topic's highest, stepping by two, a
new topic's block a hundred above the highest, research's next number, and
every other kind's next block of ten. It treats as taken every identifier of
the kind that any file carries or cites, so a withdrawn number or one cited
before its file exists is never given again. Five fixtures:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 78 tests in 4.904s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=76, errors=2)
```

On this repository:

The method topic's highest is 3172, and 3174 to 3188 belong to other topics, so
the next free number stepping by two is 3190; the number is written without its
prefix here because no requirement carries it yet:

```text
$ meow-method new requirement --topic the-method
(the requirement numbered 3190)
$ meow-method new adr
ADR-1190
$ meow-method new task
TSK-1650
$ meow-method new research
RES-0276
```

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
