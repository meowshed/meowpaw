---
id: REQ-1561
artifact: requirement
topic: onboarding
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0058
verification: behavioural
---

# REQ-1561

Where a repository is inconsistent about a convention, the step that writes a
profile MUST report the inconsistency rather than choose one of the variants.

Choosing silently records a decision nobody took, and the repository then has
a declared convention that half of it violates.
