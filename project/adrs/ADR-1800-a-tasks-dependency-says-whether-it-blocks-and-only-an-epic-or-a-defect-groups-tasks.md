---
id: ADR-1800
artifact: adr
status: done
revised: 2026-09-28
addresses: [REQ-1358, REQ-3320]
postpones: []
supersedes: []
---

# 1800. A task's dependency says whether it blocks, and only an epic or a defect groups tasks

## Decision

Each line under a task's `## Depends on` names one task and says whether it
blocks, and only a blocking dependency makes a task wait:

```text
- TSK-NNNN (blocking): the parser this task extends lands there.
- TSK-MMMM (not blocking): shares a fixture, which either task can write.
```

- `paw` reads a dependency line as blocking when it says `(blocking)`, or
  when it names a `TSK-` identifier and says neither form, and as not blocking
  when it says `(not blocking)`. `paw ready cover`, `paw ready implement` and
  `paw status` wait only on the blocking ones, so a task whose only open
  dependency doesn't block is ready. The rule `defect-epic-ordered` accepts a
  defect's epic by two paths today, a task's dependency and an epic entry whose
  text contains `depends:`, and on both it counts only a blocking one as an
  order between the defect's tasks, because a convenience imposes no order. An
  epic entry's `depends:` counts when it says `(blocking)` or says neither
  form, and doesn't count when it says `(not blocking)`. An unmarked entry
  counts because every approved epic was written under the template's "a
  convenience isn't a dependency", so its `depends:` was meant as an order.
- A new draft rule on tasks, `dependency-declared`, reports each line under a
  draft task's `## Depends on` that names a `TSK-` identifier without
  `(blocking)` or `(not blocking)`, and each line naming more than one
  identifier, because a line with two identifiers and one marker leaves the
  second one's meaning to a guess. It is a draft rule (ADR-1140), so the 53
  approved tasks that name a dependency keep the meaning they were approved
  with, an order, and none is migrated.
- The task template shows both forms. The epic template's entry takes the same
  marker, as `depends: TSK-NNNN (not blocking) - why`, and the method's epic
  step gains a rule beside E6: declare a dependency that exists only for
  convenience as not blocking, with its reason, and never leave it out. The
  task and epic types in `meow-prose` say the same in place of "a convenience
  isn't a dependency".

A task sits under exactly one record, the epic that realises its authorising
record or the defect that carries it, and nothing else groups tasks (REQ-3320):

- In the record, `one-authority` already reports a draft task naming both
  `epic:` and `bug:`, or neither. `lib/layout.toml` adds `milestone`,
  `parent`, `project`, `sprint`, `iteration`, `label` and `labels` to the
  forbidden fields of the task, epic and defect kinds, and `epic` to the epic
  kind's as well, so a task, an epic or a defect that carries one is reported
  whatever its status. The three lists match because an epic or a defect
  grouped under a milestone or a label groups its tasks there too, and `epic`
  is the epic's only extra field because only an epic would place one epic
  under another. A forbidden field applies to approved records too. RES-0289's
  searches found no task, epic or defect carrying any of these fields, and no
  epic carrying `epic:`.
- On a tracker, `meow-github project` passes none of `--milestone`,
  `--parent`, `--project` or `--label` and creates no blocked-by relation. It
  writes a task's dependencies into the issue's body, as it does today, and
  the body now carries each one's marker, because GitHub's only dependency
  relation blocks (RES-0289), and a label or a project field would be a
  grouping this decision forbids.

After this decision an epic can record that two tasks share something without
serialising them, a draft that leaves the question open is reported, and a
grouping field on a task, an epic or a defect is reported. What still doesn't work:

- A blocking dependency isn't projected onto GitHub's blocked-by relation, so
  GitHub shows no Blocked icon for a task waiting on another.
- The epic isn't projected onto a tracker grouping (REQ-1364), so on GitHub
  the issues of one epic share only the epic's identifier in their bodies.
- The `[P]` mark on an epic's entry and a task's dependencies both speak about
  parallel work, and nothing checks that they agree.
- The marker on an epic entry's `depends:` isn't checked against the task's
  own `## Depends on` line, and readiness reads only the task's line, so an
  epic can say `(not blocking)` while the task still waits.
- A grouping the record invents under a field name the forbidden list doesn't
  hold, such as `group:`, isn't reported.

## Why

RES-0289 found that `depends_on()` returns every `TSK-` identifier under
`## Depends on`, so every dependency the record holds is an order, and the
templates tell the author to leave a convenience out. REQ-1358 asks that the
author declare it instead, which is RES-0022's rule as `meowctl` stated it:
"say so and let them proceed in parallel". Declaring it keeps the reason two
tasks touch each other where the implementer of the second one reads it.
RES-0289 left untested whether that implementer acts on the reason. I take
REQ-1358, which is approved, as settling that it's worth recording, and no
trigger under What would reverse it measures whether the reason is read.

The unmarked form reads as blocking because each of the 53 approved tasks with
a dependency was written under the rule that left convenience out, so each
was meant as an order, and a frozen record keeps the rules it was approved
under (ADR-1140).

REQ-1362 asked that the epic be the only grouping above a task, and REQ-0354,
approved before it, lets a defect carry its own tasks. No design could meet
both, so I withdrew REQ-1362 and wrote REQ-3320, which names the two records a
task may sit under and keeps the rest of the obligation. RES-0289 found GitHub
offers four more groupings, and RES-0022 found that a sub-issue doesn't close
by keyword and that a tracker grouping the record doesn't hold is a second
plan.

## Alternatives

| Option                                                                            | Better at                                                         | Why it lost                                                                                                                                                    |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leave a convenience dependency out, as the templates say now                      | No marker, no rule                                                | REQ-1358 asks for a declaration, and the implementer loses the reason the two tasks touch                                                                      |
| A front matter field, such as `depends: [TSK-NNNN]` and `after: [TSK-MMMM]`       | Structured data, read without a line pattern (M16)                | The reason stays in the body, apart from the identifier, and the 53 approved tasks would keep a second form forever, since a frozen record can't be migrated   |
| Keep an unmarked line blocking and add only an optional `(not blocking)` marker   | No draft fails the check, and the reading side of REQ-1358 is met | Nothing makes a draft author decide line by line, so a convenience written from habit stays unmarked and blocks, and REQ-1358's declaration is never asked for |
| A separate `## Related` section for convenience dependencies                      | An unmarked line under `## Depends on` keeps meaning blocks       | Two sections for one relation, and a draft could still leave a convenience under `## Depends on` with nothing to report it                                     |
| Read an unmarked line as not blocking                                             | A draft author types less for the common convenience case         | Every approved task's order would stop gating `paw ready`, which reverses 53 approved decisions silently                                                       |
| Keep REQ-1362 and read a defect's tasks as outside it                             | No withdrawal                                                     | The requirement's text says the epic is the only grouping, and a reading that exempts the defect rewords an approved requirement in place                      |
| Project each blocking dependency onto GitHub's blocked-by relation in this record | GitHub shows the Blocked icon                                     | It changes `meow-github`'s writes and its replay rules (ADR-1310), which is a tracker decision of its own; this one needs no tracker                           |
| Do nothing                                                                        | No change                                                         | REQ-1358 and REQ-3320 stay unmet, and a task waits on a dependency its author knew didn't block                                                                |

## What it costs

Every draft task author writes a marker on each dependency line, and
`paw check` reports a draft that leaves one out, so a task written from habit
fails the check once. A task whose `## Depends on` mentions another task in
passing, as in "unlike TSK-NNNN", is reported as an undeclared dependency, and
its author rewrites the sentence.

Whoever maintains `crates/meow` changes one function every readiness answer
depends on. A pattern that misreads `(not blocking)` as blocking only delays a
task, and one that misreads `(blocking)` as not blocking lets a task start
before its input exists, so the fixtures test both forms and the unmarked
form. `meow-flow` and `meow-prose` each raise their minor version, since the
templates and the step change what an author is told.

Every draft epic author writes the same marker on each entry's `depends:`,
and the epic step's review reads it. Whoever maintains `meow-github` keeps a
stand-in `gh` that records its arguments, and updates it whenever `project`
passes a new argument.

Nothing accumulates, and nobody waits on a person: the rule reports at
`paw check`, which the gate already runs.

## What would reverse it

I would move dependencies into front matter if the record gained a parser that
edits a task's body and its front matter together, so the reason could sit
beside the identifier in structured data. I would read an unmarked line as not
blocking if the approved tasks naming a dependency were all withdrawn or
superseded. I would allow a second grouping if a tracker could close a grouped
item by keyword in the same change as its group, and a repository asked the
record to hold that grouping.

I would drop the `(not blocking)` marker, and go back to leaving a convenience
out, if a task started on a `(not blocking)` dependency is reworked or
reverted because that dependency's output was missing. I would make the epic
step's review check each `(not blocking)` reason, and not only that one is
present, if more than half the dependency lines in the drafts written after
this decision say `(not blocking)`. The 53 approved tasks wrote every dependency
as an order, so a share above half says the marker has become the
default, which is the Premortem's failure.

## Consequences

- `crates/meow/src/record.rs`: `depends_on()` returns the blocking
  dependencies only, a new draft rule `dependency-declared`, and
  `defect-epic-ordered` counting only blocking entries.
- `plugins/meow-flow/lib/layout.toml`: `dependency-declared` among the task's
  draft rules, and the forbidden fields above on the task, epic and defect
  kinds.
- `plugins/meow-flow/templates/task.md` and `templates/epic.md`, and the epic
  step's rule beside E6, with `meow-flow`'s version raised.
- `plugins/meow-prose/skills/writing/types/record/task.md` and `epic.md`, with
  `meow-prose`'s version raised.
- A test in `meow-github` with a stand-in `gh` that records its arguments.
- SPC-1090 says which dependencies the readiness table waits on, and SPC-1070
  names the new draft rule.

## How I will know it was realised

1. A `paw` fixture shows a draft task whose dependency line reads
   `- TSK-NNNN (not blocking): shares a helper` passing `paw check`, and the
   same draft with a bare `- TSK-NNNN` line, or a line naming two identifiers,
   reported by line under `dependency-declared`.
2. A fixture shows an approved task with a bare dependency line not reported,
   and `paw ready implement` still waiting on it.
3. A fixture shows `paw ready implement` and `paw ready cover` reporting a
   task ready when its only open dependency is marked `(not blocking)`, and
   waiting when the same dependency is marked `(blocking)`; `paw status` names
   the task whose only dependency is not blocking as next.
4. Fixtures show `defect-epic-ordered` reporting a defect's epic whose only
   order between tasks is a task's dependency line marked `(not blocking)`,
   and one whose only order is an epic entry's `depends:` marked
   `(not blocking)`, and accepting each when the marker is `(blocking)`.
5. A fixture shows a task carrying `milestone:` and an epic carrying `parent:`
   each reported by `paw check`, and a task naming `epic:` or `bug:` passing.
6. A `meow-github` test with a stand-in `gh` shows `project` passing no
   `--milestone`, `--parent`, `--project` or `--label` argument, and an issue
   body carrying `(not blocking)` where the task's line does.
7. The task and epic templates in `meow-flow` and the task and epic types in
   `meow-prose` show `(blocking)` and `(not blocking)` and no longer say a
   convenience isn't a dependency, the epic step holds the new rule beside E6,
   SPC-1090 states that readiness waits only on blocking dependencies, and
   SPC-1070 names `dependency-declared`.
8. A fixture shows a defect carrying `milestone:` reported by `paw check`.
9. Every requirement ADR-1800 addresses lands in exactly one closed task.

## What this does not settle

- Projecting a blocking dependency onto GitHub's blocked-by relation.
- Projecting the epic onto a tracker grouping, which REQ-1364 asks for.
- Whether the `[P]` mark should be derived from the dependencies or checked
  against them.
- How a stack of pull requests follows the dependencies (REQ-1810, REQ-1812,
  REQ-1814). Whatever decides it reads the blocking dependencies, since a
  not-blocking one imposes no order.

## Premortem

A year on, the marker was the wrong place. Authors wrote `(not blocking)` on
every line to get a task started, and the order the epic needed was lost,
because the rule checks that a marker is present and never that it's true.
The epic step's review was the only check on the choice, and a reviewer
approving an epic of twenty tasks didn't read each reason. The strongest
objection is this one: the decision moves a judgement into a token a program
reads, and the program can't tell a convenience from an order.
