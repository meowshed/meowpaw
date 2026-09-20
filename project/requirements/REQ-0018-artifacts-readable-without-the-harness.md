---
id: REQ-0018
artifact: requirement
topic: adoption
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0011, RES-0001
verification: static
---

# REQ-0018

Every artifact the harness writes MUST be readable and editable by someone who
does not have the harness installed: plain text, in no format that only the
harness can parse.

The record outlives the tool that wrote it, and an artifact only one program
can read is lost the moment that program is not installed.
