---
name: rule-e10-forward-reference
description: A text carrying a named defect.
tags: [defect, rule-E10]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Retention

## The default period

The service keeps events for 30 days, and section 7 explains why. After that the events are deleted.

## Other sections

(Sections 3 to 6 are omitted from this excerpt.)

## 7. The reason for 30 days

A longer period doubled the storage bill and no consumer read events older than 20 days.
</text>
