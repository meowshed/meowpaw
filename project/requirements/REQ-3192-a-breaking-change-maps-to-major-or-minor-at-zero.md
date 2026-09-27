---
id: REQ-3192
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0221, RES-0264
source: semantic versioning, reconciled with REQ-2994
verification: behavioural
---

# REQ-3192

A commit marked as breaking an interface MUST map to a major version in the
release it lands in, or to a minor version while the major version is zero,
because major version zero is where anything may change, and REQ-2994 keeps
the harness there until its interface stops moving.
