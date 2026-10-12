---
id: TSK-5140
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2580
closes:
  [
    REQ-0132,
    REQ-0147,
    REQ-0149,
    REQ-0151,
    REQ-0157,
    REQ-0452,
    REQ-0454,
    REQ-0456,
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-0819,
    REQ-0822,
    REQ-0823,
    REQ-2202,
    REQ-2372,
    REQ-2376,
    REQ-2390,
    REQ-2406,
    REQ-2830,
    REQ-2958,
    REQ-2960,
    REQ-2964,
    REQ-2966,
    REQ-2967,
    REQ-2968,
    REQ-2969,
    REQ-2970,
    REQ-3072,
    REQ-3900,
    REQ-3902,
  ]
issue: 1008
projected: fb826a5d7120
tracked: b678b82ddc1f
---

# Report an active requirement or decision gap

`paw check relations` reports an approved requirement with no approved ADR
that addresses or postpones it, and an approved addressing ADR with no
approved epic or direct task.

## Acceptance criteria

1. Given each missing relation and each exempt state, when the relation checks
   run, then only the two active gaps fail and name their identifiers. Closed
   by: crate fixtures for REQ-3900 and REQ-3902.
2. Given this repository, when `paw check` runs, then neither finding appears.
   Closed by: `paw check`.

## What to do

Add both determinations to the `record` feature, treat `postpones` as a
provider, and exempt decisions that only postpone because they create no
implementation plan.

## Depends on

Nothing.

## Evidence

The tests were written first and seen failing in `8941de27`, and pass after
`3990875c`. Criterion 1 closes with the five crate tests: the providerless
requirement and the planless decision are reported, a provider clears the
requirement, an approved epic clears the decision, and a postponing-only
decision names no plan, each naming REQ-3900 or REQ-3902. Criterion 2 closes
with `paw check relations` reporting 0 findings on this repository, after
ADR-2990 gave the ten stray requirements their providers and the three
decisions their direct tasks.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

Whether tasks have finished; coverage already checks their relation.
