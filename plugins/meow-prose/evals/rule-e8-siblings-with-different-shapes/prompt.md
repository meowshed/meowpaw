---
name: rule-e8-siblings-with-different-shapes
description: A text carrying a named defect.
tags: [defect, rule-E8]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Commands

## build

| Flag        | Meaning             |
| ----------- | ------------------- |
| `--release` | Optimise the output |

## test

When I first wrote the test command, it only ran unit tests, but over the months it grew, and now it runs everything it finds under `tests/`, which is why it can take a while.

## lint

- Runs the linter
- Exits 1 on a finding
- Prints one line for each finding
</text>
