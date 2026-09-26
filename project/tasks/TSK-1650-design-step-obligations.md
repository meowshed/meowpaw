---
id: TSK-1650
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1190
closes:
  [
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
    REQ-2138,
    REQ-2140,
    REQ-2760,
    REQ-2762,
    REQ-2764,
    REQ-2766,
    REQ-2768,
    REQ-2770,
    REQ-2772,
    REQ-2776,
    REQ-2778,
    REQ-2780,
    REQ-2782,
    REQ-2794,
    REQ-2796,
  ]
issue: 262
---

# The design step carries the obligations on what it designs

The design step carries the obligations on what it designs, as ADR-1190 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given `steps/design.md`, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in the file. Closed by: the trace table and a script finding each label.
2. Given the step files, when they are searched for a practice command, then none is named. Closed by: the search's output.

## What to do

Append the design rules ADR-1190 places to `steps/design.md`'s rules block, labelled after the existing ones, each with its reason and naming no requirement. Show with a search that no step file names a practice command. Record the trace under Evidence.

## Depends on

Nothing. ADR-1190 is approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and no rule names a requirement:

| Requirement | Carried by               |
| ----------- | ------------------------ |
| REQ-1230    | D11 in `steps/design.md` |
| REQ-1231    | D12 in `steps/design.md` |
| REQ-1232    | D14 in `steps/design.md` |
| REQ-1233    | D12 in `steps/design.md` |
| REQ-1234    | D14 in `steps/design.md` |
| REQ-1235    | D12 in `steps/design.md` |
| REQ-1236    | D15 in `steps/design.md` |
| REQ-1237    | D13 in `steps/design.md` |
| REQ-1238    | D15 in `steps/design.md` |
| REQ-1239    | D13 in `steps/design.md` |
| REQ-1240    | D16 in `steps/design.md` |
| REQ-1242    | D16 in `steps/design.md` |
| REQ-1244    | D16 in `steps/design.md` |
| REQ-1246    | D18 in `steps/design.md` |
| REQ-1248    | D18 in `steps/design.md` |
| REQ-1250    | D18 in `steps/design.md` |
| REQ-1252    | D18 in `steps/design.md` |
| REQ-1254    | D20 in `steps/design.md` |
| REQ-1256    | D21 in `steps/design.md` |
| REQ-1258    | D21 in `steps/design.md` |
| REQ-2138    | D23 in `steps/design.md` |
| REQ-2140    | D24 in `steps/design.md` |
| REQ-2760    | D22 in `steps/design.md` |
| REQ-2762    | D22 in `steps/design.md` |
| REQ-2764    | D22 in `steps/design.md` |
| REQ-2766    | D15 in `steps/design.md` |
| REQ-2768    | D17 in `steps/design.md` |
| REQ-2770    | D16 in `steps/design.md` |
| REQ-2772    | D17 in `steps/design.md` |
| REQ-2776    | D19 in `steps/design.md` |
| REQ-2778    | D19 in `steps/design.md` |
| REQ-2780    | D19 in `steps/design.md` |
| REQ-2782    | D19 in `steps/design.md` |
| REQ-2794    | D21 in `steps/design.md` |
| REQ-2796    | D21 in `steps/design.md` |

REQ-2130 is held without a rule: a search of the step files for a practice command finds none, so no step requires one.

```text
$ grep -rln 'practice' plugins/meow-method/skills | wc -l
0
```

The prompt check and `meow-method check` pass, as the gate shows, and a
script found every traced label in its step file. Whether the model follows
the rules is measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
