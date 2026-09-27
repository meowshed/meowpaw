---
id: TSK-2240
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1450
closes: [REQ-0139, REQ-0141]
issue: 502
projected: 588b3b4dbaf7
---

# `paw check` walks each chain and each citation's date, and `paw show` marks a suspect citation

`check coverage` reports an artifact resting on a draft provider anywhere up
its chain, and `check relations` reports a suspect citation a change can
clear. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved task closing a requirement that elaborates draft research,
   when `paw check` runs, then `coverage` names the chain and exits 1, and it
   passes once the research is approved. Closed by: a fixture naming REQ-0139,
   seen failing first.
2. Given a draft decision addressing a withdrawn requirement, when `paw check`
   runs, then `coverage` reports it. Closed by: a fixture naming REQ-0139.
3. Given a draft citing a requirement revised after it, when `paw check` runs,
   then `relations` reports the citation as suspect; given an approved record
   doing the same, `check` passes and `paw show` marks the citation with the
   target's date. Closed by: fixtures naming REQ-0141, seen failing first.
4. Given a draft citing an epic revised after it, when `paw check` runs, then
   it passes, and given the epic withdrawn, then it reports the citation.
   Closed by: a fixture naming REQ-0141.
5. Given the project record, when `paw check` runs, then it exits 0. Closed
   by: its output.

## What to do

Add the chain walk to `coverage` and the date comparison to `relations` in the
native tool's `record` feature, with epics and defects compared by status, and
mark suspect citations in `show`'s `Names` list. State nothing new in
SPC-1100, which already describes it.

## Depends on

Nothing. ADR-1470 is approved.

## Evidence

Closes REQ-0139 and REQ-0141. `plugins/meow-verbs/bin/meow-verbs run format lint
test` exits 0 with `summary: format passed, lint passed, test passed`, and the
record fixtures run 148 tests, OK. Each criterion's check:

1. `Connections.test_an_approved_task_over_draft_research_names_the_chain`
   (REQ-0139) fails before the change and passes after it; the clean-record
   fixture passes with the research approved.
2. `Connections.test_a_draft_over_a_withdrawn_requirement_is_reported`
   (REQ-0139).
3. `Connections.test_a_draft_citing_a_later_revision_is_suspect` and
   `Connections.test_an_approved_record_citing_a_later_revision_is_marked_by_show`
   (REQ-0141), both seen failing first.
4. `Connections.test_an_epic_is_suspect_by_its_status_and_not_its_date`
   (REQ-0141).
5. `plugins/meow-flow/bin/paw check` exits 0 on the project record.

The first run on the project record found three suspect citations ADR-1470
didn't count, because the one-off script read only one-line fields: SPC-1040
states REQ-2908, and SPC-1070 states REQ-3168 and REQ-3190, each written after
the specification's last `revised` date, which nobody moved when the
specification changed to state them. Both specifications now carry the date
of that change. Two older fixtures rested on what the check now reports, a
verified epic over draft research and a living specification stating a
withdrawn requirement, and each now sets up only the case it tests.

The unit is at 0.32.0, the release ADR-1390 scheduled to stop reading the
index markers from before the rename, so that reading is removed here and its
fixture now shows the old markers refused.

## Left alone

What `status` reports, which TSK-2250 adds.
