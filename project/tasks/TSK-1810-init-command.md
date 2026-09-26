---
id: TSK-1810
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1250
closes: [REQ-1560, REQ-1563]
issue:
---

# The init command and the profile template

The init command and the profile template, as ADR-1250 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an empty repository, when `template profile` runs, then it prints the path of a template whose text names no language, build tool or package manager. Closed by: a fixture and a search.
2. Given the command, when its front matter is read, then it carries `disable-model-invocation: true` and its rules name the two files it writes. Closed by: a search.

## What to do

Write `templates/profile.toml`, naming no language, build tool or package manager, and add `profile` to the templates `template` knows and to the templates' index. Write `skills/init/SKILL.md`, a command with `disable-model-invocation`, which writes `.meowpaw/profile.toml` and, where none exists, `CLAUDE.md` from the constitution template, and nothing else.

## Depends on

Nothing. ADR-1250 is approved.

## Evidence

Not yet.

## Left alone

Onboarding from existing documents, which ADR-1250 leaves to the next
decision.
