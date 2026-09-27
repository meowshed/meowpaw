---
id: TSK-2080
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1360
closes: [REQ-2834]
issue: 429
projected: f4dc85e00095
---

# The review step follows a changed quick start, or says it only read it

The review step's file carries a labelled rule: a review of a change to a
quick start follows it from an empty directory, and where it can't, reports
that it read the quick start and didn't run it. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given `steps/review.md`, when it is read, then a labelled rule carries
   REQ-2834 with its reason, and names no requirement, language or tool.
   Closed by: the rule, traced in the evidence.
2. Given the step files, when `mise run prompts` runs, then it passes. Closed
   by: its output.

## What to do

Add the rule to `steps/review.md`, and a line to the step's numbered steps
where a change touches a quick start. Add the second rule ADR-1380 gives the
review step, judging each changed page against the kind it names, which
holds REQ-1952 and REQ-1954 as a judgement beside the document step's rules.

## Depends on

Nothing. It changes a different file from TSK-2070, so the two can run in
either order.

## Evidence

`steps/review.md` carries two new labelled rules and a numbered step for a
change that touches documentation. W11 carries REQ-2834: follow a changed
quick start from an empty directory, and report it as read and not run where
that can't be done. W12 judges each changed page against the kind it names,
holding REQ-1952 and REQ-1954 as a judgement beside the document step's O5
and O6, which close them. A search of the file for record identifiers finds 0.

```text
$ python3 tools/check_prompts.py
52 shipped prompts, 0 failures
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

## Left alone

The document step, which TSK-2070 changes.
