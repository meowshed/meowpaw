---
id: REQ-NNNN
artifact: requirement
topic: <topic> # identifiers are allocated in blocks per topic, with gaps
class: functional # functional | non-functional
status: draft # draft, approved, then withdrawn or superseded; never reworded
revised: YYYY-MM-DD
elaborates: RES-NNNN # the research conclusion this rests on
verification: behavioural # static | behavioural | judgement | evaluation
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-NNNN

The <subject> MUST <one observable obligation>.

The reason, where the obligation would otherwise look arbitrary, and nothing
where the sentence above already carries it. One obligation per file, stating
what must be true and never how, because a requirement that names a mechanism
has decided what the design hasn't.
