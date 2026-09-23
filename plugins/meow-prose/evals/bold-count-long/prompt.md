---
name: bold-count-long
description: A text carrying a named defect.
tags: [defect, named]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
**The cache is the answer.** Three things make this work. The worker reads the batch from the queue, checks each record against the schema that the upstream team publishes every morning at six, retries the ones that fail validation twice with a two-second wait between attempts, and writes the rest to the store so the reporting job can pick them up before the nightly export runs.
</text>
