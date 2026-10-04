---
id: BUG-1401
artifact: bug
status: approved
severity: major
violates:
enters: requirements
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi skills name a platform the harness does not run on

The skills shipped in the Pi packages are the Claude Code plugins'
`SKILL.md` files copied byte for byte, so they still name
`${CLAUDE_SKILL_DIR}` in every command and file reference: fourteen of
fifteen skills carry it, forty references in all. Pi never sets that
variable, so the model reads an instruction such as "Run
`${CLAUDE_SKILL_DIR}/../../bin/paw ready <step>`", runs the literal string
as a shell command, and the shell answers `command not found`.

## Reproduction

Pi 1.0.2 on macOS 15 (aarch64), the packages at `84f8ee63`:

1. `pi install ./packages/meow-flow`, then in a Pi session ask for the
   research step on any question.
2. The session loads `skills/method/SKILL.md` and reaches step 3, which
   says to run `${CLAUDE_SKILL_DIR}/../../bin/paw ready research`.
3. The Bash tool reports `no such file or directory`: no `CLAUDE_SKILL_DIR`
   exists in Pi's environment and no directory of that name sits in the
   working directory.

## What the system does

The method skill's step 3, the very first gated command the method asks
for, cannot run: `grep -rl 'CLAUDE_SKILL_DIR' packages/*/skills/` lists
fourteen files at `84f8ee63`. The record check, the template step and every
binary-named instruction fail the same way.

## What it should do, and why

A skill in a Pi package tells the model how to run its unit's binary and
read its supporting files on Pi, because the skill is the unit's behaviour
and a skill that cannot be followed loads for nothing. What this defect
showed wrong is REQ-4102 itself — a byte-identical copy cannot work — so
the requirements step withdrew it and REQ-4132 states what holds in its
place, which TSK-5207 implements.

## Triage

Enters at implement, because the requirement named the portability and the
copy kept a platform variable no other platform sets. Major, because the
method's first command fails and no part of the chain can run past it.

## Closed by

TSK-5207. `grep -r 'CLAUDE_SKILL_DIR\|CLAUDE_PLUGIN_ROOT' packages/`
reports no match, and a Pi session running the method skill's step 3
answers `paw ready research: ready; research needs no approved input`.
