---
name: rule-t5-said-twice
description: A text carrying a named defect.
tags: [defect, rule-T5]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
The service keeps lookups in a cache. The cache expires entries after ten minutes. After ten minutes, an entry in the cache is expired. A new lookup then reads the source.
</text>
