---
id: EPC-1320
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1320
---

# Source-control discipline, held by checks and by the commit skill

Realises exactly one authorising record, ADR-1320. The epic is complete when the
four settleable parts fail a check and the commit skill carries the rest.

## Acceptance criteria

Taken from ADR-1320, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `check-message` refusing a sign-off that names someone other
   than the author, `push-guard` refusing a branch named for a date or its
   author, and `check frozen` reporting an added line citing a hash as a
   revision.
2. A fixture shows each read running with prompting and paging turned off.
3. Each rule ADR-1320 places in the commit skill maps to its requirement in the
   task that closes it.
4. Every requirement ADR-1320 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1960 the sign-off names the commit's author
      closes: REQ-1312
      evidence: a fixture, and the push guard passing each commit's author, in
      #381.

- [x] T-002 TSK-1970 a branch name carries nothing the forge stores
      closes: REQ-2818
      evidence: two fixtures, the refusal and the false positive guarded, in
      #382.

- [x] T-003 TSK-1980 the record cites a pull request, never a commit hash
      closes: REQ-3176
      evidence: two fixtures, a rule in the verify step, and a run over real
      records, in #383.

- [x] T-004 TSK-1990 source control is read with prompting and paging off
      closes: REQ-2526, REQ-2528
      evidence: one environment for every read, and a fixture, in #384.

- [x] T-005 TSK-2000 the commit skill carries the branching and merging rules
      closes: REQ-1296, REQ-1298, REQ-1306, REQ-1320, REQ-1322, REQ-1324, REQ-1328, REQ-2534, REQ-2536, REQ-2538, REQ-2820, REQ-2822
      evidence: 12 requirements traced to eight rules and the signing setup, in
      #385.

## Coverage

ADR-1320 addresses 17 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The five tasks touch different units and can
run in parallel.

## Not covered

Nothing ADR-1320 addresses.
