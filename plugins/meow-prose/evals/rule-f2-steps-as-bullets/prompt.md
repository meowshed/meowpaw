---
name: rule-f2-steps-as-bullets
description: A text carrying a named defect.
tags: [defect, rule-F2]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Release the plugin

The steps depend on each other, and each must finish before the next starts:

- Merge the pull request
- Tag the release
- Build the archives
- Upload the archives to the tag
</text>
