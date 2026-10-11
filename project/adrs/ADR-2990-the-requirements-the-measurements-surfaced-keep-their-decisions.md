---
id: ADR-2990
artifact: adr
status: approved
revised: 2026-10-11
addresses:
  [
    REQ-2798,
    REQ-2800,
    REQ-2928,
    REQ-3074,
    REQ-3196,
    REQ-4300,
    REQ-4510,
    REQ-4616,
    REQ-4620,
    REQ-4622,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2990. The requirements the measurements surfaced keep the decisions their behaviour came from

## Decision

RES-0354 measured the harness on its own trunk and wrote nine requirements
whose behaviour was already decided elsewhere but whose provider relation was
never written, and REQ-2928 joined them from BUG-1680. This amendment gives
each one the decision whose behaviour holds it, the way ADR-2740 restored its
own batch, and changes no behaviour.

- REQ-2798, the judge asked only where the command publishes text: ADR-2700,
  which names the prose gate's judge call as the one hook exception and
  bounds its scope.
- REQ-2800, a warm `paw` invocation within a second: ADR-1480, whose ledger
  is what a warm invocation reads instead of the whole run.
- REQ-2928, a check measures the tree under review: ADR-1480, whose tree
  binding is the relation the installed-release preference broke.
- REQ-3074, the trunk's gate passes: ADR-1610, which binds this repository's
  five stages to the tasks the gate composes.
- REQ-3196 and REQ-4622, a unit's description and page agreeing across both
  trees: ADR-2820, which mirrors each unit one to one and releases both
  distributions on one tag.
- REQ-4300, the test stage within five minutes: ADR-1610, which owns the
  stage composition the timing holds.
- REQ-4510, a launcher resolves its binary once: ADR-2870, whose one build
  and data marker are what the launcher resolves.
- REQ-4616, a run starts from a Pi session: ADR-2780, which ships the
  extensions the Pi session runs.
- REQ-4620, a launcher and extension generated from one template: ADR-2780,
  which ships both distributions' material from the shared tree.

Once this is accepted, every requirement RES-0354 and BUG-1680 surfaced names
its provider, and `paw check`'s relations pass on this repository. What still
doesn't work: nothing this decision names changes behaviour; where a
behaviour behind one of these requirements drifts, the defect goes to the
decision named here.

## Why

RES-0354 found the record keeping requirements whose provider relations were
missing, and the record check ADR-2740 commissioned reports them. Writing the
relation is the repair the method asks for, because a requirement nobody
authorized can't be told from a gap nobody noticed.

## Alternatives

| Option                        | Better at             | Why it lost                                                         |
| ----------------------------- | --------------------- | ------------------------------------------------------------------- |
| Leave the strays unaddressed  | No new record         | The check reports ten requirements in force with no provider         |
| Withdraw the ten              | Fewer relations       | Each states a behaviour the tree holds and a test pins               |
## Consequences

The ten requirements name providers, so the record's coverage and relations
read them as part of the decisions whose behaviour holds them, and a defect
against one goes to that decision's record.

## What it costs

One decision record and its task, and the read of nine requirement bodies to
place each provider honestly.

## What would reverse it

A requirement whose behaviour no decision named here holds: the amendment
moves its provider, or a later record withdraws this one naming the
replacement.
