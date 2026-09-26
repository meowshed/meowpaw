---
id: TSK-1860
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1270
closes: [REQ-0036, REQ-0038, REQ-0040]
issue:
---

# An unavailable capability names what would supply it

An unavailable capability names what would supply it, as ADR-1270 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a profile declaring no `test`, when `meow-verbs status` runs, then the line names `.meowpaw/profile.toml` and `[verbs]` and says unresolved. Closed by: a fixture.
2. Given a unit with no binary for the machine, when its launcher runs, then it names the machine and the reinstall and exits as unchecked. Closed by: a fixture.

## What to do

Make `meow-verbs status` and `run` say, for an undeclared verb, to declare it under `[verbs]` in `.meowpaw/profile.toml`, and for a value that isn't one command, to write one. Make each launcher's report of a missing binary name the machine's system and processor and say to reinstall the unit. Keep every such outcome unresolved or unchecked.

## Depends on

Nothing. ADR-1270 is approved.

## Evidence

Not yet.

## Left alone

A doctor that reports every unit's capabilities at once, which ADR-1270
leaves.
