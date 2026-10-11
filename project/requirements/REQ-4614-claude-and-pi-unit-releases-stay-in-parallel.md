---
id: REQ-4614
artifact: requirement
topic: pi-packages
class: non-functional
status: approved
revised: 2026-10-11
elaborates: ADR-2920
verification: static
---

# REQ-4614

A change to a unit's shared behavior, skill, public contract or user-facing
documentation MUST update its Claude plugin and Pi package in the same pull
request, and both manifests MUST carry the same version.

A unit tag releases both distributions. If one side misses the change or keeps
a different version, users of that platform receive a different unit under the
same release identity. Host-specific adapters remain specific to their
platform, while shared skill behavior stays aligned.
