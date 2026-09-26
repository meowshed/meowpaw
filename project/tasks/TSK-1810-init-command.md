---
id: TSK-1810
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1250
closes: [REQ-1560, REQ-1563]
issue: 319
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

`templates/profile.toml` holds the sections `[verbs]`, `[commits]`, `[git]`,
`[record]` and `[prose]`, each value commented out with what fills it, so the
file parses before and after init fills it. `meow-method template profile`
prints its path, and a repository's own `.meowpaw/templates/profile.toml` wins
as every template does. A fixture reads the template and finds each section
and none of fifteen language, tool and extension names; it fails against a
stub that returns nothing.

`skills/init/SKILL.md` carries `disable-model-invocation: true`, found
1 time, so only a person starts it. Its rule N1 names the two files it
writes, `.meowpaw/profile.toml` and a missing `CLAUDE.md`, and forbids
everything else REQ-1563 lists. The prompt check passes it in the gate.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 106 tests in 6.792s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=103, errors=3)
```

## Left alone

Onboarding from existing documents, which ADR-1250 leaves to the next
decision.
