---
id: REQ-2814
artifact: requirement
topic: source-control
class: functional
status: withdrawn
revised: 2026-09-27
elaborates: RES-0221
source: semantic versioning
verification: behavioural
---

# REQ-2814

**Withdrawn. Replaced by REQ-3192.**

It read: a commit marked as breaking an interface MUST map to a major version
in the release it lands in. Marking it and then releasing it as a minor
version is the same as not marking it; REQ-2212 is what requires the mark.

It named no exception for major version zero, where REQ-2994 keeps the
harness, so it and REQ-2994 couldn't both be met by a unit below 1.0.0.
REQ-3192 keeps the mapping and states the exception semver makes at zero.
