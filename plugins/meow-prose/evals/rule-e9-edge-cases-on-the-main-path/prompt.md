---
name: rule-e9-edge-cases-on-the-main-path
description: A text carrying a named defect.
tags: [defect, rule-E9]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Quick start

The timer converts a local time to UTC. Daylight saving changes make the offset differ by date, and in a zone that skipped a day, such as Samoa in 2011, the conversion of 30 December returns an error because the day does not exist. The offset table holds 598 rows and is derived from the tz database by taking each zone's transitions, sorting them and merging adjacent rows with equal offsets.

Run `timer convert 2026-03-01T09:00 Europe/Oslo`.
</text>
