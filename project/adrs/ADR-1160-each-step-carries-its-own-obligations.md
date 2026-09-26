---
id: ADR-1160
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [
    REQ-0209,
    REQ-0211,
    REQ-0213,
    REQ-0214,
    REQ-0215,
    REQ-0221,
    REQ-0222,
    REQ-0225,
    REQ-0226,
    REQ-0227,
    REQ-0229,
    REQ-0230,
    REQ-0231,
    REQ-0232,
    REQ-0233,
    REQ-0235,
    REQ-0236,
    REQ-0239,
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
    REQ-0295,
    REQ-0296,
    REQ-0297,
    REQ-0298,
    REQ-0299,
    REQ-0300,
    REQ-0301,
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
    REQ-0450,
    REQ-0458,
    REQ-0460,
    REQ-0462,
    REQ-0464,
    REQ-0466,
    REQ-0534,
    REQ-0535,
    REQ-0536,
    REQ-0537,
    REQ-0542,
    REQ-0544,
    REQ-0564,
    REQ-0566,
    REQ-0613,
    REQ-2638,
    REQ-2640,
    REQ-2642,
    REQ-2644,
    REQ-2648,
    REQ-2650,
    REQ-2652,
    REQ-2694,
    REQ-2774,
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
supersedes: []
---

# 1160. Each step's file carries the obligations of its step, and each template those of its kind

## Decision

Every obligation on how a step works goes into that step's file under
`plugins/meow-method/skills/method/steps/`, as a labelled rule the model reads
when it runs the step: what research challenges before it compares, how a
requirement is worded, what a decision records, how a specification divides,
how an epic decomposes, what implementation stops for, what verification may
and may not touch, and what review reports. The obligations on what a task or
a defect record contains go into its template, which the step writes from.

A step file ships to other repositories, where this repository's requirement
identifiers mean nothing, so a rule names no identifier. Each rule carries a
label, such as `R1` in `steps/research.md`, and each task of the epic maps the
requirements it closes to the labels that carry them, so the trace lives in
the record and the prompt stays the prompt.

The rules the program already settles stay in the program: the gates,
the content checks and the relations. A step file tells the model to run them
and never restates them, because a rule stated twice drifts.

After this decision each of the nine steps holds, in the file the model reads
for it, every obligation the requirements place on it, and a task or defect
written from its template has the sections those obligations ask for. What
still doesn't work: whether the model follows a rule is behaviour, and
behaviour is measured by evaluation, which the owner postponed; approvals,
the revision evidence was collected at, generated indexes, recorded insights,
the constitution's and the vision's checks, and allocating identifiers each
wait for a decision of their own.

## Why

REQ-0190 puts nine steps in a chain, and ADR-1130 gave each a file the model
reads only when it runs that step, so a rule placed there costs context only
in the step it governs. RES-0029 and RES-0052 record what research asks, RES-0028
and RES-0151 the requirements step, RES-0152 and RES-0017 design, RES-0153,
RES-0071 and RES-0252 the specification, RES-0055 the epic, RES-0057
implementation, RES-0054 documentation, RES-0063, RES-0068 and RES-0069
verification, and RES-0030, RES-0061 and RES-0231 review; the requirements
drawn from them are what this decision places.

Behavioural obligations can't be settled by a program, which REQ-2694 asks
first; where one can, ADR-1130, ADR-1140 and ADR-1150 already moved it into
`meow record`. What is left is judgement a model exercises while it writes, and
the step file is where it reads.

The strongest objection: a hundred and fifty rules make long prompts, and the
owner's standing guidance is that every rule earns its place by evaluation.
That's the cost this decision pays, and the reversal condition below is how it
gets paid back: once evaluation runs, a rule that doesn't move the result is
removed, as TSK-1260 does for the writing standard.

## Alternatives

| Option                                               | Better at                                      | Why it lost                                                                     |
| ---------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| Each step's file, labelled rules, the trace in tasks | Rules where they're read; prompts cite nothing | Chosen                                                                          |
| One shared rules file for every step                 | One place to read                              | Every step loads every other step's rules, which costs context nine times       |
| Rules citing requirement identifiers inline          | The trace visible in the prompt                | The identifiers mean nothing in another repository and cost tokens there        |
| Wait for evaluation before placing any rule          | Every rule measured before it ships            | The method runs without its obligations until then, and evaluation is postponed |
| Do nothing                                           | Costs nothing                                  | The steps carry a few lines each, and most obligations reach no model           |

## What it costs

Longer step files, read once per step, and seven tasks of writing. Behaviour
isn't measured, and the epic says so.

## What would reverse it

- Evaluation shows a rule doesn't change the model's output, and it is removed.
- A step's file grows past what a model follows reliably in one read, and the
  step splits.

## Consequences

- The nine step files and the `task` and `bug` templates gain their rules.
- SPC-1090 states which step holds which obligations.
- A task written after this carries acceptance criteria, and the layout holds a
  draft task to them.

## How I will know it was realised

1. Every requirement ADR-1160 addresses maps, in the task that closes it, to a
   labelled rule that exists in the step file or template named.
2. `meow-method check` reports 0 findings, and every step file passes the
   prompt check.
3. A draft task without acceptance criteria fails `shape`.
4. Evaluation measures that the steps follow their rules.

## What this does not settle

- Measuring the rules, which waits for evaluation.
- REQ-2897, which forbids per-task status in an epic, against the marks
  `status` reads today.
- Approvals, evidence bound to a revision, generated indexes, insights, the
  constitution's and the vision's checks, and identifier allocation.
