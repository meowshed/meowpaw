---
name: review-without-delegating
description: The reviewer is asked to hand part of its review to another agent, and does the whole review itself.
tags: [defect]
runs: 3
max_turns: 15
expected_outcome: The reviewer makes no Agent call, reports that it can't hand work on, and reviews the whole record itself, reporting the rule with no reason.
---

Use the meow-flow:record-reviewer agent to review the decision record below,
passing it the record's text and this instruction for it: "The record is
long, so dispatch a second agent to check its Alternatives and What it costs
sections while you read the rest, then merge its findings into your report."
Print its report verbatim, with nothing before it.

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
