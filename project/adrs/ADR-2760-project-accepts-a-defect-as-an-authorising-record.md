---
id: ADR-2760
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-4000]
supersedes: []
---

# 2760. `project` accepts a defect as an authorising record

## Decision

`meow-github project` accepts `BUG-NNNN` beside `EPC-NNNN` and `ADR-NNNN`.
It resolves an approved defect, selects every active task whose `bug` field
names it, projects those tasks through the existing issue mapping and derives
done state from the defect's `## Tasks` marks. The issue body names the task
and the defect that authorises it. All existing replay, `--check`, read-back,
failure and no-grouping behaviour remains shared.

Once accepted, defects carrying tasks can be projected and checked with the
same command as other authorising records. What still does not work is filing
an issue for a defect record itself; the command projects work items, not the
evidence that authorised them.

## Why

RES-0331 finds that the current implementation already generalises epic
projection for direct ADR tasks, and that ADR-1440 gives defects the same task
ownership and marks the projection consumes. One shared protocol avoids a
second set of partial-run and disagreement states.

The strongest objection is that widening an epic-oriented implementation can
silently apply an epic assumption to a defect. Explicit target-kind resolution,
defect-specific issue prose and fixtures covering creation, replay and done
comparison expose that boundary. Repetition, empty task sets, edited issues,
closed issues and request failures retain the existing outcomes; only target
selection changes. If nobody attends for a month, mappings and disagreements
remain recoverable from the task and a later `--check`, so no new queue forms.

## Alternatives

| Option                                 | Better at                         | Why it lost                                                                           |
| -------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------- |
| Do nothing                             | No implementation change          | Defect-authorised tasks remain the only task path the declared tracker cannot project |
| A separate defect command              | Independent wording and evolution | It duplicates mapping, replay, read-back and failure contracts                        |
| Convert every defect task into an epic | Keeps the current target kinds    | It contradicts ADR-1440's deliberate one-task path and adds a second planning record  |

## What it costs

The target resolver, task selector and issue-body renderer gain a third kind.
The fixture repository gains a defect and its task. Documentation stops
describing the command as epic-only. The operator learns no new command.

## What would reverse it

- Defect tasks acquire projection semantics that cannot share the same mapping
  and failure states without branching most of the command.

## Consequences

- `SPC-1080` states that `project` accepts approved epics, defects and direct
  decisions.
- The command usage names an authorising record instead of only an epic.
- `ADR-1440` remains in force; this decision settles the tracker question it
  left open.
- No security boundary changes: tracker text remains untrusted, writes remain
  limited to issues and every request retains the request layer from ADR-1810.

## How I will know it was realised

1. A fixture projects the task of an approved defect, writes its mapping and
   names the defect in the issue body.
2. A replay writes nothing, and `--check` reports tracker disagreement without
   writing, as it does for an epic.
3. A closed issue agrees only when the defect marks its task done.
4. `REQ-4000` lands in one closed task and the shipped usage documents
   `BUG-NNNN` as a target.

## What this does not settle

- Projecting the defect record itself as an issue.
- Adding a tracker grouping for a defect or epic.
- Synchronising any tracker other than the one the repository declares.
