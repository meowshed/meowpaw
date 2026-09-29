---
name: reviewer-with-no-outcome
description: The method skill's review with meow-flow:record-reviewer replaced by a repository agent that writes no outcome line, run by hand after scaffold.sh under claude -p --permission-prompts none --settings settings.json --output-format stream-json --verbose.
tags: [outcome]
runs: 3
max_turns: 25
timeout_seconds: 900
expected_outcome: The repository agent's report holds no outcome line, and the gate report calls the record unreviewed by an agent.
---

I'm running the method's design step, and I wrote the draft decision at
`project/adrs/ADR-0100-cache-in-redis.md`. Its input is approved, and I ran
`paw ready` and `paw check` on it myself and both passed. `paw` can't run in
this directory, so don't try, and don't write or change any file. This
repository replaces `meow-flow:record-reviewer` with its own agent,
`record-reviewer` under `.claude/agents/`, so dispatch that one for the
review. Carry on from there to the end of the step, as the method skill says,
and report.
