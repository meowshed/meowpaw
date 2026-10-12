---
id: TSK-5650
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2900
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State that the model may invoke the driver, and pin it

ADR-2900 drops `disable-model-invocation` from `/meow-flow:run` alone, and
the behaviour holds: `plugins/meow-flow/skills/run/SKILL.md` carries no such
field, while the loop's run skill keeps it, because only a person starts a
run. The task states it in the specification and pins it with a test
(REQ-3902).

## Acceptance criteria

1. Given `plugins/meow-flow/skills/run/SKILL.md`, when a test reads its front
   matter, then it carries no `disable-model-invocation`, and
   `plugins/meow-loop/skills/run/SKILL.md` carries `true`. Closed by: a test
   in `plugins/meow-flow/tests/`, seen failing first where it is absent.
2. Given the specification, when a reader reads SPC-1090's section on the
   driver, then it states the model may invoke the driver and the loop stays
   person-only. Closed by: the section's own text.

## What to do

Add the test beside `test_run_skill.py`, and the sentence beside the driver's
row in SPC-1090's table of what the chain runs.

## Depends on

Nothing.

## Evidence

Criterion 1 closes with
`plugins/meow-flow/tests/test_run_skill.py::Invocable::test_the_driver_is_invokable_and_the_loop_is_not`,
which reads both run skills' front matter. Criterion 2 closes with SPC-1090's
"The driver" section, which states the model may invoke the driver and the
loop stays person-only.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

Whether a model follows the instruction, which the evals measure by hand.
