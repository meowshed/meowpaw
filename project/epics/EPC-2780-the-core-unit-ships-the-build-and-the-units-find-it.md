---
id: EPC-2780
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2870
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2780. The core unit ships the build and the units find it

This epic realises the first half of ADR-2870. It is complete when the core
unit carries the binary and writes where it is, and every unit that runs a
program can find it and declares the dependency, with the units still carrying
their own builds.

## Acceptance criteria

1. `plugins/meow-core` carries the binary for each platform the harness
   supports (ADR-2870, criterion 1, in part).
2. Each unit that runs a program names `meow-core` and nothing else under
   `dependencies` (ADR-2870, criterion 2).
3. A unit's launcher run with the data file absent exits 3 and names
   `meow-core` (ADR-2870, criterion 3).

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5300 The core unit ships the one build and writes where it is (done: pull request 881)
      closes: REQ-4500
      depends: nothing
- [x] T-002 TSK-5301 Each unit declares the dependency and finds the binary (done: pull request 881)
      closes: REQ-4502, REQ-4504, REQ-4506, REQ-4508
      depends: TSK-5300 (blocking) - a launcher needs the data file to read

## Coverage

REQ-4500 lands in TSK-5300. REQ-4502, REQ-4504, REQ-4506 and REQ-4508 land in TSK-5301.

## Not covered

- Removing the units' own builds, which EPC-2790 does after this one.
