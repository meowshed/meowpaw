---
id: EPC-1540
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1570
checked-at:
---

# The harness reads git unescaped and without locks, keeps to the repository's configuration, and releases a breaking change as it is marked

Realises exactly one authorising record, ADR-1570. The epic is complete when
every path listing reads NUL-separated, git reads go through the lock-free
helper, no shipped source writes global configuration, and the release
refuses a breaking change without the version showing it.

## Acceptance criteria

Taken from ADR-1570, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show the record check and the evidence listing reading a path
   holding a newline, a quote and a non-ASCII character as it is.
2. Unit tests show the reading helper setting `GIT_OPTIONAL_LOCKS=0`, and
   fail on a source, a shipped prompt or a workflow naming `git config` with
   `--global`.
3. A unit test fails on a source that starts git outside the reading helper.
4. A test of the release check refuses a breaking commit with a patch bump,
   accepts it with a minor one at zero and a major one above zero, and holds
   each unit a commit touches, every binary-shipping unit for a commit
   touching `crates/meow/`.
5. Every requirement ADR-1570 addresses lands in exactly one closed task, and
   REQ-2532 and REQ-2544 read as postponed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2400 read paths with `-z`, hold the lock-free helper and the
      configuration rule with unit tests
      closes: REQ-2522, REQ-2524, REQ-2540
      evidence: two path fixtures and the configuration scan seen failing
      first, in #571.

- [x] T-002 [P] TSK-2410 refuse a release of a breaking change without the
      version showing it
      closes: REQ-3192
      evidence: six tests of the new check, and the check passing on this
      repository, in #572.

## Coverage

ADR-1570 addresses 4 requirements, and each lands in exactly one task above.
T-002 changes the release workflow and T-001 the native tool, so they can run
side by side.

## Not covered

REQ-2532 and REQ-2544, which ADR-1570 postpones with their conditions.
