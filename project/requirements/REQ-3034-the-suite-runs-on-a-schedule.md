---
id: REQ-3034
artifact: requirement
topic: the-harness-on-itself
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0266
verification: behavioural
---

# REQ-3034

**Withdrawn. Replaced by REQ-3035.**

It read: the measurement suite MUST run on a schedule and at release rather
than on every change, because every run is a real model call.

It asked for a scheduled run, and the owner keeps model calls out of
continuous integration and runs evaluations by hand, so ADR-2690 left the
conflict open for a later decision. ADR-2840 withdraws the schedule and keeps
the reason it gave: REQ-3035 asks for a run by hand, and REQ-3038 keeps a new
model as a reason to run it again.
