---
id: REQ-4122
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340
---

# REQ-4122

The meow-flow extension registers a Pi command for each method step
(`research`, `requirements`, `design`, `spec`, `epic`, `implement`, `review`)
and for the driver (`run`), the initialiser (`init`) and the onboarding
command (`onboard`). Each command loads the corresponding skill and runs the
step. The command's description is the skill's description, so the model sees
the same routing information.

Rationale: Claude Code skills with `disable-model-invocation: true` are
user-only commands. Pi commands registered with `pi.registerCommand()` are
invoked with `/command-name`. The mapping preserves the user-only nature of
the driver and the step commands while giving the model routing information
through the command descriptions.
