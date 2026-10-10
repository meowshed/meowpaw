---
name: rule-e2-no-stated-reader
description: A text carrying a named defect.
tags: [defect, rule-E2]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Rotating the signing key

The signing key rotates every 90 days. A new key is generated, published to the key server, and used for the next release. The old key stays valid for 14 days.

## Steps

1. Generate the key.
2. Publish it.
3. Update the release job.
</text>
