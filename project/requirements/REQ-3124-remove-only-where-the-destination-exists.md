---
id: REQ-3124
artifact: requirement
topic: onboarding
class: functional
status: approved
revised: 2026-09-26
elaborates: RES-0277
verification: behavioural
---

# REQ-3124

Removing onboarded documents MUST refuse to remove a migrated or superseded
document whose destination resolves to no artifact.

A document migrated to an artifact that doesn't exist was never migrated, and
removing it loses its content.
