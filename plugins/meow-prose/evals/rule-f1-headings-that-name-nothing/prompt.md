---
name: rule-f1-headings-that-name-nothing
description: A text carrying a named defect.
tags: [defect, rule-F1]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Cache

## Overview

The cache holds the last 1,000 lookups.

## Details

Entries expire after 10 minutes, so a price can lag its source.

## More

Clear it with `cache clear` after a price import.
</text>
