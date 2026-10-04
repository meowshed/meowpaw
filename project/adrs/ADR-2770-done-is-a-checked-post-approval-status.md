---
id: ADR-2770
artifact: adr
status: approved
revised: 2026-10-04
addresses: [REQ-0583, REQ-0585, REQ-0594, REQ-0595, REQ-0596]
supersedes: []
---

# 2770. Done is a checked post-approval status

## Decision

`done` joins the stored status vocabulary for decisions, epics and tasks as a
post-approval claim. It retains the freeze and acceptance of `approved`, while
`paw check` verifies it against the completion already derived from the tree.
The check is bidirectional: a derived-complete record left at `approved` and a
`done` record not derived complete are both findings.

One completion calculation serves the status check and every existing view:

- a task under an epic or defect is complete when its parent marks it `[x]`;
- a task directly realising a decision is complete when its Evidence is not
  empty and does not begin with `Not yet`;
- a grandfathered task with no epic, defect or decision is complete by the
  same Evidence rule, because no parent mark can exist for it;
- an epic is complete when each task it carries is done or dropped;
- a decision is complete when its directly realising tasks, and every task of
  its realising epic when it has one, are done or dropped.

The `approved → done` transition is an allowed frozen-record edit. It changes
only the structured status field and does not make any other content mutable.
Every readiness, relation and projection path that asks whether one of these
records is approved treats `done` as approved. Other artifact kinds do not
accept the new value.

The migration changes only the status field of every decision, epic and task
the calculation derives complete, including the grandfathered tasks after
their real completion Evidence is written. It records artifact counts before
and after, and one check over the final tree proves both directions at once.

After this decision, the Markdown record states completion and the tree proves
the statement; missing or false claims fail the gate. What still does not
work: a reader of one file cannot independently prove the claim without the
rest of the record, and no completion status is added to requirements or
defects.

## Why

RES-0332 found that the existing split between stored agreement and derived
observation prevents drift but leaves completion absent from the record a
reader opens. A checked assertion keeps the derivation authoritative while
making the lifecycle explicit. Reusing the existing task marks, Evidence and
group closure avoids a second algorithm.

The strongest objection is the migration churn across hundreds of frozen
records. The churn is mechanical and reviewable because it changes one
structured field, while making the check one-way would incur the same model
cost without ensuring completed records ever adopt it.

## Alternatives

| Option                                  | Better at                                      | Why it lost                                                        |
| --------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------ |
| Checked `done` claim in both directions | Visible records without an independent truth   | Chosen                                                             |
| Keep completion derived only            | No migration and no possible metadata drift    | The Markdown record still does not state that its work is complete |
| Make stored `done` authoritative        | A single file answers without loading the tree | A stale field can close work whose marks or Evidence remain open   |
| Check only a written `done` claim       | Existing records need no migration             | Derived-complete records may omit the field forever                |

## What it costs

The layout, all approval predicates, the frozen check, status diagnostics,
templates and documentation must understand a post-approval state. The
migration touches every completed decision, epic and task, and any future
completion PR must update the status alongside its marks or Evidence.

If nobody attends to the repository for a month, no queue accumulates: a
missing transition is one local gate finding fixed in the same change. The
design adds no network call, notification, concurrent writer or
security-relevant boundary.

## What would reverse it

- The status diff becomes materially harder to review than the completion
  marks it repeats, and users choose the derived view over record-local
  visibility.
- A future record format exposes derived fields without storing them in source,
  so one Markdown view can show completion without a checked assertion.

## Consequences

- REQ-0586 is withdrawn because checked stored derivation is now deliberate.
- The shared decided vocabulary gains `done`, but only decision, epic and task
  kinds declare it.
- `paw check` reports `done` disagreement in either direction, using one
  completion calculation.
- Approval gates and frozen-record checks treat `done` as post-approval.
- Templates tell authors to set `done` in the same change that supplies marks
  and Evidence.
- All currently completed decisions, epics and tasks migrate mechanically.

## How I will know it was realised

1. Fixtures show an open record marked `done` and a completed record left
   `approved` both fail, while matching states pass for each of the three
   kinds.
2. Fixtures show a `done` input passes the same readiness and projection paths
   as an approved input.
3. A frozen-check fixture permits only `approved → done` in the status field
   and still rejects a simultaneous substantive edit.
4. A grandfathered task with no authority and completed Evidence derives
   complete and accepts `done`.
5. `paw count` reports the same artifact totals before and after migration,
   and the repository gate reports no status disagreement.

## What this does not settle

- Completion for requirements, defects, research or other record kinds.
- Rendering a derived field into Markdown without storing it.
- Closing or reopening the corresponding tracker issue.
