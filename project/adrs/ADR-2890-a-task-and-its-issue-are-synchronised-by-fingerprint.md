---
id: ADR-2890
artifact: adr
status: approved
revised: 2026-10-10
addresses: [REQ-4700, REQ-4702, REQ-4704, REQ-4706]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2890. A task and its issue are synchronised by a fingerprint of each side

## Decision

`meow-github sync` compares each task with its issue by a fingerprint of the
record side and of the tracker side, both taken at the last synchronisation and
carried by the mapping (REQ-4704). Where only one side changed, its change is
applied to the other. Where both changed, the record's is applied (REQ-4700).
Where the record is approved, the tracker's title or body is reported and never
written into it, and the issue's state is still written, as `done` is today
(REQ-4702).

The method runs the synchronisation at the start and at the end of an epic's
work, and nothing runs it in the background (REQ-4706). I chose that reading of
"automatically" because the owner didn't name a trigger, and a background run
would write into the record with no person looking. The owner may overturn it
by naming a trigger.

Once this is accepted, a person edits an issue's title on GitHub and a draft task
takes it at the next run. What still doesn't work: an approved task's wording
changed on the tracker, which is reported and stays on the tracker.

## Why

RES-0349 found that GitHub keeps one `updated_at` for a whole issue, so
"the newer" can't be told for a field, and that the fingerprints taken at the
last synchronisation say which side changed. A frozen record takes no reworded
text from any source.

## Alternatives

| Option                                   | Better at                          | Why it lost                                          |
| ---------------------------------------- | ---------------------------------- | ---------------------------------------------------- |
| Do nothing                               | One owner of every field           | An edit made on the tracker is reported forever      |
| Both ways by `updated_at`                | No stored state                    | One clock for the issue and none for the file        |
| Both ways for every record, approved too | The tracker's wording always lands | Rewords an approved record, which the method forbids |

## What it costs

The mapping stores a derived value, the tracker's fingerprint, which REQ-1388
refused, and it can go stale when a person edits the issue between runs. A stale
value reads as a conflict, and the record wins a conflict, so the harm is a
tracker edit overwritten, which the report names before it happens.

## What would reverse it

- A tracker edit overwritten in a conflict that a person wanted kept, twice, or
  GitHub exposing a per-field edit time that makes the fingerprint unnecessary.

## Consequences

REQ-1353, REQ-1394 and REQ-1388 are withdrawn and replaced. ADR-1310 is amended
in what it says of an edited issue, and SPC-1080's section on projecting the
record states the new rule. `tools/sync_issues.py` is retired. EPC-2810 carries
three tasks.

## How I will know it was realised

1. A fixture with a draft task whose issue's title changed gets the title in the
   file at the next `sync`, and an approved task gets a report and no write
   (REQ-4700, REQ-4702).
2. A fixture where both sides changed leaves the file's text on the issue
   (REQ-4700).
3. The method's start and end steps run `meow-github sync` (REQ-4706).

## What this does not settle

- A tracker other than GitHub Issues.
- Which fields beyond title, body and state travel.
