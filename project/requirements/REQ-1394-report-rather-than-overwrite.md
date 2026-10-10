---
id: REQ-1394
artifact: requirement
topic: the-forge
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0025
verification: behavioural
---

# REQ-1394

**Withdrawn. Replaced by REQ-4700 and REQ-4702.**

It read: where the two sides disagree on a field the repository owns, the harness MUST report rather than overwrite.

RES-0349 finds that which side changed can only be told from a fingerprint of
each side, so ADR-2890 changes what it says: a draft takes the tracker's change and an approved record only reports it.
