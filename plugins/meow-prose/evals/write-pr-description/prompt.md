---
name: write-pr-description
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write a pull request description for this change: the dashboard's colour palette moves from hard-coded hex values to CSS variables, so a theme can override them, and the three components that used the old values now read the variables. Print only the description.
