---
name: rule-e5-opens-with-own-vocabulary
description: A text carrying a named defect.
tags: [defect, rule-E5]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# The Reconciler

The Reconciler is a component of the Ledger Subsystem that applies the Settlement Policy to each Batch. It runs after the Collector.

Without it, a payment that arrives twice is counted twice, and the monthly total is wrong.
</text>
