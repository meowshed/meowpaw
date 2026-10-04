---
id: TSK-3860
artifact: task
status: done
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3652]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Migrate every record to the seven-step chain's shape

Every task loses `## Cover`, every epic loses `## Verified`, `checked-at` and `## Open review findings`, and each citation of a kept run file names the pull request it ran under instead, in a mechanical change of its own. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the record after the change, when `grep -rlE '^## (Cover|Verified|Open review findings)|^checked-at:' project/` runs, then it prints nothing. Closed by: that command's empty output and exit 1.
2. Given `paw count` run before and after, when the two outputs are compared, then every kind has the same number of records. Closed by: both outputs in the pull request.
3. Given the record after the change, when `paw check` runs, then it reports 0 findings. Closed by: the `test` verb.

## What to do

Edit front matter as structured data and sections by heading, never by text substitution (M16). Split the change: tasks, then epics, then citations, each in its own commit. `paw check frozen` must accept these edits for the sections ADR-2300 names; change the rule in the same pull request if it doesn't.

## Depends on

- TSK-3800 (blocking): until the program derives state from tasks, removing `checked-at` would turn every realised decision back to `next: verify`.
- TSK-3830 (blocking): the kept files the citations name are removed there.

## Evidence

`MigratedShape` in `plugins/meow-flow/tests/test_record.py` holds fifteen
checks and `tools/test_record_shape.py` two. The seven in the pull request's
first commit failed there, and ten more came with the two reviews' fixes.
Criterion 1's own command can't print nothing, because its pattern also
matches `## Coverage`; the tool test reads the same three headings and the
field on a word boundary, outside fenced code, and that is what holds it. `paw count` printed the same before and after:
1 vision, 20 specifications, 150 research, 1151 requirements, 73 decisions, 71
epics, 212 tasks, 48 defects, 1726 identifiers. `paw check` reports 0 findings
and `paw check frozen --base` against the trunk reports 0.

The migration ran as four commits, each a deletion or a one-for-one rewrite:
`## Cover` from 63 tasks; `## Verified` and `checked-at` from 71 epics;
`## Open review findings` and `checked-at` from 45 other records, the 20
specifications among them; and 40 citations of a kept run file in 35 records,
each now naming the pull request that added the file, found from git's
history. A fifth commit reworded those sentences by hand, removed the one
`## Verified` heading that carried more words, in EPC-1010, and corrected
RES-0301, which named a kept file by its path, with a line naming ADR-2300. The layout retires the field and the three sections, so `paw check`
reports one that returns.

Left alone: prose that mentions the
old sections or `project/evidence/` as history stays as it was. BUG-1360's
Closed by states a condition and no fix, so the program reads the defect as
closed; rewording a defect's closure is a change of data, not of format.

## Left alone

Nothing beyond what the epic leaves.
