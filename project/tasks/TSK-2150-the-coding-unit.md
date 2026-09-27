---
id: TSK-2150
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1400
closes:
  [
    REQ-0090,
    REQ-0092,
    REQ-0094,
    REQ-0096,
    REQ-0098,
    REQ-1010,
    REQ-1015,
    REQ-2010,
    REQ-2012,
    REQ-2014,
    REQ-2016,
    REQ-2018,
    REQ-2070,
    REQ-2072,
    REQ-2074,
    REQ-2076,
    REQ-2078,
  ]
issue: 461
projected: d55b539153c1
---

# `meow-code` ships the skill that holds how code is changed and checked

A new unit, `meow-code`, ships `meow-code:change`, whose rules carry each
obligation ADR-1420 lists, loaded before Claude Code changes code. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given the skill, when it is read, then a labelled rule carries each
   requirement this task closes, and no rule names a requirement, a language,
   a tool or a file extension. Closed by: a table in the evidence tracing each
   requirement to its rule, and a search of the file.
2. Given the unit, when `mise run prompts` and `mise run budget` run, then
   both pass. Closed by: their output.
3. Given a scratch repository and a session on each of Sonnet 5 and Opus 5.5
   with only the unit installed, when Claude Code is asked to change a function, then it loads
   the skill before its first edit. Closed by: the session's transcript.

## What to do

Create `plugins/meow-code/` with a manifest, a page, a budget and a
`requires.toml`, and the skill with a description stating the obligation, as
ADR-1050 decides. Write the two groups of rules ADR-1420 lists, each with its
reason in the same sentence. Add the unit to the catalogue.

## Depends on

Nothing. ADR-1420 is approved.

## Evidence

`plugins/meow-code/` holds the unit at 0.1.0 with its skill, page, manifest,
budget and `requires.toml`, and joins the catalogue; `claude plugin validate`
passes on both. The skill carries eight rules on changing code and five on
writing a check, each with its reason, and a search of it finds no record
identifier, language, tool or file extension:

| Requirement | Carried by     |
| ----------- | -------------- |
| REQ-0090    | E1, and step 3 |
| REQ-0092    | E2, and step 1 |
| REQ-0094    | E3, and step 2 |
| REQ-0096    | E3             |
| REQ-0098    | E7             |
| REQ-1010    | E8             |
| REQ-1015    | E8             |
| REQ-2010    | E4, and step 3 |
| REQ-2012    | E4             |
| REQ-2014    | E5, and step 1 |
| REQ-2016    | E6, and step 4 |
| REQ-2018    | E6, and step 5 |
| REQ-2070    | C3             |
| REQ-2072    | C2, and step 5 |
| REQ-2074    | C5             |
| REQ-2076    | C1             |
| REQ-2078    | C4             |

`check_prompts.py` passes on 54 prompts, and `check_budget.py` measures the
description at 233 characters against a ceiling of 330.

In a scratch repository, one session on each model, with only this copy of
the unit installed, was asked to change a function. Each loaded the skill
before any other tool:

```text
claude-sonnet-5: Skill(meow-code:change) -> Read -> Edit
claude-opus-5-5: Skill(meow-code:change) -> Read -> Bash(check expecting "hi") -> Edit -> Bash(the same check)
```

One run per model shows the skill routes; it isn't a measurement of how
reliably the rules hold.

## Left alone

Evaluation cases for the unit, which a later measurement adds.
