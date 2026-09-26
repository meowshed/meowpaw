---
id: TSK-1730
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1220
closes: [REQ-0568, REQ-0569, REQ-0571, REQ-0574, REQ-0576]
issue: 291
---

# The record keeps an insight, its shape checked

The record keeps an insight, its shape checked, as ADR-1220 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an insight whose title carries a date or runs under four words, when `check rules` runs, then it reports the title. Closed by: a fixture.
2. Given an insight whose Evidence section holds no digit and no fenced block, when `check rules` runs, then it reports the section. Closed by: a fixture.
3. Given an insight whose last section isn't The pattern, when `check rules` runs, then it reports it. Closed by: a fixture.
4. Given an empty record, when `new insight` and `template insight` run, then they print `INS-0001` and the template. Closed by: a fixture.

## What to do

Add the kind `insight` to `lib/layout.toml`: prefix `INS`, directory `insights`, the record statuses, sections Evidence, What looked right and The pattern, and the rules `title-states-claim`, `evidence-measured` and `ends-with-pattern`, which the program implements. Write `templates/insight.md` and list it in the templates' index, add it to the templates `template` knows, and name the kind in `CLAUDE.md`'s layout.

## Depends on

Nothing. ADR-1220 is approved.

## Evidence

Not yet.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
