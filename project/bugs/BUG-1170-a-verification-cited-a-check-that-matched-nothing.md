---
id: BUG-1170
artifact: bug
status: approved
severity: major
violates: REQ-0288
found: 2026-09-26
revised: 2026-09-26
issue: 239
---

# A verification cited a check that matched nothing

A verification recorded a criterion as met on the output of a script that had
checked nothing.

## Reproduction

At the revision #238 merged, on macOS 27.0, run the trace script #238 used
against EPC-1160's tasks. Its pattern expected one space around each table
cell, and the formatter pads the tables, so it matched no row and printed:

```text
0 traced labels found in their step files, 0 missing
```

## What the system does

EPC-1160's `## Verified` table recorded criterion 1 as met, "found each label
in its step file", with that output as the evidence. The script exited 0,
because it failed only on a missing label, and a run that found none had no
missing label either.

## What it should do, and why

REQ-0288 asks verification to judge whether each check would fail if its
requirement were violated, and to report one that wouldn't. A check that
matches nothing can't fail, so its passing is no evidence, and the
verification should have read "0 found" as a failure of the check.

## Triage

Implementation, in how the verification was run. The criterion itself is met:
run with a pattern that tolerates the padding, the script finds all 139 labels
the six step tasks trace, and none missing. The severity is major because an
approved record carried a claim with nothing behind it.

## Closed by

The script now fails when it finds nothing as well as when a label is missing,
and EPC-1160's row cites the corrected run: 139 found, 0 missing. The row is
marked as corrected by this record, so the change is visible in the epic.
