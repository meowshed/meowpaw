---
id: EPC-2760
artifact: epic
status: done
revised: 2026-10-10
realises: ADR-2850
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# EPC-2760. The five verification obligations are called stages

This epic realises ADR-2850. It is complete when a profile declares the five
under `[stages]`, a `[verbs]` table still resolves and says what to use, and a
check holds living and shipped text to the word.

## Acceptance criteria

1. A profile with a `[stages]` table resolves the five, and a profile with a
   `[verbs]` table still resolves them and reports `[stages]` (ADR-2850,
   criterion 1).
2. A check fails, naming the file and the line, on "verb" in a living or
   shipped file outside its allow-list (ADR-2850, criterion 2).
3. REQ-4200, REQ-4202 and REQ-4204 are each named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [x] T-001 TSK-5270 The profile reads `[stages]` and reports `[verbs]` as deprecated (done: pull request 875)
      closes: REQ-4202, REQ-4204
      depends: nothing
- [x] T-002 TSK-5271 Living and shipped text says "stage" (done: pull request 876)
      closes: REQ-4200
      depends: TSK-5270 (blocking) - the pages say a profile declares `[stages]`, and that has to work
- [x] T-003 TSK-5272 A check fails on "verb" in living and shipped text (done: pull request 877)
      closes: REQ-4200
      depends: TSK-5271 (blocking) - the check fails on every page until the pages change

## Coverage

REQ-4202 and REQ-4204 land in TSK-5270. REQ-4200 lands in TSK-5271, which
changes the text, and in TSK-5272, which holds it. TSK-5270 and TSK-5271 are
the smallest set that would show the decision realised, and TSK-5272 keeps it
so.

## Not covered

- Removing the read of `[verbs]`. It lands in the second release after the one
  that adds `[stages]` (REQ-4204), as a task written then, because the release
  that does it doesn't exist yet.
- Renaming the Rust modules and directories named for "verbs" (ADR-2850, "What
  this does not settle").
