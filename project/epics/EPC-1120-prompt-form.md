---
id: EPC-1120
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1030
checked-at: "#209"
---

# Every shipped prompt in one form of top-level tags

Realises exactly one authorising record, ADR-1030. The decision said it added no
task, because other epics' tasks made the change; REQ-0239 asks each decision
for its own epic, and BUG-1160 records that this one had none. The epic is
complete when its task confirms the merged work realises the decision.

## Acceptance criteria

Taken from ADR-1030, from its list of how I will know it was realised:

1. `tools/check_prompts.py` passes on every shipped prompt, and fails on probes with a nested tag, a heading, and a tag outside the five.
2. The loop's table shows this form against the nested one on both models.
3. Every requirement ADR-1030 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1470 confirm that TSK-1230 of EPC-1020 wrote the form and its check realise ADR-1030
      closes: REQ-1130
      evidence: the decision's probes, run on the tree, in #209.

## Verified

Checked under issue 209, with evidence gathered at the revision it merged:

| Criterion                                             | Evidence                                                                                                                                           |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. The prompt check passes, and fails on three probes | `check_prompts` reports 50 shipped prompts and 0 failures; probes with a nested tag, a heading and a tag outside the five drew 1, 2 and 3 findings |
| 2. The loop's table shows the form on both models     | Not met: the measurement is evaluation, which the owner postponed, and REQ-3170 lets the epic close with this named                                |
| 3. Every requirement in one closed task               | `meow-method check coverage` reports 0 findings                                                                                                    |

## Coverage

ADR-1030 addresses one requirement, and T-001 closes it.

## Not covered

Criterion 2 is unmet, as the table says, and waits for evaluation.
