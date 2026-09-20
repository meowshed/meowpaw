---
id: REQ-2522
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0131
verification: behavioural
---

# REQ-2522

Where a tool escapes special characters in paths by default, the harness MUST
request the unescaped form.

Otherwise a filename with a quote, a newline or a non-ascii character is
parsed into a path that does not exist.
