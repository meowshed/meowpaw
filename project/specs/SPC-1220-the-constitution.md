---
id: SPC-1220
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-2732,
    REQ-2734,
    REQ-2736,
    REQ-2738,
    REQ-2740,
    REQ-2744,
    REQ-2745,
    REQ-2746,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The constitution

## Scope

This covers a repository's constitution, `CLAUDE.md` at its root: what it
carries, what it leaves out, the length `paw check` reports, how
`/meow-flow:init` writes one and how the design step keeps it free of
contradiction.

It leaves the rules a unit ships to SPC-1030, which holds that none depends on
being read last, the other living documents to SPC-1070 and SPC-1230, and the
rest of `/meow-flow:init` to SPC-1090.

ADR-2570 decides it, and EPC-2440 realises it.

## Boundary

| Surface                                           | What it is                                                     |
| ------------------------------------------------- | -------------------------------------------------------------- |
| `CLAUDE.md`                                       | The repository's constitution, at its root                     |
| `plugins/meow-flow/templates/constitution.md`     | The template `/meow-flow:init` writes a constitution from      |
| `paw check`                                       | Reports a constitution over its target length, failing nothing |
| `plugins/meow-flow/skills/method/steps/design.md` | Asks whether a decision's rule pulls against one already there |

## Behaviour

### What it carries

A constitution carries what is always relevant, can't be checked and can't be
derived (REQ-2744). It carries no procedure, no material specific to a
language, no explanation of the method and nothing the repository already
shows, because each of those loads on demand or is visible in the tree
(REQ-2745). Each rule names a command, a path or a value (REQ-2736). A rule
that must hold every time names the check that holds it, so the constitution
is never its only carrier (REQ-2732).

When the constitution is rewritten, each rule whose failure hasn't recurred in
the evidence of the last ten merged tasks is proposed for removal, with that
count (REQ-2746).

### Its length

`paw check` counts the constitution's lines and, over 200, prints
`CLAUDE.md: over its target of 200 lines at <n>; cut it` after the checks'
findings (REQ-2734). The line is advice and no finding: it counts towards no
check's findings and leaves the exit status as the checks set it, because 200
lines is a target and a hard limit would cut rules to fit a number. Where no
`CLAUDE.md` exists at the root, `paw check` prints nothing about it.

### The harness's instructions and a repository's

The harness's own instructions, its skills, step files and output style, and a
repository's constitution are separate documents. `/meow-flow:init` writes a
repository's `CLAUDE.md` from the constitution template and what the
repository holds, and copies no step, rule or template of the method into it
(REQ-2740). The template carries a role, a short project line, the principles
and the gate, and each principle in it states the rule, its reason and the
check that holds it where one exists.

### Rules that pull against each other

For each decision that adds a rule to the constitution, the design step asks
whether the rule pulls against one already there. Two that do become one rule
with its exception stated, written in the same decision (REQ-2738).

## Failure paths

| Condition                                    | What happens                                                          |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `CLAUDE.md` over 200 lines                   | `paw check` prints the advice line and keeps its exit status          |
| No `CLAUDE.md` at the root                   | `paw check` says nothing about the constitution                       |
| `CLAUDE.md` can't be read                    | `paw check` prints that it couldn't count the constitution, exit kept |
| A decision's rule pulls against one in force | The design step merges the two into one rule with its exception       |
