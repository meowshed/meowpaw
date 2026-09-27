---
id: ADR-1430
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [REQ-1890, REQ-1892, REQ-1894, REQ-1896, REQ-1898, REQ-1900, REQ-1902]
supersedes: []
---

# 1430. A debugging skill reproduces first and tests one hypothesis at a time

## Decision

`meow-code` ships a second skill, `meow-code:debug`, which loads before the
model looks for the cause of a defect. It carries these rules as labelled
rules, and names no language or tool:

- reproduce the defect first, as small as it can be made, and keep the
  reproduction (REQ-1890);
- record what the system actually does before offering a cause (REQ-1892);
- hold one falsifiable hypothesis at a time, and test it by trying to refute
  it (REQ-1894);
- bisect once the hypotheses run out, and stop guessing (REQ-1896);
- close the defect with the reproduction seen failing before the change and
  passing after it (REQ-1898);
- fix the cause, and say so where only the symptom was treated (REQ-1900);
- where the defect shows a requirement to be wrong, route it through an
  amendment and patch nothing (REQ-1902).

After this decision a model debugging in a repository with `meow-code`
installed reproduces before it theorises and closes a defect on evidence that
could have failed. What still doesn't work: no program checks that a
reproduction was kept or seen failing, so the rules rest on the model and on
review, and the method's own path for a defect, its triage and its record, is
a later decision.

## Why

The rules are RES-0015's conclusions on debugging, with REQ-1898 drawn also
from RES-0055 and RES-0021. A defect gets debugged whether or not the
repository keeps a record, so the rules sit in the practice layer beside how
code is changed, where `meow-code` already is (ADR-1420).

A second skill, not more rules in `meow-code:change`, because debugging is a
different activity with its own trigger: a skill loads by its description,
and one description can't name both "before any code changes" and "before
looking for a cause" without loading its whole body for either.

The strongest objection: every rule here is behavioural, and none can be
checked by a program, so a model under pressure skips them. A measurement of
debugging with the skill and without it is what settles that, and it comes
with the unit's evaluation cases.

## Alternatives

| Option                           | Better at                  | Why it lost                                                                                      |
| -------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------ |
| Do nothing                       | No skill to ship           | The model guesses a cause and patches it, which RES-0015 found is how a defect comes back        |
| More rules in `meow-code:change` | One skill, one description | Every edit would load the debugging rules, and a search for a cause that edits nothing wouldn't  |
| A new unit for debugging         | Installable alone          | Debugging without changing code is rare, and a second unit for one skill costs a catalogue entry |

## What it costs

The skill's description adds a few hundred characters in context on every
turn to `meow-code`, and its body loads when the model debugs.

## What would reverse it

I would reverse this if a measurement of debugging with the skill and without
it, on Sonnet 5 and Opus 5.5, scored the same, because that would show the
rules change nothing.

## Consequences

- `plugins/meow-code/skills/debug/SKILL.md` ships the rules, and the unit's
  ceiling rises to hold its description.
- SPC-1130 states the debugging rules.

## How I will know it was realised

1. Each requirement ADR-1430 addresses is carried by a labelled rule in the
   skill, traced in the task's evidence, and no rule names a requirement, a
   language or a tool.
2. The prompt check and the budget check pass on the unit.
3. Five sessions on each of Sonnet 5 and Opus 5.5, with only the unit
   installed and asked to find why a script prints the wrong value, load the
   debugging skill before their first edit in at least four of five.
4. Every requirement ADR-1430 addresses lands in exactly one closed task.

## What this does not settle

- The method's path for a defect: its triage, the step it enters at, and a
  defect's own tasks.
- Which tool bisects in which version control system, which belongs to a
  pack.
