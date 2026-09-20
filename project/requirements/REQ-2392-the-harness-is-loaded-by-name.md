---
id: REQ-2392
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0074
verification: static
---

# REQ-2392

An unattended run MUST load the harness by name rather than by discovery.

The scripted mode that skips a folder's own hooks and servers also skips
plugins, and the alternative runs a repository's code in a folder nobody ever
trusted.
