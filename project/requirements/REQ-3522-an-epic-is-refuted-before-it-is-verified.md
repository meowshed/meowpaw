---
id: REQ-3522
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0309, RES-0070
verification: static
---

# REQ-3522

**Withdrawn by ADR-2300.**

It read: before an epic's verification is recorded, an agent that didn't produce its work MUST have tried to refute that each requirement the epic's authorising record addresses is met, and the verification records that agent's outcome for each such requirement: refuted, naming the input or condition that breaks it, not refuted, or not judged, naming what the agent couldn't reach. Where the verification runs somewhere it can't dispatch an agent, it records instead that the refutation wasn't attempted, and names that cause.

The session that verifies an epic is usually the one that implemented it, and
a model judging its own work is measurably biased, and capability doesn't
correct it (RES-0070). Four requirements this repository recorded as verified
were unmet, each on a check that couldn't fail or an input no check tried,
but that count is a floor and ordinary later work found all four, so the case
rests on the bias more than on the four (RES-0309).

The outcome is recorded per requirement because a record that says nothing
when the agent ran can't be told apart from one where it never ran. The best
outcome is "not refuted", never "met", because an agent that finds no break
has shown only that it found none. The exception is limited to a place that
can't dispatch, such as a verification running inside a subagent, and its
cause is written down, so a reader can see whether the reason applies and
nobody reads the epic as independently checked.

ADR-2300 removes the verification step and the skeptic, so no step is left for this rule to bind.
