---
id: ADR-2410
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2590, REQ-2592, REQ-2594, REQ-2595, REQ-2596, REQ-2597]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2410. A search reports its mode, and an absence comes only from one that read everything

## Decision

`paw find` states its mode on its first line: `exhaustive` where it read every
artifact, `ranked` where an index ordered the hits (REQ-2590). Today it reads
every file under the record root, so it prints `exhaustive`. A step may write
"the record has no X" only from an exhaustive search, and a ranked search
supports only "the search found X" (REQ-2592).

Each hit names its file and its heading, and a step that quotes a hit reads
the artifact around it first, with `paw show` (REQ-2594). The last line counts
the artifacts that matched, never the lines that did, so three hits in one
requirement count as one place (REQ-2595).

Where a unit later reads through an index, such as a document query tool, the
index is a cache: the unit refreshes it before it relies on a miss, resolves
each hit to its file before citing it (REQ-2596), and reports a result as
local to this machine (REQ-2597).

Once this is accepted, a reader of `paw find`'s output can tell a complete
answer from a partial one. What still doesn't work: no unit reads through an
index yet, so the index rules apply to nothing until one does (ADR-2430).

## Why

RES-0141 found that a ranked search answers "what is most like this" while an
exhaustive one answers "what contains this", and that treating the first as
the second produces confident absences that are false. Method rule M7 asks
every step to search before it writes, so the search's answer decides whether
a step writes a duplicate.

## Alternatives

| Option                         | Better at                  | Why it lost                                                          |
| ------------------------------ | -------------------------- | -------------------------------------------------------------------- |
| Do nothing                     | No change to output        | A step can't tell from the output whether a miss means absent        |
| Only ever search exhaustively  | One mode, nothing to label | It rules out an index for a corpus too large to read on every search |
| Report the mode in a flag only | Shorter default output     | A step that forgets the flag reads a ranked miss as an absence       |

## What it costs

One more line in every `paw find` output, and a line of every step's
instruction that turns "not found" into "absent" only on an exhaustive search.

## What would reverse it

- The record grows past what an exhaustive search reads in the time a step
  waits, and the only usable search is ranked.

## Consequences

`paw find` prints its mode first and its artifact count last. The method's
rule M7 says which answers each mode supports.

## How I will know it was realised

1. `paw find` prints `exhaustive` on its first line and an artifact count on
   its last (REQ-2590, REQ-2595).
2. A fixture with one requirement matching three times reports one artifact
   (REQ-2595).
3. Each hit line names a file and a heading (REQ-2594).

## What this does not settle

- Which index, if any, the harness adopts. ADR-2430 postpones the query tool.
