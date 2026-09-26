---
id: EPC-1060
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1090
checked-at:
---

# The git pack, refusing a commit on the trunk and checking a push

Realises exactly one authorising record, ADR-1090. The epic is complete when
`meow-git` refuses a commit on the declared trunk, checks every commit a push
would publish for the declared convention and for a good signature, reports
the message check as unrun where `meow-scm` is absent, and this repository
declares its trunk and its signing policy.

## Acceptance criteria

Taken from ADR-1090, from its list of how I will know it was realised, before
the task below was written:

1. A `git commit` on the declared trunk is blocked, naming the trunk, and one
   on another branch runs.
2. A push that would add a commit whose message fails `meow-scm check-message`
   is blocked, naming the commit and the failure.
3. With `meow-scm` absent, the push hook reports the message check as unrun
   and doesn't claim it passed.
4. With `require_signatures`, a push adding an unsigned commit is blocked, and a
   commit whose key material is missing locally is reported as unverifiable.
5. With no `[git]` table, nothing is refused on commit, and the push checks
   messages and says the trunk and the policy are undeclared.
6. Every requirement ADR-1090 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1320 `plugins/meow-git/`: the hooks, the program, the
      fixtures over scratch repositories, the page, the budget, the
      marketplace entry and this repository's `[git]` table
      closes: REQ-0079, REQ-1292, REQ-1326, REQ-2530

## Coverage

ADR-1090 addresses four requirements, and the one task closes all of them,
which `tools/check_coverage.py` compares against the decision's `addresses`.
The pack is one reviewable change, so it is one task.

## Not covered

Nothing ADR-1090 addresses is left out. Worktrees, stacked branches, the squash
merge and enforcement on the forge are outside this epic.
