---
id: EPC-1130
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1040
checked-at: "#209"
---

# The reply shape carried to every subordinate agent

Realises exactly one authorising record, ADR-1040. The decision said it added no
task, because other epics' tasks made the change; REQ-0239 asks each decision
for its own epic, and BUG-1160 records that this one had none. The epic is
complete when its task confirms the merged work realises the decision.

## Acceptance criteria

Taken from ADR-1040, from its list of how I will know it was realised:

1. `fragments/reply-shape.md` does not exist, and the style's R10 names the style's own rules block.
2. `tools/check_subagent_shape.py` fails on a probe unit that dispatches without naming `output-styles/meow.md`, and passes on the tree.
3. Every requirement ADR-1040 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1480 confirm that TSK-1230 of EPC-1020 made the change and TSK-1030 of EPC-1000 wrote the check realise ADR-1040
      closes: REQ-0954
      evidence: the decision's probes, run on the tree, in #209.

## Verified

Checked under issue 209, with evidence gathered at the revision it merged:

| Criterion                                                     | Evidence                                                                                   |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1. The fragment is gone and R10 names the rules block         | `plugins/meow-core/fragments/` doesn't exist; R10 names the style's rules block            |
| 2. The subagent check fails on a probe and passes on the tree | 0 without the shape on the tree; the probe agent is named as dispatching without the shape |
| 3. Every requirement in one closed task                       | `meow-method check coverage` reports 0 findings                                            |

## Coverage

ADR-1040 addresses one requirement, and T-001 closes it.

## Not covered

Nothing.
