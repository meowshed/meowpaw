---
id: ADR-1050
artifact: adr
status: approved
revised: 2026-09-23
addresses: [REQ-1144, REQ-1146, REQ-1148, REQ-1150]
supersedes: []
---

# 1050. A unit that must hold is loaded by a description stating the obligation

## Decision

A unit that has to be in context before the model acts is loaded by its
description, and the description states that obligation. It opens with a
sentence saying what the unit is, then says in the third person that the unit
MUST be loaded before the work (REQ-1144), which keeps the third person
REQ-1134 already requires. It names each verb a
request uses for that work and no work the unit does not govern (REQ-1146).
It closes by saying the unit MUST NOT be skipped however short or simple the
work looks (REQ-1148).

The writing skill's description becomes:

> The writing standard for all text. It MUST be loaded before any prose of any
> length is written, rewritten, reworded, edited or reviewed, including code
> comments, pull request and issue descriptions, commit messages, and Markdown
> files. It MUST NOT be skipped, however short or simple the text looks.

How often such a unit loads is measured on Sonnet 5 and Opus 5.5, on requests
that should load it and on near misses including answers in chat (REQ-1150).

This amends ADR-1020. `meow-prose` ships no `SessionStart` hook, and the
example description in ADR-1020 ("Holds the writing standard ... Use before
writing any of them") is replaced by the form above. The rest of ADR-1020
stands.

## Why

RES-0272 measured it. On Sonnet 5 the description above loaded the writing
skill in 36 of 36 writing runs and 0 of 39 near misses, where the description
ADR-1020 left in place loaded it in 0 of 30. A `SessionStart` hook naming the
skill was delivered as context and did not change what the model did, so the
reason ADR-1020 gave for the hook no longer holds.

ADR-1020 expected louder wording to over-trigger, following the guides. It did
not on Sonnet 5: across 882 near-miss runs of worded obligations, the skill
loaded once. On Opus 5.5 the description loaded the skill in 33 of 33 writing
runs, never on work that changes code, and on 8 of 12 runs that answer in chat
or fix a word in a README. Those count as prose here, because the reply shape
in `meow-core` loads the writing skill for replies with prose, so a chat answer
that loads it is the behaviour wanted.

## Alternatives

| Option                                              | Better at                                         | Why it lost                                                                           |
| --------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------- |
| A description stating the obligation, no hook       | Loading on writing requests and nowhere else      | Chosen                                                                                |
| The `SessionStart` hook ADR-1020 chose              | Placing the pointer in every session              | Delivered as context and ignored in 4 of 4 runs, and it costs a line in every session |
| The same obligation in the second person            | Reading as an order to the model                  | 24 of 60 writing runs against 45 of 53 in the third person                            |
| A long description cataloguing what the skill holds | Telling the model why the skill is worth loading  | 10 of 30 and 11 of 30 in two versions                                                 |
| The description ADR-1020 left in place              | Following the guides' advice on ordinary phrasing | 0 of 30 writing runs on Sonnet 5                                                      |
| Do nothing                                          | Costing nothing                                   | The standard would stay unloaded on Sonnet 5 for every text it governs                |

## What it costs

The description is 299 characters, listed in every session where `meow-prose`
is enabled, about the length of the hook's line it replaces. It stops being a
plain description of the unit and becomes an instruction, which the guides
advise against, so the measurement on both models is what keeps it honest.

Every wording change to such a description is a routing change, and has to be
measured again on both models before it ships.

## What would reverse it

- Z4 loads the writing skill on work that changes code in more than one run
  of ten, on either model. The obligation would then need a narrower form, or
  a description per model if the platform allows one.
- A later Sonnet release loads the skill below nine runs in ten with this
  description. The form would then be measured again from the candidates in
  RES-0272.
- The platform offers a way to load a skill without the model choosing it.
  The description could then go back to describing the unit.

## Consequences

- `plugins/meow-prose/skills/writing/SKILL.md` carries the description above,
  and `meow-prose` carries no `hooks/hooks.json`.
- REQ-1140 is withdrawn for REQ-1144, REQ-1146, REQ-1148 and REQ-1150.
- SPC-1030 states the form of such a description, and SPC-1010 drops the hook.
- EPC-1030 realises this decision. TSK-1240 in EPC-1020 keeps the
  third-person descriptions and drops the hook.

## How I will know it was realised

1. The writing skill loads in at least nine runs of ten on the writing
   requests RES-0272 lists, on Sonnet 5 and on Opus 5.5, with the published
   plugin installed.
2. On the same two models, the near misses that change code load it in no
   more than one run of ten. Answers in chat and edits to a Markdown file are
   prose, and loading on them is not a miss.
3. `meow-prose` ships no hook, and SPC-1010 and SPC-1030 name none.

## What this does not settle

- Whether the form holds for a unit other than the writing skill. The next
  unit that has to hold is measured before its description ships.
- Whether it holds in a long session with other work in context. Every run in
  RES-0272 started clean.
- Whether the skill's body does what it says once loaded, which TSK-1180
  measures.
