---
id: REQ-2546
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0132
verification: behavioural
---

# REQ-2546

Where the source-control tool in use does not run a repository's hooks, the
harness MUST report that the checks those hooks carried are absent rather than
assume the two tools are equivalent.
