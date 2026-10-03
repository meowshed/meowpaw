---
id: TSK-5155
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2600
closes:
  [
    REQ-1364,
    REQ-1366,
    REQ-1370,
    REQ-1390,
    REQ-1398,
    REQ-2562,
    REQ-2570,
    REQ-2584,
    REQ-2586,
    REQ-2588,
    REQ-2824,
  ]
issue:
---

# Project an epic onto the tracker's grouping

Extend the GitHub projection through the request layer with a parent, task
links, mechanism report, pending state and recursion guard.

## Acceptance criteria

1. Given ADR-2540's fixture, projection produces every parent, link and report
   it specifies and a harness write starts no second run. Closed by: GitHub
   projection fixtures for every requirement this task closes.

## What to do

Implement ADR-2540 through the GitHub feature and its unit page.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Trackers with no grouping mechanism.
