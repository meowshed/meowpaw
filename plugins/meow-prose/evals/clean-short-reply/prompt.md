---
name: clean-short-reply
description: A text the standard accepts.
tags: [clean]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
The export failed because the disk on the reporting host filled at 02:10 UTC. I cleared the old archives, which freed 40 GB, and reran the export, which finished at 02:55 UTC. I lowered the disk alert from 95% to 80%, because at last night's fill rate of about 15% an hour it now fires about 80 minutes before the disk is full, where it used to fire about 20 minutes before.
</text>
