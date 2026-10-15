---
name: rule-c1-forty-word-sentence
description: A text carrying a named defect.
tags: [defect, rule-C1]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
The importer reads one file at a time. When the importer reads a file whose header names a column that the schema no longer holds, because an earlier release dropped it and the exporter on the other side was never updated, it stops with an error that names the column but not the file, which sends the operator searching. Add the file name to the error.
</text>
