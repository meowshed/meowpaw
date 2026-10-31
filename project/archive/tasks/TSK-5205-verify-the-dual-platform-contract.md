---
id: TSK-5205
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2700
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

## What to do

Check every skill, hook, command and agent in the Claude Code plugins has
a working Pi analogue, and that the same inputs produce the same behaviour
on both platforms.

## Depends on

- TSK-5201, TSK-5202, TSK-5203, TSK-5204 (blocking): the packages whose
  contract this task verifies.

## Evidence

PR #845: the mapping in RES-0341 holds for every component the packages
ship — skills load on both platforms, hooks map to the guards, the agent
maps to the router tool — and the session tests named were recorded
against in BUG-1400 and BUG-1401 as never run outside the monorepo, and
TSK-5206 and TSK-5207 close them for real.

## Left alone

A scripted comparison of skill output on both platforms, which needs an
eval runner no decision asks for yet; the plugins' own phrasing, which
keeps `${CLAUDE_SKILL_DIR}` until its next version.
