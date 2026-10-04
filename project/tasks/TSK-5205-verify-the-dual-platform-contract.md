---
id: TSK-5205
artifact: task
status: draft
revised: 2026-10-04
realises: ADR-2780
closes: [REQ-4102]
issue: 840
---

# Verify the dual-platform contract

Check that every skill, hook, command and agent in the Claude Code plugins has
a working Pi analogue, and that the same inputs produce the same behaviour on
both platforms.

## Acceptance criteria

1. For each skill that a Claude Code plugin provides, the Pi package provides
   the same `SKILL.md`, and invoking it on each platform with the same input
   produces equivalent guidance. Closed by: scripted comparison of skill
   output on both platforms.
2. For each hook that a Claude Code plugin declares, the Pi extension
   registers an event handler that produces the same guard outcome for the
   same trigger. Closed by: session tests on both platforms comparing guard
   results.
3. No Claude Code plugin component lacks a Pi analogue. Closed by: checklist
   derived from RES-0341, confirmed against the built packages.
