---
name: rule-e14-table-without-a-takeaway
description: A text carrying a named defect.
tags: [defect, rule-E14]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Instance sizes

We tested three instance sizes against the same workload.

## Results

The workload ran for one hour on each size.

The cost is listed per hour.

| Size   | p95 latency | Cost |
| ------ | ----------- | ---- |
| small  | 410 ms      | 0.08 |
| medium | 190 ms      | 0.17 |
| large  | 185 ms      | 0.34 |

</text>
