---
name: rule-t1-context-before-the-answer
description: A text carrying a named defect.
tags: [defect, rule-T1]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
In the first release the exporter wrote every field. Later a customer asked for a smaller file, and the team discussed a column filter at length. After that discussion the exporter gained one. The exporter now writes only the columns named in `columns.toml`.
</text>
