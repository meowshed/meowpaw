---
id: TSK-1480
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1130
closes: [REQ-0954]
issue: 209
---

# Confirm that the merged work realises ADR-1040

One task, one branch, one pull request, one review.

## What to do

Run ADR-1040's own probes against the tree, and record what they report, because
TSK-1230 of EPC-1020 made the change and TSK-1030 of EPC-1000 wrote the check, and nothing confirmed that the decision itself was realised.

## Depends on

Nothing.

## Evidence

`plugins/meow-core/fragments/` doesn't exist, and the style's R10 names the
`<rules name="the reply shape">` block. `tools/check_subagent_shape.py`
reports "1 dispatches a subordinate agent, 0 without the shape" on the tree,
and on a probe agent that dispatches without naming `output-styles/meow.md`
it reports "dispatches without the shape: plugins/meow-core/agents/probe.md".

## Left alone

The work itself, which is merged and unchanged.
