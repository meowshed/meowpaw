---
id: EPC-1110
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1140
checked-at:
---

# Each kind's content rules, checked with the scope the frozen record allows

Realises exactly one authorising record, ADR-1140. The epic is complete when
`meow-method check` holds each kind's content rules as the layout declares
them, a draft meets every rule, and the approved record passes as it does
today.

## Acceptance criteria

Taken from ADR-1140, from its list of how I will know it was realised, before
the tasks below were written:

1. A draft research record with an undated source fails `meow-method check
rules`, naming the line, and the approved record's undated sources don't.
2. A draft decision without a section saying how it will be known realised
   fails `shape`, and ADR-1000 doesn't.
3. A requirement carrying `priority` fails `front-matter`, draft or approved.
4. `meow-method check` on this repository reports 0 findings.
5. Every requirement ADR-1140 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1450 the layout's content rules and their scope: sections,
      drafts-only sections, the opening section, fields required and
      forbidden, with a fixture for each
      closes: REQ-0216, REQ-0219, REQ-0234, REQ-0247, REQ-0266, REQ-0309, REQ-0512, REQ-0514, REQ-0538, REQ-0540, REQ-0546, REQ-0556, REQ-0560, REQ-0562, REQ-0587, REQ-0588, REQ-0589, REQ-0592, REQ-0593, REQ-2668, REQ-2864, REQ-2866, REQ-2878, REQ-2884, REQ-2886, REQ-2898, REQ-2912, REQ-2914, REQ-2923, REQ-2924, REQ-3102
      evidence: ten fixtures, each rule and scope, seen failing against a
      stub, in #199.

- [x] T-002 TSK-1460 the `rules` check: dated sources, research citing no
      requirement, a judged requirement's verifier, an epic realising one
      record, and the alternatives' reason
      closes: REQ-0223, REQ-0262, REQ-0558, REQ-2868, REQ-2882
      depends: TSK-1450 - the rules read the scope the layout declares
      evidence: five fixtures, each rule and its scope, seen failing against a
      stub, in #200.

## Coverage

ADR-1140 addresses thirty-six requirements. Each lands in exactly one task
above, and `meow-method check coverage` compares the decision's `addresses`
against the union of the tasks' `closes`. T-001 alone tests the decision: a
draft held to a rule the frozen record isn't.

## Not covered

Generating the indexes, rules that need judgement, and correcting the frozen
records that break a drafts-only rule, as ADR-1140 says.
