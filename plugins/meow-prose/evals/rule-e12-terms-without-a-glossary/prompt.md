---
name: rule-e12-terms-without-a-glossary
description: A text carrying a named defect.
tags: [defect, rule-E12]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# The relay

A lane carries tickets from a spool to a shard. The relay moves a ticket between lanes when a quorum of shards agrees. A spool holds at most 500 tickets, and a lane holds one ticket at a time.

A shard that misses three relays leaves its quorum.
</text>
