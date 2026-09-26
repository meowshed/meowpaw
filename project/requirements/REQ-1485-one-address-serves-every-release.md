---
id: REQ-1485
artifact: requirement
topic: distribution
class: functional
status: approved
revised: 2026-09-26
elaborates: RES-0274, RES-0275
verification: behavioural
---

# REQ-1485

The harness MUST publish its marketplace at one address that serves every
release, so that the platform's own update brings a person a later release
with nothing downloaded by hand.

A person who has to fetch a file again to learn that a release exists doesn't
learn it, and keeps running the version with the defect a later release
fixed. The platform already knows how to refresh a marketplace, and an address
that stays the same is all it needs.
