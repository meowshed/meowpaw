---
id: TSK-1650
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1190
closes:
  [
    REQ-1230,
    REQ-1231,
    REQ-1232,
    REQ-1233,
    REQ-1234,
    REQ-1235,
    REQ-1236,
    REQ-1237,
    REQ-1238,
    REQ-1239,
    REQ-1240,
    REQ-1242,
    REQ-1244,
    REQ-1246,
    REQ-1248,
    REQ-1250,
    REQ-1252,
    REQ-1254,
    REQ-1256,
    REQ-1258,
    REQ-2130,
    REQ-2138,
    REQ-2140,
    REQ-2760,
    REQ-2762,
    REQ-2764,
    REQ-2766,
    REQ-2768,
    REQ-2770,
    REQ-2772,
    REQ-2776,
    REQ-2778,
    REQ-2780,
    REQ-2782,
    REQ-2794,
    REQ-2796,
  ]
issue:
---

# The design step carries the obligations on what it designs

The design step carries the obligations on what it designs, as ADR-1190 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given `steps/design.md`, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in the file. Closed by: the trace table and a script finding each label.
2. Given the step files, when they are searched for a practice command, then none is named. Closed by: the search's output.

## What to do

Append the design rules ADR-1190 places to `steps/design.md`'s rules block, labelled after the existing ones, each with its reason and naming no requirement. Show with a search that no step file names a practice command. Record the trace under Evidence.

## Depends on

Nothing. ADR-1190 is approved.

## Evidence

Not yet.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
