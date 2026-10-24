---
id: ADR-3010
artifact: adr
status: approved
revised: 2026-10-24
addresses: []
postpones:
  [
    REQ-1364,
    REQ-1366,
    REQ-1370,
    REQ-1390,
    REQ-1398,
    REQ-2562,
    REQ-2570,
    REQ-2584,
    REQ-2586,
    REQ-2588,
    REQ-2824,
  ]
supersedes: [ADR-2540]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3010. The tracker projection stays flat, and a tracker's grouping is not written

## Decision

I supersede ADR-2540 and postpone the eleven requirements that TSK-5155 would
have closed: REQ-1364, REQ-1366, REQ-1370, REQ-1390, REQ-1398, REQ-2562,
REQ-2570, REQ-2584, REQ-2586, REQ-2588 and REQ-2824. TSK-5155 and its epic
EPC-2600 are withdrawn. The projection of ADR-1310 stays as it is, one issue
for each task.

ADR-2540 asked the harness to write a parent issue for each epic with its tasks
as sub-issues. REQ-3320, which ADR-1800 approved, forbids writing any grouping
of a task other than its epic or defect, on a tracker or in the record, and
names a parent issue. The two records cannot both hold, and the guard exists:
`meow-github` refuses a `--parent` and its test
`test_project_groups_an_issue_nowhere` fails one.

Once this is accepted, no approved record asks for a grouping on a tracker. What
still doesn't work: an epic shows on GitHub as no parent, and four requirements
that don't depend on grouping, REQ-1398, REQ-2562, REQ-2570 and REQ-2824, wait
with the rest because TSK-5155 scoped them into the same rewrite.

## Why

ADR-1800 rests on RES-0289 and RES-0022. They found that a sub-issue doesn't
close by keyword and that a grouping the record doesn't hold is a second plan,
and nothing since contradicts them. I take the harness's flat projection to be
the simpler design, and the one the owner's rule against a tracker that plans
for the record already describes.

## Alternatives

| Option                                                    | Better at                                        | Why it lost                                                                                                               |
| --------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                | Keeps both records                               | They contradict each other, and TSK-5155 can't be built without breaking the check that guards REQ-3320                   |
| Withdraw REQ-3320 instead                                 | An epic is visible as one parent issue           | Reopens ADR-1800's finding and the forbidden-fields check, and the tracker then holds a plan the record doesn't           |
| Keep the four independent requirements as a narrower task | Closes REQ-1398, REQ-2562, REQ-2570 and REQ-2824 | I know of no failure of the projection as it stands, and a failure that appears is a defect, which authorises its own fix |

## What it costs

An epic has no parent issue, and the four requirements above wait until
something fails or the owner asks for them.

## What would reverse it

- The owner asks for a tracker grouping, or a second tracker pack is written,
  or the flat projection loops, passes a converted field value or collapses a
  pending check into a failure.

## Consequences

Eleven requirements read as postponed. ADR-2540 reads as superseded, and
TSK-5155 and EPC-2600 are withdrawn.

## How I will know it was realised

1. `paw status` lists the eleven under Postponed and names no `next:` for
   EPC-2600.
2. `paw check` reports no finding, and no approved record asks for a parent
   issue.

## What this does not settle

- Whether a later tracker pack, such as Linear's, may group items, which REQ-3320
  would first have to allow.
