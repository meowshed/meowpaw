---
id: EPC-2810
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2890
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2810. A task and its issue are synchronised by a fingerprint of each side

This epic realises ADR-2890. It is complete when `meow-github sync` applies the
side that changed, reports an approved record's difference, and the method runs
it at the start and the end of an epic's work.

## Acceptance criteria

1. A draft takes a changed title, and an approved task gets a report and no
   write (ADR-2890, criterion 1).
2. Where both sides changed, the file's text is on the issue (ADR-2890,
   criterion 2).
3. The method's start and end steps run `meow-github sync` (ADR-2890,
   criterion 3).
4. REQ-4700, REQ-4702, REQ-4704 and REQ-4706 are each named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5320 The mapping carries the tracker side's fingerprint (done: pull request 885)
      closes: REQ-4704
      depends: nothing
- [x] T-002 TSK-5321 `meow-github sync` applies the side that changed (done: pull request 885)
      closes: REQ-4700, REQ-4702
      depends: TSK-5320 (blocking) - the command compares the two fingerprints
- [x] T-003 TSK-5322 The method runs the synchronisation and the script is retired (done: pull request 885)
      closes: REQ-4706
      depends: TSK-5321 (blocking) - the steps name the command

## Coverage

REQ-4704 lands in TSK-5320, REQ-4700 and REQ-4702 in TSK-5321, and REQ-4706 in
TSK-5322.

## Not covered

- A tracker other than GitHub Issues.
