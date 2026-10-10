---
id: RES-0349
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A tracker edit is told by a fingerprint and not by a clock, and a frozen record can't take one

## Summary

GitHub gives one `updated_at` for a whole issue and no per-field time, so which
side of a task changed since the last synchronisation can't be read from
timestamps. A fingerprint of each side taken at the last synchronisation tells
it: one side changed, both changed, or neither. On that, "the newer change wins,
and the file wins a conflict" is the side that changed, and the file where both
did. Two approved records forbid the tracker-to-file direction today, and a
frozen record can't take a reworded title or body from any source, so the
direction is open for drafts and for the issue's state only.

The document covers how one task and its issue are compared and which side's
change may be applied. It doesn't cover the trigger, which a decision sets.

## The question

How does the harness tell which side of a task and its issue changed, and may
it write the tracker's change into the file?

The assumption behind the question is that "newer" can be read. For a whole
issue it can, and for a field it can't, and the file has no time of its own
(a record carries no date that identifies work, `CLAUDE.md` layout).

## Method

I read the issue endpoint's response fields in the GitHub REST documentation
on 2026-10-10. I read what the records say of the direction of writes:
REQ-1353, REQ-1372, REQ-1386, REQ-1388, REQ-1394, REQ-1400, REQ-2360 and
ADR-1310, and the section "Projecting the record onto a tracker" of SPC-1080,
and the frozen check in SPC-1070. I read `tools/sync_issues.py`, which sends a
record's body to its issue. I did not call GitHub, and I did not test what a
fingerprint of a body does when GitHub normalises its whitespace.

## Findings

### GitHub offers one timestamp for the whole issue

The issue object has `title`, `body`, `state`, `updated_at` and `closed_at`.
`updated_at` is the time of the last change to any field. The documentation
names no per-field modification time and no edit history.

### The mapping holds the file side's fingerprint only

REQ-1386 has the mapping carry a fingerprint of the task at the version last
projected, and `projected:` on the task holds it. REQ-1388 says the state of a
synchronisation is computed by comparing that fingerprint with the tracker, and
not stored. A fingerprint of the tracker side at the same moment isn't kept, so
a later difference can't be told from one the file made.

### The records forbid the tracker-to-file direction today

REQ-1353 permits one write from the tracker to the record: marking an item done.
REQ-1394 says that where the sides disagree on a field the repository owns the
harness reports and doesn't overwrite, and ADR-1310 says an edited issue "is
reported and left". SPC-1080 states the same.

### A frozen record takes no reworded text

`paw check frozen` lets an approved task change only its Evidence, its mark,
`issue` and `projected` (SPC-1070). A title or body written from an issue into
an approved task is a rewording of an approved record, which `CLAUDE.md` names
as the failure the method exists to prevent.

### One direction is already in a script

`tools/sync_issues.py` sends the body of a task or a defect to the issue named
in its front matter, and reports what differs without `--write`. ADR-1310 says
the pack replaces it.

## Comparison

| Option                                              | Better at                                       | Why it falls short                                                           |
| --------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------- |
| Record to tracker only, as today                    | One owner, nothing to reconcile                 | An edit made on the tracker is lost or reported forever                      |
| Both ways by `updated_at`                           | Needs no stored state                           | One clock for a whole issue, and none for the file, so a field can't be told |
| Both ways by a fingerprint of each side             | Tells one side, both or neither                 | Stores the tracker's fingerprint, which REQ-1388 refuses                     |
| Both ways for drafts and state, report for approved | The file wins a conflict, a frozen record stays | An approved record's wording is changed on the tracker and not synchronised  |

## The case against the fingerprint

A stored fingerprint of the tracker side is derived state, the thing REQ-1388
forbids, and it goes stale when the issue is edited by a person while a run
holds an old value. The harm is bounded: the stored value only decides which
side to apply, a wrong value reads as a conflict, and a conflict is won by the
file.

## Conclusions

1. A synchronisation tells which side changed from a fingerprint of each side
   taken at the last synchronisation, and not from a timestamp (Findings:
   GitHub offers one timestamp for the whole issue; the mapping holds the file
   side's fingerprint only).
2. Where only the tracker side changed, its title, body and state are written
   into a draft, and where both changed the file's are written to the tracker
   (Findings: the mapping holds the file side's fingerprint only).
3. Where the record is approved, the tracker's difference in title or body is
   reported and not written, and the issue's state still flows to the record
   (Findings: a frozen record takes no reworded text; the records forbid the
   tracker-to-file direction today).
4. The mapping carries the tracker side's fingerprint beside the file side's
   (Findings: the mapping holds the file side's fingerprint only).
5. `tools/sync_issues.py` is retired in favour of the pack's command (Findings:
   one direction is already in a script).

## Sources

- [GitHub REST: get an issue](https://docs.github.com/en/rest/issues/issues#get-an-issue), read 2026-10-10 - the issue's fields and its one `updated_at`.
- `project/requirements/REQ-1353-*.md`, `REQ-1386-*.md`, `REQ-1388-*.md`, `REQ-1394-*.md`, as of pull request 880, read 2026-10-10 - the direction of writes and the stored fingerprint.
- `project/adrs/ADR-1310-*.md` and `project/specs/SPC-1080-the-native-tool.md` ("Projecting the record onto a tracker") and `SPC-1070` ("The frozen check"), as of pull request 880, read 2026-10-10 - how an edited issue and a frozen record are treated.
- `tools/sync_issues.py` as of pull request 880, read 2026-10-10 - the existing one-way script.
