---
id: TSK-3130
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1800
closes: [REQ-0083]
issue:
---

# Write the Markdown skill and `reviewing.md`

The skill tells the model what ADR-1900 orders it to, in RES-0111's order, and
`reviewing.md` carries the six points a Markdown reviewer checks that no
command reports, loaded when Markdown is reviewed, as SPC-1195 states. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `reviewing.md`, when a test reads it, then it finds each of RES-0111's
   six reviewer points: the heading outline as the argument, a table against a
   list, the language tag on a fence, reference links for a source cited more
   than twice, links that survive a move, and a diagram claiming what the
   prose doesn't. Closed by: a fixture naming REQ-0083, seen failing first.
2. Given the skill, when a test reads it, then it names `reviewing.md` as the
   file to load on review, forbids markdownlint-cli against a
   `.markdownlint-cli2.*` file, failing a check on an unreachable link without
   saying so, and a spell check with no project word list, names `meow-prose`
   as the owner of the writing standard, and names the tool versions from
   RES-0294. Closed by: a fixture.
3. Given the skill, when `mise run prompts` and `mise run budget` run, then
   both pass, and the skill's per-turn load stays within the unit's
   `budget.toml`. Closed by: the gate, exit status 0.
4. Given the skill's order and wording, when a reviewer reads it against
   RES-0111's order, then it follows that order. Closed by: judgement, by the
   pull request's reviewer, because the order of a prompt's sections is read,
   not matched.

## What to do

Write the skill's body and `reviewing.md` under
`plugins/meow-markdown/skills/markdown/`, to the prompt vocabulary
`meow-author:write` sets, carrying what the skill knows of front matter,
admonitions and diagram blocks for the seven known render targets. Raise
`meow-markdown`'s minor version.

## Depends on

TSK-3100, because the unit and its skill file come from it.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

The program's commands, which TSK-3100, TSK-3110 and TSK-3120 take. The
writing standard, which stays in `meow-prose`.
