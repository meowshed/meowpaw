---
id: SPC-1130
artifact: spec
status: live
revised: 2026-09-27
checked-at:
states:
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
---

# The coding unit

## Scope

This covers `meow-code`, the practice-layer unit that carries how the harness
changes code and how it writes a check. It leaves which tool serves which
language to packs, and running the checks to `meow-verbs`.

ADR-1420 decides this part.

## Boundary

| Surface                                    | What it is                                            |
| ------------------------------------------ | ----------------------------------------------------- |
| `plugins/meow-code/skills/change/SKILL.md` | The skill, loaded before code is changed              |
| `plugins/meow-code/README.md`              | The unit's page                                       |
| `plugins/meow-code/budget.toml`            | The characters the unit keeps in context on each turn |

## Behaviour

### When the skill loads

`meow-code:change` loads before Claude Code changes code, by a description
stating that obligation. It names no language, tool or file extension.

### How code is changed

The model makes the smallest change that is correct, and never reformats while
it changes behaviour (REQ-0090, REQ-0098). It reads a file before writing to
it (REQ-0092). A question about a symbol goes to a language server where the
session offers one, and an answer from a text search states what the search
can't cover (REQ-0094, REQ-0096). A symbol is edited semantically, a
mechanical rewrite structurally and a literal textually, and a change one
structural edit can make is made as one (REQ-2010, REQ-2012). Reads and edits
that don't depend on each other are batched (REQ-2014). After an edit the
model reads the file's diagnostics before claiming anything about it, and its
evidence comes from the verification verbs, never from diagnostics (REQ-2016,
REQ-2018). Every publicly reachable declaration carries documentation, and an
example the language runs as a check is preferred where it runs them
(REQ-1010, REQ-1015).

### How a check is written

An obligation is checked statically where it can be, behaviourally where it
can't, and by evaluation only where neither can (REQ-2076). A check is seen to
fail before the work that makes it pass, where the language and its tooling
allow (REQ-2072). A weak or tautological assertion is reported as a defect in
the check, and a check that wouldn't fail if its requirement were violated is
rewritten, not supplemented (REQ-2070, REQ-2078). Where the repository runs
mutation testing, the model runs it when asked whether the checks would catch
a change and reports the survivors, and where it doesn't, says none is
available (REQ-2074).

## Failure paths

| Failure                               | What happens                                                         |
| ------------------------------------- | -------------------------------------------------------------------- |
| No language server in the session     | The answer comes from a text search, stating what it can't cover     |
| No mutation testing in the repository | The model says none is available and runs nothing in its place       |
| A verb the change needs is unresolved | `meow-verbs` reports it unresolved, and the change isn't called done |
