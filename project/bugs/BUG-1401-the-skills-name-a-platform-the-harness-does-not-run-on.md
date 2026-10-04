---
id: BUG-1401
artifact: bug
status: approved
severity: major
violates: REQ-4102
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi skills name a platform the harness does not run on

The skills shipped in the Pi packages are the Claude Code plugins' `SKILL.md`
files copied byte for byte, so they still name `${CLAUDE_SKILL_DIR}` in every
command and file reference: fourteen of fifteen skills carry it, forty
references in all. Pi never sets that variable, so the model reads an
instruction such as "Run `${CLAUDE_SKILL_DIR}/../../bin/paw ready <step>`",
runs the literal string as a shell command, and the shell answers `command
not found`.

## Expected

A skill in a Pi package tells the model how to run its unit's binary and read
its supporting files on Pi (REQ-4102), because the skill is the unit's
behaviour and a skill that cannot be followed loads for nothing.

## Actual

`grep -rl 'CLAUDE_SKILL_DIR' packages/*/skills/` at `84f8ee63` lists fourteen
files. Following the method skill in a Pi session fails at its step 3:
`paw ready research` never runs, because the command the model was given
starts with an unset variable's literal text.

## Reproduction

1. `pi install ./packages/meow-flow`, then in a Pi session ask for the
   research step on any question.
2. The session loads `skills/method/SKILL.md` and reaches step 3, which
   says to run `${CLAUDE_SKILL_DIR}/../../bin/paw ready research`.
3. The Bash tool reports `no such file or directory`, because no
   `CLAUDE_SKILL_DIR` exists in Pi's environment and no directory of that
   name sits in the working directory.

## Environment

Pi 1.0.2 on macOS 15 (aarch64); meowpaw at `84f8ee63`; package
`@meowshed/meow-flow` 0.47.0 as shipped by EPC-2700.
