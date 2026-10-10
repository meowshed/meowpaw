---
id: EPC-2790
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2870
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2790. The units drop their own builds

This epic realises the second half of ADR-2870. It is complete when no unit but
the core unit carries a binary, and the standalone check lets a unit name the
core unit and no other.

## Acceptance criteria

1. No unit but `meow-core` carries a binary, and the release packs none in
   them (ADR-2870, criterion 1).
2. `tools/check_standalone.py` passes for a unit that names `meow-core` under
   `dependencies`, and fails for one that names another unit (ADR-2870,
   criterion 2).

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5302 The release packs one build and the units ship none (done: pull request 881)
      closes: REQ-4500
      depends: EPC-2780 is done (blocking) - the launchers find the shared binary first
- [x] T-002 TSK-5303 The standalone check lets a unit name the core unit (done: pull request 881)
      closes: REQ-4502
      depends: TSK-5302 (not blocking) - either can land first

## Coverage

REQ-4500 and REQ-4502 land in these tasks as well as in EPC-2780, because the
requirements state the end state and this epic reaches it.

## Not covered

- REQ-4504, REQ-4506 and REQ-4508, which EPC-2780 closes.
- The Pi packages, which already share one binary (REQ-4136).
