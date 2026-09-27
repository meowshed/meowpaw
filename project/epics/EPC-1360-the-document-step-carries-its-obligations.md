---
id: EPC-1360
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1380
checked-at:
---

# The document step writes one kind per page to the declared style, and checks documentation through the verbs

Realises exactly one authorising record, ADR-1380. The epic is complete when
the document step's file carries each obligation ADR-1380 names on a
repository's documentation, the review step's file carries the one on its
quick start, and this repository declares its documentation style.

## Acceptance criteria

Taken from ADR-1380, from its list of how I will know it was realised, before
the tasks below were written:

1. Each requirement ADR-1380 addresses is carried by a labelled rule in
   `steps/document.md` or `steps/review.md`, traced in the task's evidence,
   and no rule names a requirement, a language or a tool.
2. The prompt check passes on both step files.
3. This repository's profile declares `[docs] style`, and the document step,
   run on this epic, reports the verb that checked its documentation.
4. Every requirement ADR-1380 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2070 carry the documentation obligations in the document step,
      and declare this repository's style
      closes: REQ-0287, REQ-0289, REQ-1950, REQ-1952, REQ-1954, REQ-1956,
      REQ-1958, REQ-1960, REQ-1962, REQ-1964, REQ-2836
      evidence: rules O4 to O13 in `steps/document.md`, traced in #428.

- [x] T-002 [P] TSK-2080 have the review step follow a changed quick start
      closes: REQ-2834
      evidence: rules W11 and W12 in `steps/review.md`, in #429.

## Coverage

ADR-1380 addresses 12 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, the
document step names each page's kind, writes to the declared style and
reports the verb that checked its documentation. T-002 touches another file,
so it can run beside T-001.

## Not covered

Nothing ADR-1380 addresses. A program that checks one kind per page is left
out, as ADR-1380 says.
