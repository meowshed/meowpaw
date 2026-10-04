---
id: RES-0332
artifact: research
status: approved
revised: 2026-10-04
elaborates: RES-0011
---

# A stored done claim can be checked against the tree

## Summary

An explicit `done` value can make completed decisions, epics and tasks visible
in their own records without becoming a second source of truth, provided the
gate rejects every value that disagrees with the existing completion
calculation. This research covers the lifecycle contract and migration of
those three record kinds; it does not change requirement or defect states.

## The question

Should a decision, epic or task store `status: done` when its work is complete,
and should the gate verify that claim from the tree? The assumption to
challenge is that visibility requires storage: `paw status` can display a
derived state without changing a record. Storage earns its cost only if the
record itself must carry an auditable completion claim and the checker makes
drift impossible.

## Method

On 2026-10-04, I read `CLAUDE.md`, RES-0011 and the existing requirement
records about observed status on `main` after pull request #830. I read the allowed statuses in
`plugins/meow-flow/lib/layout.toml` and the completion functions `marks`,
`mark_of`, `task_finished` and `position` in `crates/meow/src/record.rs` at the
same revision. I ran `paw find` for observed state, lifecycle, approval and
migration terms, `paw status` for unconnected records, and `paw count` for the migration baseline. No external
source was needed because the question concerns this repository's own
contract and implementation.

## Findings

### Stored and observed states currently answer different questions

`CLAUDE.md` says `approved` records agreement and freezes a record, while
`open`, `in-progress` and `closed` are observations derived from the tree.
The existing requirements make an observed status derived and forbid it in
stored metadata. A stored `done` therefore cannot merely
rename the existing observed `closed`; it must be a checked claim whose truth
continues to come from the tree.

### The tree already has one completion calculation

`record.rs` derives a task's mark from its epic or defect, or from Evidence for
a task directly realising a decision. The same module derives whether an epic
or decision is closed from its tasks. Reusing those functions gives a stored
claim an independent verifier; implementing a second calculation for `done`
would create the drift the proposal is meant to prevent.

### Approval and completion are sequential but not mutually exclusive facts

A record must be approved before its work can be implemented, and approval
freezes its substantive content. Completion occurs later. Treating `done` as
an unchecked replacement for `approved` would make approval gates fail or
silently unfreeze a record. Treating it as the later stored phase of an
approved record preserves the freeze and lets readiness checks accept both
phases.

### Three viable representations have different failure modes

Keeping completion derived only has the smallest metadata surface and cannot
drift, while its advocate can point to `paw status` as the proper view. It
does not satisfy the requested property that the Markdown record itself state
completion.

Making `status: done` authoritative gives readers a direct answer and makes a
single file easy to query. It is better for systems that cannot load the whole
record, but it permits a false claim whenever task marks or Evidence disagree.

Making `status: done` a stored assertion checked in both directions gives the
record a visible claim while retaining the tree as verifier. It costs a
repository-wide migration and requires every approval and frozen-record path
to treat `done` as post-approval. The strongest case against it is mechanical
churn across already frozen records; that cost is justified only if the
checker also rejects a derived completion left at `approved`, so the new field
cannot become optional decoration. This comparison decides on the checked
assertion rather than leaving the representation to discretion.

### The migration is bounded and mechanically countable

On `main` after pull request #830, `paw count` reports 119 decisions, 98 epics and 315
tasks. Existing completion is already derived, so a migration can select
records through the same calculation, change only their structured `status`
field and verify equal artifact counts before and after.

### Three grandfathered tasks have no authorising relation

On `main` after pull request #830, `paw status` reports TSK-1000, TSK-1100 and TSK-1220
as unconnected. Draft rules now require an authority, but those frozen tasks
predate the rule. The current calculation consults Evidence only for a task
directly realising a decision, so an unconnected historical task cannot ever
derive completion. Letting a grandfathered task with no authority derive
completion from non-placeholder Evidence closes that finite compatibility gap
without weakening the authority rule for new tasks.

## Conclusions

1. Decisions, epics and tasks must accept `done` as a stored post-approval
   phase that preserves the same frozen-record rules as `approved`.
2. The gate must reject `status: done` unless the existing tree calculation
   derives completion, and must reject a derived completion that remains
   `status: approved`.
3. Readiness, projection and relation checks that accept an approved record
   must also accept its `done` phase where completion does not invalidate it.
4. Existing decisions, epics and tasks that the current calculation derives
   as complete must migrate to `status: done` in the same change, with artifact
   counts recorded before and after.
5. Requirements, defects and other artifact kinds must retain their current
   stored and observed status contracts.
6. A grandfathered task with no authorising relation must derive completion
   from its non-placeholder Evidence, because no parent mark can exist for it.

## Sources

- `CLAUDE.md` on `main` after pull request #830, read 2026-10-04 - stored and observed lifecycle
  vocabulary, record freezing and the ordered method.
- `project/research/RES-0011-artifact-lifecycle.md` on `main` after pull request #830, read 2026-10-04
  - the append-only record and derived-projection model.
- The observed-status requirement records on `main` after pull request #830, read 2026-10-04 -
  the existing obligations that the new claim must preserve rather than
  contradict.
- `crates/meow/src/record.rs` and `plugins/meow-flow/lib/layout.toml`, read 2026-10-04
  on `main` after pull request #830 - the completion calculation and allowed stored statuses.
