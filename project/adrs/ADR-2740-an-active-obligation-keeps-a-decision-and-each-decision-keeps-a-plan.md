---
id: ADR-2740
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-0132,
    REQ-0147,
    REQ-0149,
    REQ-0151,
    REQ-0157,
    REQ-0452,
    REQ-0454,
    REQ-0456,
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-0819,
    REQ-0822,
    REQ-0823,
    REQ-2202,
    REQ-2372,
    REQ-2376,
    REQ-2390,
    REQ-2406,
    REQ-2830,
    REQ-2958,
    REQ-2960,
    REQ-2964,
    REQ-2966,
    REQ-2967,
    REQ-2968,
    REQ-2969,
    REQ-2970,
    REQ-3072,
    REQ-3800,
    REQ-3900,
    REQ-3902,
  ]
supersedes: []
---

# 2740. An active obligation keeps a decision, and each decision keeps a plan

## Decision

An approved requirement always names an approved decision through
`addresses` or `postpones`, and an approved decision that addresses work
always has an approved epic or direct task. Superseding a decision carries
forward every requirement that remains in force, because the old decision no
longer provides it (REQ-3900, REQ-3902).

The obligations formerly provided only by ADR-1490, ADR-1530, ADR-1560 and
ADR-2000 remain in force under this decision. Their behaviour already lives in
SPC-1040, SPC-1090 and SPC-1201 and in the tasks that realised those records;
this amendment restores the missing upward relation and changes no behaviour.

REQ-1188 is withdrawn because the platform installs no dependency language
and ADR-1110 ships one native tool. REQ-2666 is withdrawn because the record
stores subjects rather than history. REQ-2954 is withdrawn because TOML cannot
share YAML front matter; REQ-3800 preserves its comments obligation, which
TOML meets.

Once accepted, the record reports an active requirement with no active
decision and an active decision with no approved plan. It still does not
decide how an attended action asks for confirmation; ADR-2750 does.

## Why

RES-0063 makes the decision-to-plan relation the authority for work, while
RES-0261 requires a profile a person can explain beside its values. A
superseded provider silently removed 30 valid obligations from the active
decision graph, and five deliberately open contradictions showed that the
record checked task coverage without checking its two earlier gates.

## Alternatives

| Option                               | Better at                   | Why it lost                                          |
| ------------------------------------ | --------------------------- | ---------------------------------------------------- |
| Treat superseded providers as active | Fewer relations             | A superseded choice no longer states what holds      |
| Edit the old decisions               | Smaller diff                | Approved records are frozen                          |
| Check both provider and plan         | Keeping the chain connected | Chosen; it detects the two omissions at their source |

## What it costs

The record check reads every approved requirement, decision, epic and task,
and a superseding decision must state what it carries forward.

## What would reverse it

- A later record model derives authority without authored requirement and
  decision relations and migrates every existing artifact to that model.

## Consequences

REQ-1188, REQ-2666 and REQ-2954 carry withdrawal tombstones. `paw check`
gains provider and plan findings. The profile keeps comments through REQ-3800.

## How I will know it was realised

1. A fixture requirement provided only by a superseded ADR fails `paw check`.
2. A fixture approved ADR with no approved epic or direct task fails.
3. The repository has no approved requirement without an approved provider.
4. The repository has no approved addressing ADR without an approved plan.
5. A profile containing comments parses successfully.

## What this does not settle

- Whether an existing task should be copied into a later epic; a carried
  requirement remains closed by its original evidence.
