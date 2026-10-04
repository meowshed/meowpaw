---
id: ADR-1440
artifact: adr
status: done
revised: 2026-09-27
addresses:
  [
    REQ-0348,
    REQ-0350,
    REQ-0352,
    REQ-0354,
    REQ-0356,
    REQ-0358,
    REQ-0360,
    REQ-0362,
    REQ-0364,
    REQ-0368,
    REQ-0370,
    REQ-0372,
    REQ-0374,
    REQ-3170,
    REQ-3174,
  ]
supersedes: []
---

# 1440. A defect authorises work directly, and enters the chain where its triage says

## Decision

A defect record authorises work as a decision does (REQ-0352), and a defect
whose fix is one task needs no epic. A task names the record that authorises
it in exactly one of two fields: `epic: EPC-NNNN`, or `bug: BUG-NNNN`
(REQ-0354). A task a defect authorises closes no new requirement, because the
requirement it restores is already in force (REQ-0350), so its `closes` may
be empty. The defect then carries a `## Tasks` section with the same marks an
epic's has, and a task's state derives from the defect's mark as it does from
an epic's. An epic realises a defect only where the fix needs at least two
tasks with an order between them (REQ-0356).

A defect's path begins with reproduction (REQ-0348). Its record carries a
reproduction before it is triaged (REQ-0364), and its triage answers first
whether a requirement in force covers the behaviour (REQ-0358): `violates`
names that requirement, or the Triage section says none does. A new field,
`enters`, names the step the defect enters at, and the answer decides it
(REQ-0360): `implement` where the code fails a requirement in force, `design`
where the design is what fails it, `requirements` where the requirement itself
is wrong, which starts the amendment path, or where no requirement covers the
behaviour, and `research` where the cause is unknown. Severity stays a required
field (REQ-0372).

A research record, a requirement or a decision a defect prompted names it in
a new relation, `prompted-by: BUG-NNNN` (REQ-0362). A defect closed as not a
defect is stored `rejected`, and its Triage section records why (REQ-0370). A
closed defect's Closed by section names the check that closed it, which stays
as a regression check (REQ-0368). `paw status` reports how many tasks
decisions authorised and how many defects did (REQ-0374).

`paw check` holds the rules a program settles: a task naming neither `epic` nor
`bug`, or both; a draft defect whose Triage section is written and which names
no `enters`; a defect with `enters` at `implement` or `design` and no
`violates`; a defect with `enters` and an empty Reproduction; a rejected defect
with an empty Triage; a defect whose tasks are all done with an empty Closed
by; an epic realising a defect with fewer than two tasks or no order between
them; and a `prompted-by` naming no defect. Requiring `enters` is a draft rule,
so the defects approved before this decision keep the rules they were approved
under (ADR-1140). The other rules on `enters` apply wherever the field appears,
which is only in defects written after this decision.

The implement and verify step files carry the rules a program can't settle. The
implement step begins a defect's task by running its reproduction and seeing it
fail, and writes no defect record for a defect that a gate caught and the same
change closed (REQ-3174). The verify step closes an epic while a defect it
uncovered is still open only where that defect is recorded. Where the defect
contradicts an acceptance criterion, the step names both and says why closing
is right (REQ-3170).

After this decision a one-task fix costs a defect record and a task, with no
epic. The record says which step a defect enters at, and `paw status` shows how
much work defects authorise. What still doesn't work: whether a triage
answer is right is a judgement no program settles, so review holds it.

## Why

RES-0034 found every kind of work in both taxonomies it surveyed routing
through a decision or a defect, and RES-0033 found a defect differing from a
decision in one way: the decision was already made, and the system disagrees
with it. That is why a defect authorises work without a new decision, and why
its task restores a requirement instead of closing a new one. An epic for a
one-task fix is the overhead the research named as the reason people route
around a method.

RES-0015 found reproduction the step that makes the rest answerable: without
it, the question of which requirement a defect violates is asked about
behaviour nobody has seen twice. So the reproduction comes before `enters`,
and a program checks the order.

Most of the rules are facts in front matter and sections, so `paw check`
holds them (REQ-1172). Whether a defect enters at `implement` or at `design`
needs a reader, so the step files hold it.

The strongest objection: the defect records approved before this decision
have no `enters`, so a rule requiring it would fail them all. Requiring it is
a draft rule, as ADR-1140 decided for every new content rule, so an approved
defect keeps the rules it was approved under.

## Alternatives

| Option                                        | Better at                                     | Why it lost                                                                                     |
| --------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Do nothing                                    | No change to the record's shape               | Every one-task fix pays for an epic, and nothing records where a defect enters the chain        |
| A defect's task still needs an epic           | One place for every task's mark               | The epic is overhead for a one-task fix, which REQ-0354 lets a defect avoid                     |
| Keep a defect's task marks in the task itself | No marks in a record that is otherwise frozen | Every other task's state derives from its authorising record's mark, and two places would drift |
| Triage in prose only, no `enters` field       | No new field                                  | A program can't read which step a paragraph means, and the step is what triage decides          |

## What it costs

The task and defect templates gain a field each and the defect template a `##
Tasks` section. The layout gains the `bug` and `prompted-by` relations and the
`enters` field, and no longer requires `epic` on a task. A defect with its own
tasks is edited after approval in its Tasks and Closed by sections, as an epic
is in its marks. The record's program reads one more authorising kind for
tasks.

## What would reverse it

I would reverse the one-task path if defects carrying their own tasks drifted
from their tasks' state in two verifications, which would show the marks
belong in one kind of record only.

## Consequences

- The layout lets a task name `bug`, adds `enters` to the defect kind and
  `prompted-by` to the relations, and the templates follow.
- `paw check`, `paw ready` and `paw status` read a defect's tasks and marks.
- The implement and verify steps carry the rules on a defect.
- SPC-1090 states the defect's path, and SPC-1100 the new relations.

## How I will know it was realised

1. Fixtures show a task naming `bug:` whose defect marks it done derived as
   done, `paw ready implement` passing for it once the defect is approved, and
   `paw status` counting tasks by the kind that authorised them.
2. Fixtures show each rule `paw check` holds here failing on a draft that
   breaks it, and the defects approved before this decision passing.
3. The implement and verify step files carry the rules on a defect, traced in
   the task's evidence.
4. Every requirement ADR-1440 addresses lands in exactly one closed task.

## What this does not settle

- How a defect is debugged, which ADR-1430 settles.
- Whether a defect's severity is right, which the triage judges.
- Projecting a defect's own tasks onto a tracker, which the GitHub pack does
  for an epic's today and would need a change of its own.
