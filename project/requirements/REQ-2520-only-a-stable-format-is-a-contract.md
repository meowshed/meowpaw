---
id: REQ-2520
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0131, RES-0132
verification: behavioural
---

# REQ-2520

Where a tool documents one of its output formats as stable, the harness MUST
treat only that one as a contract and MUST read any other as best effort.

A format with no compatibility promise changes between versions and with the
user's configuration, and a parser built on one fails on somebody else's
machine for reasons the repository cannot show.
