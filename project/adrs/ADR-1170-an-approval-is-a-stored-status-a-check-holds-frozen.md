---
id: ADR-1170
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0390,
    REQ-0392,
    REQ-0394,
    REQ-0396,
    REQ-0398,
    REQ-0400,
    REQ-0402,
    REQ-0622,
    REQ-0626,
    REQ-0630,
    REQ-0634,
    REQ-0635,
  ]
supersedes: []
---

# 1170. An approval is a stored status that a check holds frozen, and a session opens with what waits for one

## Decision

An approval stays what it is today: a record's stored `status` moving from
`draft` to `approved`, in a commit of its own, so it is durable, it survives
every session, and git ties it to the version it approved. What this decision
adds is the hold:

- `meow-method check frozen --base <rev>` compares every record that was
  approved at `<rev>` with its current text, and reports a change as one that
  invalidates the approval. A record may still change where its kind is meant
  to: a task's `## Evidence` and `issue`, an epic's marks and its verification
  until it carries `checked-at`, a status moving to `withdrawn` or
  `superseded`, and a line naming the record that authorises the change, such
  as `**Amended by ADR-NNNN.**` or `Corrected by BUG-NNNN`. A living document,
  the vision, a specification or an index, is never frozen.
- A `SessionStart` hook in `meow-method` runs `meow-method status --waiting`,
  which prints what waits for approval, with the gate each waits at, and
  nothing at all when nothing waits or the repository has no record, so a
  session opens with the pending approval and no other session pays for it.
- The `method` skill stops after producing an artifact that needs approval,
  and never reads silence, a change of subject or an unrelated instruction as
  one.

After this decision a change that rewords an approved requirement or decision
without naming what authorised it fails the check, and a session starts by
naming the approval it waits on. What still doesn't work: the check compares
against a base revision someone passes, so a pull request that isn't checked
against its base isn't held, and the gate in continuous integration doesn't
run it yet, because it needs the unit's binary built there.

## Why

`CLAUDE.md` freezes a record on approval and routes a correction through an
amendment, and calls rewording an approved artifact in place the single
failure the method exists to prevent. Until now review alone held that, and
BUG-1110 and BUG-1170 are both corrections a check would have had to let
through by their authorising line, which is the design here. RES-0031 found
that a gate record has to survive the session, that silence is not approval,
and that a revision advancing on every edit keeps what was gathered before a
change from standing after it; git records both the approval and any change
made after it.

REQ-0394 asks a session to open with a pending approval, and a `SessionStart`
hook's output reaches the model before its first response, as Claude Code's
hooks documentation says. Printing nothing when nothing waits keeps the cost
at zero for every other session.

The strongest objection: a frozen check with allowed zones is a list someone
maintains, and every new kind of legitimate edit widens it. That's true, and
the alternative, no check, leaves the method's central promise to discipline,
which this repository has already broken twice in one day.

## Alternatives

| Option                                                  | Better at                                     | Why it lost                                                                     |
| ------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------- |
| A diff against a base, allowed zones, authorising lines | Holds the freeze in the change that breaks it | Chosen                                                                          |
| A content hash stored in each record at approval        | Needs no git                                  | A second copy of the record's state in the record, which drifts with every edit |
| Approvals kept in run state outside the repository      | No commit per approval                        | Lost with the machine, invisible to review, and REQ-0402 asks it to survive     |
| Do nothing: review holds the freeze                     | Costs nothing                                 | Review missed it twice in one day                                               |

## What it costs

A check that reads git history, its fixtures, a hook, a flag on `status`, and
two lines in the skill. Every legitimate kind of edit to a frozen record has to
fit a zone or name its authority.

## What would reverse it

- The allowed zones grow until the check flags nothing a reviewer would, and
  it is switched off.
- The platform records approvals itself, bound to a version, and the check
  duplicates it.

## Consequences

- `meow-method check frozen` exists with fixtures, and the ship step in this
  repository runs it against the trunk.
- `meow-method` gains a `SessionStart` hook, and `status --waiting`.
- SPC-1070 states the frozen check and SPC-1090 the waiting report.

## How I will know it was realised

1. Rewording an approved requirement fails `check frozen --base HEAD`, and the
   same change with an added `**Amended by ADR-NNNN.**` line passes.
2. Adding evidence to an approved task and marks to an unverified epic passes.
3. A session started in this repository with a draft waiting opens with it,
   and one started with nothing waiting adds nothing to context.
4. Every requirement ADR-1170 addresses lands in exactly one closed task.

## What this does not settle

- Running the frozen check in continuous integration.
- Run state outside the repository, which the harness doesn't keep.
