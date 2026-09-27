---
id: SPC-1130
artifact: spec
status: live
revised: 2026-09-27
checked-at: "#464"
states:
  [
    REQ-0090,
    REQ-0092,
    REQ-0094,
    REQ-0096,
    REQ-0098,
    REQ-1010,
    REQ-1015,
    REQ-1890,
    REQ-1892,
    REQ-1894,
    REQ-1896,
    REQ-1898,
    REQ-1900,
    REQ-1902,
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
changes code, writes a check and debugs a defect. It leaves which tool serves
which language to packs, and running the checks to `meow-verbs`.

ADR-1420 and ADR-1430 decide this part.

## Boundary

| Surface                                    | What it is                                               |
| ------------------------------------------ | -------------------------------------------------------- |
| `plugins/meow-code/skills/change/SKILL.md` | The skill, loaded before code is changed                 |
| `plugins/meow-code/skills/debug/SKILL.md`  | The skill, loaded before the cause of a defect is sought |
| `plugins/meow-code/README.md`              | The unit's page                                          |
| `plugins/meow-code/budget.toml`            | The characters the unit keeps in context on each turn    |

## Behaviour

### When the skills load

`meow-code:change` loads before the model changes code, by a description
stating that the skill must load before any code changes.
`meow-code:debug` loads before the model looks for the cause of a defect, by a
description stating that. Neither skill names a language, a tool or a file
extension.

### How code is changed

The model makes the smallest change that is correct, and never reformats while
it changes behaviour (REQ-0090, REQ-0098). It reads a file before writing to it
(REQ-0092). A question about a symbol goes to a language server where the
session offers one, and an answer from a text search states what the search
can't cover (REQ-0094, REQ-0096). The model prefers a semantic edit for a
symbol, a structural edit for a mechanical rewrite and a textual edit only for
a literal, and makes a change one structural edit can express as that one edit
(REQ-2010, REQ-2012). Reads and edits that don't depend on each other are
batched (REQ-2014). After an edit the model reads the file's diagnostics before
claiming anything about it, and its evidence comes from the verification verbs,
never from diagnostics (REQ-2016, REQ-2018). Every publicly reachable
declaration carries documentation, and an example the language runs as a check
is preferred where it runs them (REQ-1010, REQ-1015).

### How a check is written

The model checks an obligation statically where it can, behaviourally where
it can't, and by evaluation only where neither can (REQ-2076). It sees a check
fail before the work that makes it pass, where the language and the pack
support it (REQ-2072). It reports a weak or tautological assertion as a defect
in the check, and rewrites a check that wouldn't fail if its requirement were
violated, never adding a second one beside it (REQ-2070, REQ-2078). Where the
ecosystem provides mutation testing, it runs the tool the repository or a pack
names when asked whether the checks would catch a change, and reports the
survivors. Where nothing names a tool, it says how to declare one and runs
nothing in its place (REQ-2074).

### How a defect is debugged

`meow-code:debug` loads before the model looks for the cause of a defect. The
model reproduces the defect first, as small as it can make it, and keeps the
reproduction (REQ-1890). It records what the system actually does before it
offers a cause (REQ-1892). It holds one falsifiable hypothesis at a time and
tests it by trying to refute it (REQ-1894), and bisects once the hypotheses run
out (REQ-1896). The evidence that closes the defect is the reproduction failing
before the change and passing after it (REQ-1898). The model fixes the cause,
and says so where it treated only the symptom (REQ-1900). Where the defect
shows a requirement to be wrong, the model routes the defect through an
amendment and patches nothing (REQ-1902).

## Failure paths

| Failure                           | What happens                                                     |
| --------------------------------- | ---------------------------------------------------------------- |
| No language server in the session | The answer comes from a text search, stating what it can't cover |
| No mutation tool named            | The model says how to declare one and runs nothing in its place  |
