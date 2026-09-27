---
id: TSK-2240
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1450
closes: [REQ-0139, REQ-0141]
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

Not yet.

## Left alone

What `status` reports, which TSK-2250 adds.
