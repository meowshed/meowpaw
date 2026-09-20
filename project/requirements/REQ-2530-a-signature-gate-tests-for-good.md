---
id: REQ-2530
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0131
verification: behavioural
---

# REQ-2530

A signature gate MUST test for the verdict that means a good signature from a
trusted key, MUST NOT accept a verdict that merely is not bad, and MUST report
a verdict that describes missing local key material as unverifiable rather
than as unsigned.

Several verdicts describe a good signature made with a key that should not be
trusted, and all of them pass a test written as not bad.
