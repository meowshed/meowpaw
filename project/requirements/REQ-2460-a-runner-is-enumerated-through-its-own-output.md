---
id: REQ-2460
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0122, RES-0123, RES-0124
verification: behavioural
---

# REQ-2460

Where a runner emits a machine-readable list of its tasks, the harness MUST
enumerate through that output rather than by reading the runner's
configuration files.

A configuration file is not the whole task list: tasks defined as files,
supplied by includes or merged from another directory appear only in what the
runner itself reports.
