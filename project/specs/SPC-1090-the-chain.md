---
id: SPC-1090
artifact: spec
status: live
revised: 2026-09-26
checked-at:
states:
  [
    REQ-0190,
    REQ-0192,
    REQ-0194,
    REQ-0196,
    REQ-0198,
    REQ-0200,
    REQ-0202,
    REQ-0204,
    REQ-0206,
    REQ-0208,
    REQ-0210,
    REQ-0212,
    REQ-0228,
    REQ-0240,
    REQ-0294,
    REQ-0302,
    REQ-0321,
    REQ-0526,
    REQ-0528,
    REQ-0532,
    REQ-2630,
    REQ-2632,
  ]
---

# The chain

## Scope

This covers how the method's nine steps run: invoking one, the gate each
checks before it writes, the command that drives them, and the state of the
chain as the record shows it. It leaves each artifact's content rules to the
specifications of the steps that write them, and classifying trivial work to a
later decision.

ADR-1130 decides it and EPC-1100 realises it, so `checked-at` stays empty until
that epic closes.

## Boundary

| Surface                                      | What it is                                              |
| -------------------------------------------- | ------------------------------------------------------- |
| `plugins/meow-method/skills/method/SKILL.md` | What every step shares, and how to invoke one           |
| `plugins/meow-method/skills/method/steps/`   | One file per step, read only for the step being run     |
| `plugins/meow-method/skills/run/SKILL.md`    | `/meow-method:run`, the command that drives the chain   |
| `plugins/meow-method/templates/<kind>.md`    | The unit's template for each kind                       |
| `.meowpaw/templates/<kind>.md`               | A repository's own template, which overrides the unit's |
| `meow-method status`, `ready`, `template`    | The chain's state, a step's gate, the template in force |

## Behaviour

### The steps

The chain has nine steps in this order, each writing one kind of artifact
(REQ-0190):

| Step         | Reads                            | Writes                                 |
| ------------ | -------------------------------- | -------------------------------------- |
| research     | a question                       | a research record                      |
| requirements | approved research                | requirement records                    |
| design       | approved requirements            | a decision record                      |
| spec         | an approved decision             | the specification, updated             |
| epic         | an approved decision or defect   | an epic and its task records           |
| implement    | an approved task                 | the change, and the task's evidence    |
| document     | an epic whose tasks are all done | the user-facing documentation, updated |
| verify       | an epic whose tasks are all done | the epic's verification                |
| review       | a verified epic                  | findings in place, never a file        |

A person or the model invokes one step by naming it to the `method` skill, and
the step does its own work and no later step's (REQ-0192, REQ-0194). Each step
first reads the repository's principles: `CLAUDE.md` and any file the profile
names under `[method] principles` (REQ-0532). It ends by naming the artifact it
wrote and the step that picks it up (REQ-0196).

A step asks at most three clarifying questions, and chooses and records a
default for the rest (REQ-2630). A step that reviews its own output stops after
two rounds and reports what is still open (REQ-2632).

### The gate

Before it writes, a step runs `meow-method ready <step> <id>...` with the
identifiers of its input. `ready` exits 0 when every input exists and is
approved, and 1 when one isn't, naming each missing or unapproved input on its
own line (REQ-0198, REQ-0200). The step refuses on 1 and says what is missing.

| Step         | Its input is ready when                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| research     | always                                                                                                    |
| requirements | each named research record is approved (REQ-0212)                                                         |
| design       | each named requirement is approved (REQ-0228)                                                             |
| spec         | the named decision is approved (REQ-0240)                                                                 |
| epic         | the named decision or defect is approved, and a decision's requirements are all stated by a specification |
| implement    | the named task and its epic are approved, and each task it depends on is done                             |
| document     | every task of the named epic is done or dropped                                                           |
| verify       | every task of the named epic is done or dropped (REQ-0294)                                                |
| review       | the named epic carries `checked-at` (REQ-0302)                                                            |

A task is done when its epic marks it `[x]`, and dropped when it is marked
`[~]`. The tasks a task depends on are the `TSK-` identifiers under its
`## Depends on` section.

### The state

`meow-method status` prints the chain's state, computed from the record each
time it runs. It leads with every research, requirement, decision, epic, task
and defect record whose status is `draft`, under "Waiting for approval"
(REQ-0321). Then, for each approved decision, it prints the step the decision
has reached and the next one:

- no epic realises it: next is `spec`, then `epic`
- its epic is a draft: waiting for the epic's approval
- its epic has tasks not done: next is `implement` with the first task whose
  dependencies are done
- every task is done and the epic has no `checked-at`: next is `document`, then
  `verify`
- the epic carries `checked-at`: realised

Run twice with nothing changed, it prints the same text (REQ-0210).

### The driver

`/meow-method:run` runs `status`, and takes the first item that isn't waiting,
or the record a person names (REQ-0202). It runs that item's next step through
the `method` skill, and stops where the step ends at an approval gate, as the
step would (REQ-0204). At every stop it reports which step it reached, why it
stopped and what the next invocation will do (REQ-0208). It keeps no state of
its own, so run again after an approval it continues from the step after the
approved one, and run again with nothing approved it says it is waiting
(REQ-0206, REQ-0210).

### Templates

A step writes each artifact from the template `meow-method template <kind>`
names: `.meowpaw/templates/<kind>.md` where the repository has it, and the
unit's `templates/<kind>.md` otherwise (REQ-0526, REQ-0528). The kinds are
`research`, `requirement`, `adr`, `spec`, `epic`, `task`, `bug`, `vision` and
`constitution`.

## Failure paths

| Condition                                 | What happens                                               |
| ----------------------------------------- | ---------------------------------------------------------- |
| `ready` names an input that doesn't exist | Exit 1, the input named as missing                         |
| `ready` for a step it doesn't know        | Exit 2, naming the nine steps                              |
| `template` for a kind it doesn't know     | Exit 2, naming the kinds                                   |
| The record's root doesn't exist           | `status` and `ready` say so and exit 1, as `check` does    |
| No binary for the machine                 | The launcher reports the record as not checked and exits 3 |
