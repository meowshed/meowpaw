---
id: TSK-1690
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1200
closes:
  [
    REQ-1726,
    REQ-1734,
    REQ-1744,
    REQ-1746,
    REQ-1748,
    REQ-1750,
    REQ-1752,
    REQ-1754,
    REQ-1756,
    REQ-1758,
    REQ-1762,
    REQ-1766,
  ]
issue: 272
---

# Record the evidence for the attributes that already hold

Record the evidence for the attributes that already hold, as ADR-1200 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given each requirement this task closes, when its evidence is gathered at the current revision, then the task records a command and its output, or the file and line, that shows it holds. Closed by: the evidence table.

## What to do

Add a rule to the `method` skill separating what a report verified from what it assumed. For each other requirement this task closes, gather the evidence at the current revision and record it: the launchers' fallbacks, the drafts-only scope and the migrations, the kernel installed alone, the units' descriptions, the record's syntax, the gate run locally, the stub runs, the tools in `mise.toml`, and the absence of any spend without a person.

## Depends on

Nothing. ADR-1200 is approved.

## Evidence

Gathered at the revision this task's change lands on. REQ-1762 didn't hold:
the gate runs `python3` and `cargo`, and `mise.toml` declared neither, so both
were assumed present on the machine. This change declares `python = "3.14"`
and `rust = "1.98"`, the versions the gate was last run on, and the gate
passes with them, exit 0.

| Requirement | Evidence                                                                                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REQ-1726    | Each optional unit's launcher falls back alone where its binary is missing: `meow-git` prints `unrun ... nothing was checked` and exits 0, so no commit is refused; `meow-scm` and `meow-verbs` report `unchecked` and exit 3, which a step reads as unresolved and never as a failure of the step. `plugins/meow-method/bin/meow-method` exits 0 silently at the start of a session. |
| REQ-1734    | M10 in `plugins/meow-method/skills/method/SKILL.md` separates what a report verified from what it assumed. The output style's R7 keeps every real hedge. Whether the model follows M10 waits for evaluation.                                                                                                                                                                          |
| REQ-1744    | A frozen record keeps the rules it was approved under: `lib/layout.toml` scopes each rule added later to `draft_rules`, so no later version rejects an older record. `check frozen --base origin/main` reports: frozen: 0 findings                                                                                                                                                    |
| REQ-1746    | Each shape change so far came with its migration in the same change: the task's `## Acceptance criteria` and the epics' marks were added as draft rules, and the generated index blocks were written into both indexes by `index --write` in the change that introduced them (ADR-1140, ADR-1180).                                                                                    |
| REQ-1748    | `python3 tools/check_kernel.py` reports `4 kernel files, 0 names outside the kernel`: the kernel names no unit outside it, so it works installed alone.                                                                                                                                                                                                                               |
| REQ-1750    | Each unit's description states its job in one or two sentences, in words: `meow-core` 41, `meow-git` 32, `meow-method` 46, `meow-prose-gate` 51, `meow-prose` 54, `meow-scm` 35, `meow-verbs` 31.                                                                                                                                                                                     |
| REQ-1752    | `git grep -cE '^(:::\|{%\|{{<)' -- project` finds 0 files: the record uses no directive or custom syntax, only Markdown and YAML front matter.                                                                                                                                                                                                                                        |
| REQ-1754    | CI's gate job runs `mise run all`, the command a contributor runs locally, and `mise.toml` declares every tool it needs.                                                                                                                                                                                                                                                              |
| REQ-1756    | The attribution check matches the trailer, not the word: `fix: touch plugins/meow-core/` gives 0 matches and `Co-Authored-By: Claude` gives 1.                                                                                                                                                                                                                                        |
| REQ-1758    | The unit's fixtures report `Ran 83 tests in 5.333s` and pass, and against a program that returns nothing they report `FAILED (failures=80, errors=3)`.                                                                                                                                                                                                                                |
| REQ-1762    | `mise.toml` declares `markdownlint-cli2`, `prettier`, `python` and `rust`, every tool the gate runs, as of this change.                                                                                                                                                                                                                                                               |
| REQ-1766    | No workflow invokes a model: a search of `.github/workflows` for a `claude` command finds 0. The prose gate's hooks each name one model and a 60-second timeout and fire only on a tool call in a session, and `mise run eval`, which costs money, is outside `all`: `depends = ["fmt-check", "lint", "style", "prompts", "kernel", "budget", "crate"]`.                              |

## Left alone

REQ-1738, REQ-1759 and REQ-1764, which ADR-1200 leaves.
