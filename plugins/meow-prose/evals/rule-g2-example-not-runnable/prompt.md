---
name: rule-g2-example-not-runnable
description: A text carrying a named defect.
tags: [defect, rule-G2]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
Fetch the report with:

```fish
curl -H "Authorization: Bearer $TOKEN" https://api.example.test/v1/report
```

The call returns the report as a table.
</text>
