---
id: SPC-1020
artifact: spec
status: live
revised: 2026-10-11
states: [REQ-2750]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Measuring the harness

## Scope

The harness measures no prompt. ADR-2980 removed prompt evaluation — measuring
a prompt's behaviour with model runs — whole: the runner, the case sets, the
thresholds and the requirements that made a measurement obligatory, because
the owner will redesign it in future. This page stands to say so, and to name
what replaced the measurement: review.

What the harness says is held by the review before publishing, which
meow-prose runs on every text, and by the static and behavioural checks the
other specifications state. ADR-2840's prohibition stands: no
workflow under `.github/workflows/` runs a model call or holds a model
credential, and `tools/check_workflows.py` fails the gate on one.

What the redesign will settle — what measures a prompt after it, which cases
survive it, and whether the prose gate's acceptance joins it — is unset, and
ADR-2980 names the failure that would bring it back early: a shipped rule
change whose behaviour a reader faulted and review had passed.

## Behaviour

The harness states no measurement of a prompt, and keeps none: no runner, no
case set, no threshold and no published rate. What a change to a shipped
prompt produces is reviewed against the behaviour the material produced
before the change (REQ-2750), and the review before publishing is the one
check on the text.

## Boundary

The review before publishing is the one check on the text, and the harness
states no measurement of a prompt. This page leaves what the prompts say to
the specification of the unit that ships them, and what a redesign will
measure to the decision that asks for it, which no record has yet.

## Failure paths

| Condition                                                                | What happens                                                                                  |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| A workflow under `.github/workflows/` names a model call or a credential | `tools/check_workflows.py` fails the gate (ADR-2840)                                          |
| A change to a shipped prompt is asserted safe, not reviewed              | The move is reviewed against the behaviour the material produces, not asserted (REQ-2750)     |
| A prompt's behaviour regresses and review passed it                      | The failure that would bring the measurement back early is recorded, and the redesign decides |
