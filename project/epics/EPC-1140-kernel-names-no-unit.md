---
id: EPC-1140
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1060
checked-at: "#209"
---

# A kernel that names no unit outside it

Realises exactly one authorising record, ADR-1060. The decision said it added no
task, because other epics' tasks made the change; REQ-0239 asks each decision
for its own epic, and BUG-1160 records that this one had none. The epic is
complete when its task confirms the merged work realises the decision.

## Acceptance criteria

Taken from ADR-1060, from its list of how I will know it was realised:

1. `mise run all` runs the kernel check and passes on the tree as it stands.
2. The check fails on a probe that adds `meow-prose` to a file in `meow-core`, naming the file and the line.
3. Every requirement ADR-1060 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1490 confirm that the kernel check that joined the gate as `mise run kernel` realise ADR-1060
      closes: REQ-0077
      evidence: the decision's probes, run on the tree, in #209.

## Verified

Checked under issue 209, with evidence gathered at the revision it merged:

| Criterion                                         | Evidence                                                                |
| ------------------------------------------------- | ----------------------------------------------------------------------- |
| 1. The gate runs the kernel check and passes      | `mise run kernel` reports 3 kernel files and 0 names outside the kernel |
| 2. The check fails on a probe naming `meow-prose` | It reported `meow.md:75: names meow-prose, outside the kernel`          |
| 3. Every requirement in one closed task           | `meow-method check coverage` reports 0 findings                         |

## Coverage

ADR-1060 addresses one requirement, and T-001 closes it.

## Not covered

Nothing.
