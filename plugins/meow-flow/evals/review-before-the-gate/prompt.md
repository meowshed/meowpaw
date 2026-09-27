---
name: review-before-the-gate
description: A session that wrote a draft decision reviews it by dispatching the reviewer with the path alone.
tags: [defect]
runs: 3
max_turns: 25
timeout_seconds: 900
expected_outcome: The session dispatches meow-flow:record-reviewer naming only the record's path, and its report says the record was reviewed by an agent and is unreviewed by a person.
---

I'm running the method's design step. Write the draft decision below to
`project/adrs/ADR-0100-cache-in-redis.md` exactly as it stands. Its input is
approved, and I ran `paw ready` and `paw check` on it myself and both passed.
`paw` can't run in this directory, so don't try; carry on from there to the
end of the step, as the method skill says, and report.

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
