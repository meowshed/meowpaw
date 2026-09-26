---
id: ADR-1130
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0190,
    REQ-0192,
    REQ-0194,
    REQ-0196,
    REQ-0198,
    REQ-0200,
    REQ-0202,
    REQ-0204,
    REQ-0206,
    REQ-0208,
    REQ-0210,
    REQ-0212,
    REQ-0228,
    REQ-0240,
    REQ-0294,
    REQ-0302,
    REQ-0321,
    REQ-0526,
    REQ-0528,
    REQ-0532,
    REQ-2630,
    REQ-2632,
  ]
supersedes: []
---

# 1130. The chain runs as steps that a program gates

## Decision

`meow-method` carries the method's nine steps: research, requirements, design,
spec, epic, implement, document, verify and review. One skill, `method`, holds
what every step shares and a file per step that the model reads only for the
step it runs, and a person or the model invokes a step by naming it. One more
skill, `/meow-method:run`, drives the chain: it asks the program where the
record stands, runs the next step, and stops at the next approval gate.

Whether a step may run is a fact about the record, so the program settles it
and the prose doesn't. `meow record` gains three subcommands:

- `status` prints the chain's state computed from the record, leading with
  every artifact that waits for approval, then each authorising record with
  the step it has reached and the step that comes next.
- `ready <step> <id>...` exits 0 when the step's input exists and is approved,
  and 1 naming each input that is missing or unapproved.
- `template <kind>` prints the path of the template in force for a kind: the
  repository's `.meowpaw/templates/<kind>.md` where it has one, and the unit's
  own otherwise.

A step runs `ready` before it writes anything and refuses on exit 1, saying
what is missing. Each step writes one artifact from its template, names the
artifact and the step that picks it up, and never performs a later step. Every
step reads the repository's principles, `CLAUDE.md` and whatever the profile
names, before it produces anything. Clarifying questions are capped at three
per step and self-review at two rounds, and both caps are stated in the skill.

The templates move from the repository's `templates/` into
`plugins/meow-method/templates/`, where the unit that owns them ships them.

After this decision a person can run any step on its own or run
`/meow-method:run` to be taken to the next gate, and a step with a missing
input refuses where it used to depend on the model noticing. What still
doesn't work: the steps carry the method's order and gates but only a short
statement of each artifact's content rules, which later decisions state in
full, and nothing measures whether the skill routes, because evaluation is
postponed.

## Why

RES-0064 found that one command driving the chain has to stop at every gate
exactly as the step would, resume from state because it remembers nothing of
its own run, and say it is waiting when run again with no approval. All three
follow from computing the state from the record every time, which a program
does the same way twice and a model doesn't. REQ-2694 asks that a rule a
program can settle be a check, and "is this step's input approved" is such a
rule.

RES-0052 found the chain's order carries weight: research before requirements,
requirements before design. `ready` holds that order, because it refuses a
design over unapproved requirements whatever the prose says. RES-0151 found
the tireless asker and the uncapped self-review loop are the step's usual
failures, so the caps are stated numbers. RES-0012 found that a template ships
with the unit that owns it and a repository overrides it with a file of its
own.

One skill with a file per step, and not nine skills, because each skill's
description costs context on every turn and the steps share their rules. The
driver is a command a person types, so it isn't offered to the model on every
turn either.

## Alternatives

| Option                                           | Better at                                        | Why it lost                                                                                     |
| ------------------------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| One skill, a file per step, the program gating   | One description per turn; a gate a program holds | Chosen                                                                                          |
| Nine skills, one per step                        | Each step routed by its own description          | Nine descriptions on every turn, and the shared rules copied nine times                         |
| The gates stated in the prose only               | No program to build                              | A model skips a gate it was told about; REQ-2694 asks for a check where a program can settle it |
| A hook that blocks writing a record out of order | Enforced even when the skill isn't loaded        | A hook can't tell which step a write belongs to, and would refuse ordinary edits                |
| Do nothing: the constitution names the order     | Costs nothing                                    | The order holds in this repository by discipline alone, and in no other                         |

## What it costs

Three subcommands and their fixtures in the crate, one skill with nine step
files, a command, and the templates moved. The templates' citations of the old
requirement scheme, `R-H-058` and its kind, are corrected in the move.

## What would reverse it

- A step's input turns out to be a judgement the program can't make, and
  `ready` refuses work a person would let through.
- The platform starts running a skill's steps with gates of its own, and the
  driver duplicates them.

## Consequences

- `meow record status`, `ready` and `template` exist with fixtures, and the
  `test` verb runs them.
- `plugins/meow-method/skills/method/` holds `SKILL.md` and `steps/<step>.md`,
  and `plugins/meow-method/skills/run/SKILL.md` holds the driver.
- `templates/` at the repository's root is gone, and `CLAUDE.md` says where the
  templates are.
- This repository drives its next increment through `/meow-method:run`.

## How I will know it was realised

1. `meow-method ready design REQ-xxxx` exits 1 naming a draft requirement, and
   0 once it is approved.
2. `meow-method status` on this repository leads with the drafts awaiting
   approval, and then shows each decision's step and the next one.
3. Run twice with no approval between, `status` prints the same state, and the
   driver says it is waiting.
4. `meow-method template task` prints `.meowpaw/templates/task.md` where that
   file exists, and the unit's template otherwise.
5. The next increment's decision in this repository is written through the
   `method` skill's design step.

## What this does not settle

- The full content rules for each artifact, which later decisions state.
- Classifying work so that trivial work skips the chain.
- Measuring whether the `method` skill routes on its description.
