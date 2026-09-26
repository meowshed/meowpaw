---
id: SPC-1090
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#249"
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
    REQ-0209,
    REQ-0210,
    REQ-0211,
    REQ-0212,
    REQ-0213,
    REQ-0214,
    REQ-0215,
    REQ-0221,
    REQ-0222,
    REQ-0225,
    REQ-0226,
    REQ-0227,
    REQ-0228,
    REQ-0229,
    REQ-0230,
    REQ-0231,
    REQ-0232,
    REQ-0233,
    REQ-0235,
    REQ-0236,
    REQ-0239,
    REQ-0240,
    REQ-0241,
    REQ-0242,
    REQ-0243,
    REQ-0244,
    REQ-0245,
    REQ-0248,
    REQ-0249,
    REQ-0250,
    REQ-0251,
    REQ-0252,
    REQ-0253,
    REQ-0254,
    REQ-0255,
    REQ-0256,
    REQ-0257,
    REQ-0258,
    REQ-0259,
    REQ-0260,
    REQ-0263,
    REQ-0264,
    REQ-0265,
    REQ-0267,
    REQ-0268,
    REQ-0269,
    REQ-0270,
    REQ-0271,
    REQ-0272,
    REQ-0273,
    REQ-0274,
    REQ-0275,
    REQ-0276,
    REQ-0277,
    REQ-0278,
    REQ-0279,
    REQ-0280,
    REQ-0281,
    REQ-0282,
    REQ-0283,
    REQ-0284,
    REQ-0285,
    REQ-0286,
    REQ-0288,
    REQ-0290,
    REQ-0291,
    REQ-0292,
    REQ-0293,
    REQ-0294,
    REQ-0295,
    REQ-0296,
    REQ-0297,
    REQ-0298,
    REQ-0299,
    REQ-0300,
    REQ-0301,
    REQ-0302,
    REQ-0303,
    REQ-0304,
    REQ-0305,
    REQ-0306,
    REQ-0307,
    REQ-0308,
    REQ-0310,
    REQ-0311,
    REQ-0312,
    REQ-0313,
    REQ-0314,
    REQ-0315,
    REQ-0316,
    REQ-0317,
    REQ-0318,
    REQ-0319,
    REQ-0320,
    REQ-0321,
    REQ-0322,
    REQ-0323,
    REQ-0324,
    REQ-0325,
    REQ-0326,
    REQ-0327,
    REQ-0329,
    REQ-0331,
    REQ-0333,
    REQ-0335,
    REQ-0337,
    REQ-0339,
    REQ-0341,
    REQ-0390,
    REQ-0392,
    REQ-0394,
    REQ-0400,
    REQ-0402,
    REQ-0450,
    REQ-0458,
    REQ-0460,
    REQ-0462,
    REQ-0464,
    REQ-0466,
    REQ-0526,
    REQ-0528,
    REQ-0532,
    REQ-0534,
    REQ-0535,
    REQ-0536,
    REQ-0537,
    REQ-0542,
    REQ-0544,
    REQ-0564,
    REQ-0566,
    REQ-0613,
    REQ-1230,
    REQ-1231,
    REQ-1232,
    REQ-1233,
    REQ-1234,
    REQ-1235,
    REQ-1236,
    REQ-1237,
    REQ-1238,
    REQ-1239,
    REQ-1240,
    REQ-1242,
    REQ-1244,
    REQ-1246,
    REQ-1248,
    REQ-1250,
    REQ-1252,
    REQ-1254,
    REQ-1256,
    REQ-1258,
    REQ-2130,
    REQ-2131,
    REQ-2132,
    REQ-2133,
    REQ-2134,
    REQ-2137,
    REQ-2138,
    REQ-2139,
    REQ-2140,
    REQ-2256,
    REQ-2258,
    REQ-2260,
    REQ-2262,
    REQ-2264,
    REQ-2266,
    REQ-2268,
    REQ-2630,
    REQ-2632,
    REQ-2638,
    REQ-2640,
    REQ-2642,
    REQ-2644,
    REQ-2648,
    REQ-2650,
    REQ-2652,
    REQ-2694,
    REQ-2760,
    REQ-2762,
    REQ-2764,
    REQ-2766,
    REQ-2768,
    REQ-2770,
    REQ-2772,
    REQ-2774,
    REQ-2776,
    REQ-2778,
    REQ-2780,
    REQ-2782,
    REQ-2794,
    REQ-2796,
    REQ-2858,
    REQ-2859,
    REQ-2860,
    REQ-2861,
    REQ-2862,
    REQ-2869,
    REQ-2874,
    REQ-2876,
    REQ-2888,
    REQ-2890,
    REQ-2892,
    REQ-2894,
    REQ-2896,
    REQ-2900,
    REQ-2902,
    REQ-2904,
    REQ-2910,
    REQ-2916,
    REQ-2917,
    REQ-2918,
    REQ-2919,
    REQ-2920,
    REQ-2922,
    REQ-2926,
    REQ-3100,
    REQ-3104,
    REQ-3106,
    REQ-3108,
    REQ-3172,
  ]
---

# The chain

## Scope

This covers how the method's nine steps run: invoking one, the gate each
checks before it writes, the command that drives them, and the state of the
chain as the record shows it. It leaves each artifact's content rules to the
specifications of the steps that write them, and classifying trivial work to a
later decision.

ADR-1130 decides it, and EPC-1100 realised it, verified under issue 202.
ADR-1160 adds each step's obligations, and EPC-1160 realised them, verified
under issue 237 with their measurement by evaluation still to come. ADR-1170's
approvals and waiting report are verified under issue 249.

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

| Step         | Reads                                                                                                                                                                                                                                                                                                                                                                               | Writes                                 |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| research     | a question, REQ-2137, REQ-2139                                                                                                                                                                                                                                                                                                                                                      | a research record                      |
| requirements | approved research, REQ-2131, REQ-2132, REQ-2133, REQ-2134                                                                                                                                                                                                                                                                                                                           | requirement records                    |
| design       | approved requirements, REQ-1230, REQ-1231, REQ-1232, REQ-1233, REQ-1234, REQ-1235, REQ-1236, REQ-1237, REQ-1238, REQ-1239, REQ-1240, REQ-1242, REQ-1244, REQ-1246, REQ-1248, REQ-1250, REQ-1252, REQ-1254, REQ-1256, REQ-1258, REQ-2138, REQ-2140, REQ-2760, REQ-2762, REQ-2764, REQ-2766, REQ-2768, REQ-2770, REQ-2772, REQ-2776, REQ-2778, REQ-2780, REQ-2782, REQ-2794, REQ-2796 | a decision record                      |
| spec         | an approved decision, REQ-2256, REQ-2258                                                                                                                                                                                                                                                                                                                                            | the specification, updated             |
| epic         | an approved decision or defect                                                                                                                                                                                                                                                                                                                                                      | an epic and its task records           |
| implement    | an approved task, REQ-2266                                                                                                                                                                                                                                                                                                                                                          | the change, and the task's evidence    |
| document     | an epic whose tasks are all done                                                                                                                                                                                                                                                                                                                                                    | the user-facing documentation, updated |
| verify       | an epic whose tasks are all done, REQ-2260, REQ-2262, REQ-2264                                                                                                                                                                                                                                                                                                                      | the epic's verification                |
| review       | a verified epic, REQ-2268                                                                                                                                                                                                                                                                                                                                                           | findings in place, never a file        |

A person or the model invokes one step by naming it to the `method` skill, and
the step does its own work and no later step's (REQ-0192, REQ-0194). Each step
first reads the repository's principles: `CLAUDE.md` and any file the profile
names under `[method] principles` (REQ-0532). It ends by naming the artifact it
wrote and the step that picks it up (REQ-0196).

A step asks at most three clarifying questions, and chooses and records a
default for the rest (REQ-2630). A step that reviews its own output stops after
two rounds and reports what is still open (REQ-2632).

### What each step holds

Each step's file carries the obligations of its step as labelled rules, and
the `task` and `bug` templates carry the obligations of their kinds (ADR-1160).
The rules name no requirement, because the files ship to other repositories.

| Step or template | Holds                                                                                                                                                                                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| research         | REQ-0209, REQ-0211, REQ-0221, REQ-0222, REQ-0225, REQ-0226, REQ-0227, REQ-0229, REQ-0564, REQ-2640, REQ-2642, REQ-2644, REQ-2648, REQ-2650, REQ-2869                                                                                                     |
| requirements     | REQ-0213, REQ-0214, REQ-0215, REQ-0231, REQ-0245, REQ-0253, REQ-0271, REQ-0273, REQ-2874, REQ-2876                                                                                                                                                       |
| design           | REQ-0230, REQ-0232, REQ-0233, REQ-0235, REQ-0236, REQ-0249, REQ-0251, REQ-0566, REQ-2638, REQ-2652, REQ-2694, REQ-2888, REQ-2890                                                                                                                         |
| spec             | REQ-0242, REQ-0243, REQ-0244, REQ-0248, REQ-0250, REQ-0331, REQ-0333, REQ-0335, REQ-0337, REQ-0339, REQ-0341, REQ-0613, REQ-2858, REQ-2859, REQ-2860, REQ-2861, REQ-2862                                                                                 |
| epic             | REQ-0239, REQ-0252, REQ-0254, REQ-0255, REQ-0256, REQ-0258, REQ-0260, REQ-0263, REQ-0264, REQ-0265, REQ-0268, REQ-0270, REQ-0285, REQ-0301, REQ-0305, REQ-0323, REQ-2892, REQ-2894, REQ-2896, REQ-2904, REQ-3100, REQ-3106, REQ-3172                     |
| implement        | REQ-0257, REQ-0259, REQ-0267, REQ-0269, REQ-0272, REQ-0274, REQ-0276, REQ-0450, REQ-0458, REQ-0460, REQ-0462, REQ-0464, REQ-0466, REQ-2774, REQ-3104                                                                                                     |
| document         | REQ-0290, REQ-0292, REQ-0298, REQ-0300                                                                                                                                                                                                                   |
| verify           | REQ-0241, REQ-0275, REQ-0277, REQ-0278, REQ-0279, REQ-0280, REQ-0281, REQ-0282, REQ-0283, REQ-0284, REQ-0286, REQ-0288, REQ-0291, REQ-0293, REQ-0295, REQ-0296, REQ-0297, REQ-0299, REQ-0307, REQ-0317, REQ-0319, REQ-0325, REQ-0327, REQ-0329, REQ-0542 |
| review           | REQ-0304, REQ-0306, REQ-0308, REQ-0310, REQ-0311, REQ-0312, REQ-0313, REQ-0314, REQ-0315, REQ-0316, REQ-0318, REQ-0320, REQ-0322, REQ-0324, REQ-0326, REQ-0544, REQ-3108                                                                                 |
| templates        | REQ-0303, REQ-0534, REQ-0535, REQ-0536, REQ-0537, REQ-2900, REQ-2902, REQ-2910, REQ-2916, REQ-2917, REQ-2918, REQ-2919, REQ-2920, REQ-2922, REQ-2926                                                                                                     |

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

### Approvals

An approval is a record's stored status moving from `draft` to `approved`, in a
commit of its own, so it is durable and survives every session (REQ-0402). A
step that produces an artifact needing approval stops there, and never reads
silence, a change of subject or an unrelated instruction as approval
(REQ-0390, REQ-0400).

`meow-method status --waiting` prints only what waits for approval, each line
naming the artifact, its kind and the gate it waits at, and prints nothing when
nothing waits or the repository has no record (REQ-0392). A `SessionStart` hook
runs it, so a session opens with the pending approval before anything else
(REQ-0394).

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
