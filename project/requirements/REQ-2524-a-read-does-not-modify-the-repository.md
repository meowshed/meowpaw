---
id: REQ-2524
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0131
verification: behavioural
---

# REQ-2524

Where a tool offers a way to inspect state without taking a lock or refreshing
what it stores, the harness MUST use it.

A read that writes contends with the person's own work and makes the harness's
observation part of what it observed.
