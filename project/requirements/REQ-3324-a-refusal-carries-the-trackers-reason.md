---
id: REQ-3324
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0312
verification: behavioural
---

# REQ-3324

A report of a call the tracker refused MUST carry the reason the tracker gave,
beside the permission it named.

The tracker's permission headers say what an endpoint accepts, not why this
credential was refused, and a refusal caused by single sign-on reads as a
missing permission without the tracker's own words.
