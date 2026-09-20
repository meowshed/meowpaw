---
id: REQ-2398
artifact: requirement
topic: unattended-runs
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0074
verification: static
---

# REQ-2398

The hosts an unattended run may reach MUST be enumerated narrowly rather than
permitted by a broad pattern.

The proxy decides from the hostname the client supplies and does not decrypt
the connection, so a broad allowance is an exfiltration path rather than a
convenience.
