---
id: TSK-3860
artifact: task
status: approved
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

Not yet.

## Left alone

Nothing beyond what the epic leaves.
