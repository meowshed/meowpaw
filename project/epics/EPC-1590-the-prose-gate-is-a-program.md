---
id: EPC-1590
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1600
checked-at:
---

# The prose gate is a program, and it blocks only on a span it found in the command

Realises exactly one authorising record, ADR-1600. The epic is complete when
the prose gate runs as a program with no model and blocks only on a span it
quoted from the command. It carries no task of its own: the fix landed as
TSK-2470, which BUG-1230 carries, in #600, before any epic realised the
decision. So `paw status` reported ADR-1600 as waiting for an epic although
its work had merged. This epic records that realisation and adds no
implementation; its verification checks REQ-3182 again, as criterion 5 says.

## Acceptance criteria

Taken from ADR-1600, from its list of how I will know it was realised:

1. The four texts BUG-1230 records pass the gate, each as a fixture, and a
   text with an idiom, one with a bold-only line and one hiding behind
   `--body-file` are each blocked with a span found verbatim in the command.
2. `hooks/hooks.json` holds no hook of type `prompt`.
3. Every fixture runs the unit's launcher, so the gate a repository installs is
   what the fixtures check.
4. REQ-1756, REQ-3183, REQ-3187 and REQ-2076 are each closed by a task, named
   under Not covered.
5. REQ-3182 is verified against the program gate: a fixture shows a text held
   before it is published for each command the gate reads, a commit message
   through `-m`, and an issue, a pull request and a release body through
   `--body`, `--body-file`, `--notes` and `--notes-file`. The squash message a
   merge writes isn't read, so REQ-3182 is met in part, and the verification
   says so.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

None. TSK-2470 realised the decision, and it stays BUG-1230's task, because a
task names one authorising record and a defect may carry its own (REQ-0354).
Its evidence, in pull request #600: 19 fixtures seen failing first in the
commit that held them alone, and passing after.

## Coverage

ADR-1600 addresses five requirements, and this epic carries no task, because
the work landed before the epic existed. Each is named under Not covered with
the task that closed it.

The smallest set of tasks that tests the decision is TSK-2470 alone.

## Not covered

- REQ-1756, REQ-3183 and REQ-3187 are closed by TSK-2470, which BUG-1230
  carries and which landed in #600.
- REQ-2076 was closed and verified before ADR-1600, by TSK-2150 in EPC-1400.
  It is static, and the decision to use a program meets it by that choice.
- REQ-3182 was closed and verified before ADR-1600, by TSK-1140 in EPC-1010,
  but that evidence measured the prompt hook ADR-1600 removed. No task closes
  it against the program gate, so the epic's verification checks it again, as
  criterion 5 says, and it is met in part.
- What ADR-1600 leaves unsettled stays unsettled here, including: the squash
  message a merge writes from its `--subject` and `--body`; an inflected idiom
  such as `circling back`; a message passed through a variable; a match across
  a quote boundary; a bold fragment followed by text; whether other rules join
  the gate; and how `tools/measure_gate.py` and SPC-1020 apply now.
- A limit the decision accepts, not an open question: on a machine with no
  binary, the launcher reports that nothing was checked and lets the command
  run.

## Open review findings

- A reason for the marking rule's "never in a later pass", and for the `[P]`
  rule. Left: both are the template's text, and CLAUDE.md states the reason in
  the principle artifacts_stay_current.
