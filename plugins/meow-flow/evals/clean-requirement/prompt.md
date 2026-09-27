---
name: clean-requirement
description: A requirement with nothing missing, which the reviewer should report as clean.
tags: [clean]
runs: 3
max_turns: 15
expected_outcome: The report opens with the agent's label and says in one sentence that the requirement is clean, with no invented finding.
---

Use the meow-flow:record-reviewer agent to review the requirement record
below, passing it both records' text: the requirement, and the research it
elaborates for reference. Print its report verbatim, with nothing before it.

<record>
---
id: RES-0100
artifact: research
status: approved
revised: 2026-09-18
---

# Session loss on deploy

## Summary

Every deploy logs every user out, because sessions live in the application
process and a deploy restarts it.

## Method

I read the incident log for 2026-09-12 and the deploy script, both read
2026-09-18.

## Conclusions

1. A deploy restarts every process, so a session kept in a process is lost.
2. A session kept outside the process survives the restart.

## Sources

- The incident log for 2026-09-12, read 2026-09-18.
- `deploy/restart.sh` at revision 4f2a9c1, read 2026-09-18.
</record>

<record>
---
id: REQ-0100
artifact: requirement
topic: sessions
class: functional
status: draft
revised: 2026-09-20
elaborates: RES-0100
verification: behavioural
---

# REQ-0100

A request carrying a session that was valid before a deploy MUST be accepted
after the deploy, until the session's own expiry, without the user signing in
again, because a deploy that signs every user out interrupts their work for
nothing they did.
</record>
