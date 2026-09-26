---
id: TSK-1470
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1120
closes: [REQ-1130]
issue: 209
---

# Confirm that the merged work realises ADR-1030

One task, one branch, one pull request, one review.

## What to do

Run ADR-1030's own probes against the tree, and record what they report, because
TSK-1230 of EPC-1020 wrote the form and its check, and nothing confirmed that the decision itself was realised.

## Depends on

Nothing.

## Evidence

```text
$ python3 tools/check_prompts.py
50 shipped prompts, 0 failures
```

A probe skill added to `meow-core` with a tag nested in another, then with a
Markdown heading, then with a tag outside the five, drew 1, 2 and 3 findings
naming the probe.

## Left alone

The work itself, which is merged and unchanged.
