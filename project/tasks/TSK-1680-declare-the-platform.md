---
id: TSK-1680
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1200
closes: [REQ-1736, REQ-1740, REQ-1742]
issue: 271
---

# Each unit declares the platform it needs and the behaviours it relies on

Each unit declares the platform it needs and the behaviours it relies on, as ADR-1200 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given every unit, when its directory is listed, then it holds a `requires.toml` naming a Claude Code version. Closed by: a listing.
2. Given every unit's page, when it is read, then it names the behaviours the unit relies on and where each is documented. Closed by: a search of the pages.

## What to do

Give each unit a `requires.toml` with `claude_code = "2.1.283"`, the version its units were tested on, and a comment saying so. Add a line to each unit's documentation page naming the Claude Code version and the platform behaviours the unit relies on, each with the documentation page that states it.

## Depends on

Nothing. ADR-1200 is approved.

## Evidence

Each of the 7 units carries `requires.toml` naming Claude Code 2.1.283, the
version its behaviour was last tested on, with a comment saying why the unit
states it there: the plugin manifest reference, read on 2026-09-26, has no
field for a minimum platform version. Each unit's page gains "What it needs",
naming the version and the platform behaviours it relies on, each linked to
Claude Code's documentation of it:

| Unit              | Behaviours it relies on                                                                                                                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `meow-core`       | an output style with `force-for-plugin`, which applies the reply shape to every reply                                                                                                                                           |
| `meow-prose`      | a skill loaded by its description; a subordinate agent, the reviewer                                                                                                                                                            |
| `meow-prose-gate` | a `PreToolUse` hook of type `prompt`, with a `model` field                                                                                                                                                                      |
| `meow-verbs`      | a skill loaded by its description; a plugin's `bin/` programs, run by path                                                                                                                                                      |
| `meow-scm`        | a skill loaded by its description; a plugin's `bin/` programs, run by path                                                                                                                                                      |
| `meow-git`        | `PreToolUse` command hooks filtered by an `if` rule, which Claude Code applies as a best-effort filter                                                                                                                          |
| `meow-method`     | a skill loaded by its description, and one only a person invokes, with `disable-model-invocation`; a `SessionStart` command hook whose output reaches the model before its first reply; a plugin's `bin/` programs, run by path |

```text
$ ls plugins/*/requires.toml | wc -l
7
$ grep -l '^## What it needs' docs/meow-*.md | wc -l
7
```

## Left alone

REQ-1738, REQ-1759 and REQ-1764, which ADR-1200 leaves.
