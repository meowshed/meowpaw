---
id: EPC-2550
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2640
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A check holds the method to naming no language, and every pack stays optional

Realises exactly one authorising record, ADR-2640. The epic is complete when
`tools/check_language.py` fails a method prompt that names a language, the
method runs on a repository with no pack installed, each pack states its
toolchain versions, and `meow-author check` holds a description to the words
a request contains, as SPC-1030, SPC-1080 and SPC-1190 state.

## Acceptance criteria

Taken from ADR-2640's list of how it will be known realised:

1. The check fails a fixture method prompt that names a language from the list (REQ-0070).
2. The method's steps run on a fixture repository with no pack installed and report each verb as unresolved (REQ-0088).
3. Each pack's README states the versions it is current as of (REQ-0085).
4. Every requirement ADR-2640 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-5015 fail a method prompt, template or page that names a language or a tool, with `tools/check_language.py`, and rewrite CLAUDE.md's sentence
      closes: REQ-0070, REQ-0072, REQ-0084

- [ ] T-002 [P] TSK-5020 run the method's steps on a fixture repository with no pack installed
      closes: REQ-0080, REQ-0086, REQ-0088

- [ ] T-003 [P] TSK-5025 state each pack's toolchain versions and how it prints its tool's configuration, on each pack's README
      closes: REQ-0082, REQ-0085

- [ ] T-004 [P] TSK-5030 hold a unit's description to the words a request contains, in `meow-author check`
      closes: REQ-3050

## Coverage

Each of the nine requirements ADR-2640 addresses lands in exactly one task.
TSK-5015 and TSK-5020 are the smallest set that tests the decision, because
a check that finds a language name in the method and a method that finishes
with no pack is the claim. All four tasks run in parallel.

## Not covered

Which units are kernel, method and practice, which ADR-2640 leaves to the
catalogue decision, so TSK-5015's check keeps its own list until that
decision replaces it.
