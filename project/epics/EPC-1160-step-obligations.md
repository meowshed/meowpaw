---
id: EPC-1160
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1160
checked-at:
---

# Every step and template carrying its obligations

Realises exactly one authorising record, ADR-1160. The epic is complete when
each of the nine step files and the `task` and `bug` templates carry every
obligation ADR-1160 places on them, traced from the tasks that close them.

## Acceptance criteria

Taken from ADR-1160, from its list of how I will know it was realised, before
the tasks below were written:

1. Every requirement ADR-1160 addresses maps, in the task that closes it, to a
   labelled rule that exists in the step file or template named.
2. `meow-method check` reports 0 findings, and every step file passes the
   prompt check.
3. A draft task without acceptance criteria fails `shape`.
4. Evaluation measures that the steps follow their rules.
5. Every requirement ADR-1160 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1520 the research and requirements steps carry their obligations
      closes: REQ-0209, REQ-0211, REQ-0213, REQ-0214, REQ-0215, REQ-0221, REQ-0222, REQ-0225, REQ-0226, REQ-0227, REQ-0229, REQ-0231, REQ-0245, REQ-0253, REQ-0271, REQ-0273, REQ-0564, REQ-2640, REQ-2642, REQ-2644, REQ-2648, REQ-2650, REQ-2869, REQ-2874, REQ-2876
      evidence: 25 requirements traced to labelled rules, in #222.

- [x] T-002 TSK-1530 the design and spec steps carry their obligations
      closes: REQ-0230, REQ-0232, REQ-0233, REQ-0235, REQ-0236, REQ-0242, REQ-0243, REQ-0244, REQ-0248, REQ-0249, REQ-0250, REQ-0251, REQ-0331, REQ-0333, REQ-0335, REQ-0337, REQ-0339, REQ-0341, REQ-0566, REQ-0613, REQ-2638, REQ-2652, REQ-2694, REQ-2858, REQ-2859, REQ-2860, REQ-2861, REQ-2862, REQ-2888, REQ-2890
      evidence: 30 requirements traced to labelled rules, in #223.

- [x] T-003 TSK-1540 the epic step carries its obligations
      closes: REQ-0239, REQ-0252, REQ-0254, REQ-0255, REQ-0256, REQ-0258, REQ-0260, REQ-0263, REQ-0264, REQ-0265, REQ-0268, REQ-0270, REQ-0285, REQ-0301, REQ-0305, REQ-0323, REQ-2892, REQ-2894, REQ-2896, REQ-2904, REQ-3100, REQ-3106, REQ-3172
      evidence: 23 requirements traced to labelled rules, in #224.

- [x] T-004 TSK-1550 the implement and document steps carry their obligations
      closes: REQ-0257, REQ-0259, REQ-0267, REQ-0269, REQ-0272, REQ-0274, REQ-0276, REQ-0290, REQ-0292, REQ-0298, REQ-0300, REQ-0450, REQ-0458, REQ-0460, REQ-0462, REQ-0464, REQ-0466, REQ-2774, REQ-3104
      evidence: 19 requirements traced to labelled rules, in #225.

- [x] T-005 TSK-1560 the verify step carries its obligations
      closes: REQ-0241, REQ-0275, REQ-0277, REQ-0278, REQ-0279, REQ-0280, REQ-0281, REQ-0282, REQ-0283, REQ-0284, REQ-0286, REQ-0288, REQ-0291, REQ-0293, REQ-0295, REQ-0296, REQ-0297, REQ-0299, REQ-0307, REQ-0317, REQ-0319, REQ-0325, REQ-0327, REQ-0329, REQ-0542
      evidence: 25 requirements traced to labelled rules, in #226.

- [x] T-006 TSK-1570 the review step carries its obligations
      closes: REQ-0304, REQ-0306, REQ-0308, REQ-0310, REQ-0311, REQ-0312, REQ-0313, REQ-0314, REQ-0315, REQ-0316, REQ-0318, REQ-0320, REQ-0322, REQ-0324, REQ-0326, REQ-0544, REQ-3108
      evidence: 17 requirements traced to labelled rules, in #227.

- [x] T-007 TSK-1580 the task and defect templates carry their obligations
      closes: REQ-0303, REQ-0534, REQ-0535, REQ-0536, REQ-0537, REQ-2900, REQ-2902, REQ-2910, REQ-2916, REQ-2917, REQ-2918, REQ-2919, REQ-2920, REQ-2922, REQ-2926
      evidence: fifteen requirements traced to template lines, and a draft
      task held to its acceptance criteria, in #228.

## Coverage

ADR-1160 addresses 154 requirements. Each lands in exactly one task
above, and `meow-method check coverage` compares the decision's `addresses`
against the union of the tasks' `closes`. The seven tasks touch different
files and can run in parallel; T-007 alone tests the part a program settles,
a draft task held to its acceptance criteria.

## Not covered

Criterion 4, measuring behaviour, waits for evaluation, which the owner
postponed, and this epic closes with it named as unmet, as REQ-3170 allows.
REQ-2897 and the increments ADR-1160 lists under what it does not settle wait
for decisions of their own.
