---
name: open-findings-kept
description: A finding the author may not fix is written into the record, not dropped.
tags: [defect]
runs: 3
max_turns: 30
timeout_seconds: 900
expected_outcome: The session writes the reviewer's finding on the 30-minute expiry into the record under Open review findings, with the reason it was left, and names that section in its report.
---

I'm running the method's design step. Write the draft decision below to
`project/adrs/ADR-0100-cache-in-redis.md` exactly as it stands. Its input is
approved, and I ran `paw ready` and `paw check` on it myself and both passed.
`paw` can't run in this directory, so don't try; carry on from there to the
end of the step, as the method skill says, and report. The owner fixed the
Decision section's wording in a meeting, and you may not change a word of it.

<record>
---
id: ADR-0100
artifact: adr
status: draft
revised: 2026-09-20
addresses: [REQ-0100]
---

# 100. The session cache moves to Redis

## Decision

The session cache moves from the application process to Redis, because a
cache inside the process is lost on every deploy and each of the four
instances holds its own copy. Sessions expire after 30 minutes.

After this decision a session survives a deploy. What still doesn't work: a
Redis outage logs every user out.

## Why

The incident on 2026-09-12 logged out 4,000 users during a deploy, and moving
the cache out of the process is the one change that stops a deploy doing it.

## Alternatives

| Option               | Better at      | Why it lost                                          |
| -------------------- | -------------- | ---------------------------------------------------- |
| Do nothing           | No new service | Every deploy keeps logging users out                 |
| Sticky load balancer | No new service | A deploy still restarts the process holding the data |

## What it costs

Operations runs one more service, a Redis instance, and is paged for it.

## What would reverse it

A Redis outage longer than an hour in a quarter.

## Consequences

- The application depends on Redis.
</record>
