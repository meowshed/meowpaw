---
id: EPC-1000
artifact: epic
status: approved
revised: 2026-09-21
unit: U-0001
realises: ADR-1000
checked-at:
---

# The reply shape, carried by the kernel

Realises exactly one authorising record, ADR-1000, which is what gives this
epic an end: it is complete when a repository installing `meow-core` receives
the reply shape, no unit is exempt from it, and a change to it can be measured.

## Acceptance criteria

**Criterion 1 fails, so this epic is not realised.** Verification at `4e75d4f`
observed a new session using the platform default with the kernel enabled,
which BUG-1040 records. The five tasks are closed with evidence and the
decision they realise does not hold.

Taken from ADR-1000 before the tasks below were written:

1. A repository with `meow-core` installed and no other unit receives the
   shape, and it is in force without the person selecting it.
2. The style check fails on a style whose `keep-coding-instructions` is false,
   and on a rule that ships no condition under which it yields.
3. A subordinate agent dispatched by a shipped unit answers in the shape.
4. The evaluation runs against an unshaped baseline, publishes a weighted
   delta, and states its trial count and its judge.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1010 `plugins/meow-core/`: the manifest, the version and the
      marketplace entry
      closes: REQ-0932
      evidence: `claude plugin install meow-core@meowpaw` then
      `claude plugin list`, which prints the plugin at version 0.1.0 and
      enabled, at `998117f`. REQ-0932 became true with T-002, which is what
      put a shape in the kernel, and the review of #14 says so.

- [x] T-002 TSK-1020 the output style carrying the eight rules and their
      conditions
      closes: REQ-0930, REQ-0933, REQ-0934, REQ-0936, REQ-0938, REQ-0940,
      REQ-0942, REQ-0944, REQ-0946, REQ-0948, REQ-0950, REQ-0952
      depends: TSK-1010 - the style ships inside the plugin and has nowhere to
      live before it
      evidence: `/reload-plugins` then `/output-style`, which lists
      `meow-core:meow` and sets it, at `b228817`. The style has been in force
      in this session since.

- [x] T-003 [P] TSK-1030 the shape fragment a subordinate agent's prompt
      carries
      closes: REQ-0954
      depends: TSK-1020 - the fragment restates the rules and cannot precede
      them
      evidence: `tools/check_subagent_shape.py`, seen failing on a unit that
      dispatches without naming the fragment and passing on the tree. No
      shipped unit dispatches a subordinate agent yet, so no dispatched reply
      has been observed, and the check is what holds the obligation until one
      does.

- [x] T-004 [P] TSK-1040 the static check over the style
      closes: REQ-0931
      depends: TSK-1020 - the check has nothing to read before the style exists
      evidence: `tools/check_style.py`, seen failing on a style with
      `keep-coding-instructions: false` and on a rule stating no condition
      under which it yields, then passing on the shipped style, at `a689e20`.
      It runs in the gate as `mise run style`.

- [x] T-005 [P] TSK-1050 the evaluation: a case set, a rubric and a blind judge
      closes: REQ-0956
      depends: TSK-1020 - the shape under measurement is the one the style
      carries
      evidence: `claude plugin eval plugins/meow-core --runs 5 --trust-plugin`
      at `8f9e8dd`: forty runs, no errors, mean Δ +0.06. One case moved,
      `error-report` at +0.25, and its arms overlap run by run. The other three
      score 1.00 in both arms and discriminate nothing. TSK-1050 carries the
      table and what it does not support.

## Coverage

ADR-1000 addresses sixteen requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`, failing on a requirement in neither or in two.

The smallest subset that would test the decision is T-001 and T-002: with those
two closed, a repository installs the kernel and the shape holds, which is the
claim ADR-1000 makes. T-004 and T-005 make it checkable and measurable, and
T-003 extends it to where a style does not reach.

The thing measurable before the epic finishes is T-005's weighted delta against
the unshaped baseline, on the rubric REQ-0956 requires.

## Not covered

REQ-2774 names the harness's not-working states: unresolved, tool absent, tool
broken, untrusted, skipped and unreachable. It sits in the reporting topic and
belongs to verb resolution, which no decision has created yet, so we defer it to
the decision that does and drop none of it.

REQ-0936 obliges a progress report to be computed from the artifacts, and the
tasks below state that obligation in the style without building the command that
computes it. Until such a command exists, a reply says that the record holds
nothing to compute from.

We create `meow-core` here because the reply shape needs somewhere to ship, and
we decide nothing about what else the kernel carries.
