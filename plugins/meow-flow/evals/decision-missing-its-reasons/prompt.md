---
name: decision-missing-its-reasons
description: A draft decision with a rule that gives no reason and a cost section that states no cost.
tags: [defect]
runs: 3
max_turns: 15
expected_outcome: The report opens with the agent's label, and reports the rule with no reason and the cost that isn't stated, each with its line and a fix.
---

Use the meow-flow:record-reviewer agent to review the decision record below,
passing it the record's text, and print its report verbatim, with nothing before it.

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
instances holds its own copy. Sessions expire after 30 minutes. Every write to
the cache goes through the `SessionStore` interface.

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

It costs little.

## What would reverse it

A Redis outage longer than an hour in a quarter.

## Consequences

- The application depends on Redis.
</record>
