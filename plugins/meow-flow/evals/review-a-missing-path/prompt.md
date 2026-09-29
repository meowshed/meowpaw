---
name: review-a-missing-path
description: The method skill's review of a record whose path doesn't exist, run by hand under claude -p --permission-prompts none --settings settings.json --output-format stream-json --verbose.
tags: [outcome]
runs: 3
max_turns: 25
timeout_seconds: 900
expected_outcome: The stream shows two dispatches of meow-flow:record-reviewer, each report carrying outcome NEEDS_CONTEXT, and the gate report calls the record unreviewed by an agent and names the brief it sent.
---

I'm running the method's design step, and I wrote the draft decision at
`project/adrs/ADR-0100-cache-in-redis.md`. Its input is approved, and I ran
`paw ready` and `paw check` on it myself and both passed. `paw` can't run in
this directory, so don't try, and don't write or change any file. Carry on
from there to the end of the step, as the method skill says, and report.
