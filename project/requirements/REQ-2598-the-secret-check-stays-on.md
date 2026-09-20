---
id: REQ-2598
artifact: requirement
topic: helpers
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0142
verification: behavioural
---

# REQ-2598

The harness MUST leave a packer's credential check enabled and MUST report a
repository configured to disable it rather than packing under that setting.

It is the only automatic protection between a repository's credentials and
whoever receives the pack.
