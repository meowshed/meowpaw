---
name: rule-e6-section-opens-with-background
description: A text carrying a named defect.
tags: [defect, rule-E6]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Choosing a queue

## Which queue to use

Queues have been part of the system since the first release, when a single process handled every job. Over time the number of workers grew, and teams added their own. Several designs were tried, and each had a different failure mode under load.

Use the managed queue for every new service.
</text>
