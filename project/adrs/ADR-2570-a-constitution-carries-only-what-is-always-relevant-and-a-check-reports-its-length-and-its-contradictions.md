---
id: ADR-2570
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-2732,
    REQ-2734,
    REQ-2736,
    REQ-2738,
    REQ-2740,
    REQ-2742,
    REQ-2744,
    REQ-2745,
    REQ-2746,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2570. A constitution carries only what is always relevant, and a check reports its length and its contradictions

## Decision

A constitution carries what is always relevant, can't be checked and can't be
derived (REQ-2744). It carries no procedure, no language-specific material, no
explanation of the method and nothing the repository already shows
(REQ-2745). Each rule names a command, a path or a value, and not an
intention (REQ-2736). A rule that must hold every time names the check that
holds it, so the constitution is never its only carrier (REQ-2732). No rule
the harness ships depends on being read last, because several constitutions
load in an order the harness doesn't control (REQ-2742).

The harness's own instructions and a repository's constitution are separate
documents, and `/meow-flow:init` writes the repository's from what the
repository holds and copies none of the method into it (REQ-2740). The
template ADR-1250 decided already writes it that way.

`paw check` gains a constitution rule: it reports a constitution over 200
lines as a finding to cut, without failing the gate, because REQ-2734 states
a target and not a limit (REQ-2734). This repository's `CLAUDE.md` is 449
lines today, so the first run reports it, and cutting it is its own task. The
design step's file asks, for each decision that adds a rule, whether it pulls
against one already there, and two that do become one rule with its
exception stated (REQ-2738). A rule whose failure hasn't recurred in the
evidence of the last ten merged tasks is proposed for removal by the
constitution's next rewrite (REQ-2746).

Once this is accepted, a constitution has a length the gate reports and a
test for each rule it holds. What still doesn't work: whether a rule is
"always relevant" is a judgement, and review holds it.

## Why

RES-0204 found that a constitution which carries procedure grows until the
rules that matter drown, that one loaded with others can't rely on its
place in the order, and that a rule stated as an intention can't be
verified. The 200-line figure is the target REQ-2734 states.

## Alternatives

| Option                       | Better at                | Why it lost                                                           |
| ---------------------------- | ------------------------ | --------------------------------------------------------------------- |
| Do nothing                   | No new check             | CLAUDE.md keeps growing and nothing reports it                        |
| Fail the gate over 200 lines | The limit holds          | REQ-2734 states a target, and a hard limit cuts rules to fit a number |
| A constitution per unit      | Each unit owns its rules | Several constitutions are what REQ-2742 warns can't rely on order     |

## What it costs

The first run reports CLAUDE.md, and cutting it to about 200 lines means
moving procedure into skills and step files, which is a task of its own.

## What would reverse it

- The cut to 200 lines loses a rule whose failure then recurs, which would
  show the target is too tight for this repository.

## Consequences

`paw check` gains the length report. The design step's file gains the
contradiction question. A task cuts CLAUDE.md.

## How I will know it was realised

1. `paw check` reports a 449-line CLAUDE.md as over its target and exits 0
   for it (REQ-2734).
2. `/meow-flow:init` on a fixture repository writes a constitution with no
   step of the method in it (REQ-2740).
3. Each rule in CLAUDE.md that must hold names its check (REQ-2732).

## What this does not settle

- Which rules leave CLAUDE.md in the cut.
