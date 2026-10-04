---
id: TSK-2070
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1360
closes:
  [
    REQ-0287,
    REQ-0289,
    REQ-1950,
    REQ-1952,
    REQ-1954,
    REQ-1956,
    REQ-1958,
    REQ-1960,
    REQ-1962,
    REQ-1964,
    REQ-2836,
  ]
issue: 428
projected: 52111e261d21
---

# The document step carries its obligations on a repository's documentation

The document step's file carries, as labelled rules, each obligation ADR-1380
names on a repository's documentation, and this repository declares its
documentation style. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `steps/document.md`, when it is read, then each requirement this task
   closes is carried by a labelled rule, and no rule names a requirement, a
   language or a tool. Closed by: a table in the evidence tracing each
   requirement to its rule, and a search for identifiers in the file.
2. Given the step files, when `mise run prompts` runs, then it passes. Closed
   by: its output.
3. Given `.meowpaw/profile.toml`, when it is read, then it declares
   `[docs] style`, and `meow-verbs status` still resolves every verb it did.
   Closed by: the file and the command's output.

## What to do

Add the nine rules ADR-1380 lists to `steps/document.md`, each with its
reason in the same sentence, and extend the step's numbered steps where a
rule changes what the step does first: naming the kind, reading the declared
style, and running the verbs after editing. Declare `[docs] style =
"meow-prose"` in this repository's profile, and say in `meow-method`'s page
that the step reads it. The unit's version moves by a minor for the new
behaviour, and every page describing it is restamped.

## Depends on

Nothing. ADR-1380 is approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in
`steps/document.md`, and the step's numbered steps read the declared style,
name the kind first, and run the examples and the verbs after editing. No rule
names a requirement, a language or a tool: a search of the file for record
identifiers finds 0.

| Requirement | Carried by              |
| ----------- | ----------------------- |
| REQ-0287    | O12 and O13, and step 4 |
| REQ-0289    | O12                     |
| REQ-1950    | O4, and step 2          |
| REQ-1952    | O5                      |
| REQ-1954    | O6                      |
| REQ-1956    | O9                      |
| REQ-1958    | O7                      |
| REQ-1960    | O8                      |
| REQ-1962    | O10, and step 1         |
| REQ-1964    | O11                     |
| REQ-2836    | O13, and step 4         |

This repository declares `[docs] style = "meow-prose"` in its profile, and
`meow-verbs status` still resolves the three verbs it did, listing `[docs]`
among the tables it doesn't read. `meow-method`'s page says the step reads the
declaration, and the unit moves to 0.31.0 for the new behaviour, with its
pages restamped.

```text
$ python3 tools/check_prompts.py
52 shipped prompts, 0 failures
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

## Left alone

The review step, which TSK-2080 changes.
