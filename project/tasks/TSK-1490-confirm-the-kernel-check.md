---
id: TSK-1490
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1140
closes: [REQ-0077]
issue: 209
---

# Confirm that the merged work realises ADR-1060

One task, one branch, one pull request, one review.

## What to do

Run ADR-1060's own probes against the tree, and record what they report, because
the kernel check that joined the gate as `mise run kernel`, and nothing confirmed that the decision itself was realised.

## Depends on

Nothing.

## Evidence

```text
$ mise run kernel
3 kernel files, 0 names outside the kernel
```

With a line naming `meow-prose` added to `meow-core`'s style as a probe, the
check reported `plugins/meow-core/output-styles/meow.md:75: names meow-prose,
outside the kernel`.

## Left alone

The work itself, which is merged and unchanged.
