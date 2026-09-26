---
id: TSK-1580
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0303,
    REQ-0534,
    REQ-0535,
    REQ-0536,
    REQ-0537,
    REQ-2900,
    REQ-2902,
    REQ-2910,
    REQ-2916,
    REQ-2917,
    REQ-2918,
    REQ-2919,
    REQ-2920,
    REQ-2922,
    REQ-2926,
  ]
issue: 228
---

# The task and defect templates carry their obligations

One task, one branch, one pull request, one review.

## What to do

Give the `task` template an `## Acceptance criteria` section whose criteria are each a starting state, an action and an observable outcome with the evidence that will close it, and add it to the task kind's `draft_sections` in `lib/layout.toml`. Give the `bug` template the environment and versions, the revision observed at, sanitised evidence, the violated requirement or a statement that none exists, the reason for the severity, and a fix that is a task of its own. Give every template an opening that lets a reader stop, sections that permit an empty answer that is earned, and the relation naming what it elaborates. Map each requirement to the template line that carries it under Evidence.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by the template line named, and
the task kind's `draft_sections` holds a draft task to its acceptance
criteria:

| Requirement | Carried by                                                                                                                              |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| REQ-0303    | `task.md`: the `## Acceptance criteria` section, and the task kind's `draft_sections`                                                   |
| REQ-0534    | Every template opens with a paragraph or section that lets a reader stop, as `README.md` states, and `task.md` and `bug.md` gain theirs |
| REQ-0535    | `README.md`: "A section may be answered 'Nothing', with the reason"                                                                     |
| REQ-0536    | Each template's upward relation: `elaborates`, `addresses`, `realises`, `epic` and `violates`                                           |
| REQ-0537    | `README.md`: "an answer has to be earned, because a padded section reads as a claim"                                                    |
| REQ-2900    | `task.md`: each criterion "Given a starting state, when an action, then an observable outcome"                                          |
| REQ-2902    | `task.md`: "Closed by: the evidence that will show it" under each criterion                                                             |
| REQ-2910    | `bug.md`: "One defect ... a second defect is a second record"                                                                           |
| REQ-2916    | `bug.md`: "The environment and the versions, exactly"                                                                                   |
| REQ-2917    | `bug.md`: "the revision it was seen at"                                                                                                 |
| REQ-2918    | `bug.md`: "What happened, exactly, with the evidence"                                                                                   |
| REQ-2919    | `bug.md`: "Strip secrets and personal data from it first"                                                                               |
| REQ-2920    | `bug.md`: "the requirement it violates, cited in `violates`. Where none exists, say so"                                                 |
| REQ-2922    | `bug.md`: "why it has the severity it has"                                                                                              |
| REQ-2926    | `bug.md`: "The fix is a task of its own, or a change reviewed on its own"                                                               |

`test_a_draft_task_carries_acceptance_criteria` shows an approved task passing
`shape` without the section and a draft failing, and the unit's fixtures run
`OK`.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
