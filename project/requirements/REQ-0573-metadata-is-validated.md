---
id: REQ-0573
artifact: requirement
topic: artifacts
class: functional
status: approved
revised: 2026-09-20
unit: U-0001
elaborates: RES-0019
verification: behavioural
---

# REQ-0573

An artifact's metadata MUST be validated against its kind's schema before
anything relies on it, because a tool that reads an unvalidated field reports
a fact it did not check.
