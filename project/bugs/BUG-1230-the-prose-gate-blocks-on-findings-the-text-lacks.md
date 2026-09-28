---
id: BUG-1230
artifact: bug
status: approved
severity: major
violates: REQ-1756
enters: requirements
found: 2026-09-28
revised: 2026-09-28
issue: 597
---

# `meow-prose-gate` blocks texts that break none of its rules

A model judges three rules that each name their defect exactly, and nothing
checks the span it quotes against the rule or the text, so a block can name a
phrase off the list, or a bold line or structure that isn't there.

## Reproduction

With `meow-prose-gate` 0.1.2 installed from this marketplace in Claude Code
2.1.283, on the trunk after #595, on 2026-09-28. Four `gh pr create` commands
each passed their body inline with `--body "..."`, and the hook blocked each
one. Each passed after a reword and a retry. How many other publishes the gate
passed that day wasn't counted.

| Case | The body's shape                                                            | The gate's finding                            |
| ---- | --------------------------------------------------------------------------- | --------------------------------------------- |
| 1    | Plain paragraphs with no `**` or `__` anywhere                              | P2, a bold fragment standing in for a heading |
| 2    | Plain paragraphs that don't hold the phrase `deep dive`                     | P1, `deep dive`                               |
| 3    | Plain paragraphs holding the word `look` and the phrase `gate passes`       | P1, on `look` and on `gate passes`            |
| 4    | Plain paragraphs, each opening with a full sentence, and no emphasis at all | P2, on paragraphs it called unstructured      |

The exact bodies weren't kept, so I wrote one body of each shape and ran each
three times through the hook as tagged `meow-prose-gate-v0.1.2`, with
`tools/measure_gate.py`, driving the session with Sonnet 5 while the hook
named Haiku 4.5, as it ships. The unit's `evals/` held four cases instead of
its own, each `gh pr create --repo meowpaw-eval/none --title "..." --body "..."`
carrying one body. The four bodies are the fixtures in
`plugins/meow-prose-gate/tests/test_gate.py`, class `FalseBlocksFromBug1230`.

```text
python3 tools/measure_gate.py <the v0.1.2 unit, evals/ replaced> --runs 3 -j 6
| Case                 | Kind  | Blocked | Passed | Errors |
| fp1-no-bold          | clean | 0 | 3 | 0 |
| fp2-no-idiom         | clean | 1 | 2 | 0 |
| fp3-look-gate-passes | clean | 0 | 3 | 0 |
| fp4-plain-paragraphs | clean | 0 | 3 | 0 |
clean: 11 of 12 passed, 0 errors
- fp2-no-idiom: {"ok":false,"reason":"P1 | \"in depth\" | This phrase may be confused with \"deep dive\", which is on the blocked list. ...
```

The false block reproduces on case 2, once in three runs, and blocks on
`in depth`, a phrase the body holds that is off the list. A block on a span
the body doesn't hold, as cases 1 and 2 had on the day, didn't reproduce, so
that mode rests on the four unkept blocks alone. Cases 1, 3 and 4 didn't block in three runs
each, so the defect is intermittent, and three runs can't show its rate.

## What the system does

It blocks with a reason in the form `RULE | "span" | fix`, where the span is
text the body doesn't hold (cases 1 and 2 on the day), a word or phrase
outside the list of fifteen (case 3, and case 2 when reproduced), or a judgement about structure that no rule states
(case 4). The prompt says "Any phrase not on this list passes P1", and the
model blocked on phrases off the list anyway.

## What it should do, and why

It should block only where it can quote the span that breaks a rule, verbatim
from the command: for P1 an idiom from the list, for P2 a line holding only
bold text, and for P3 the path argument the text hides behind. REQ-1756 asks a
check to match the defect and never a word that can appear innocently, because
a check that reports a false positive gets disabled.

ADR-1010 would be reversed if the gate blocked texts that carry no defect and
authors routed around it. The first half is observed here and the second
isn't, since each author reworded and retried, so ADR-1010 stands and ADR-1600
amends only how its gate works.

## Triage

It enters at requirements. REQ-1756 is in force and violated, and the fix that
removes the cause is a program that matches the three rules exactly, which
REQ-3186 forbade by banning any pattern over the text. REQ-3187 replaces
REQ-3186, and ADR-1600 records the choice of a program.

Major, because the gate blocked four texts on one day, and a gate that blocks
good text is one people learn to route around, which disables it for the
defects it does catch. The block is safe: nothing wrong was published, and the
cost was a retry each time.

## Closed by

TSK-2470. The four bodies and one true positive per rule are fixtures in
`plugins/meow-prose-gate/tests/test_gate.py`, and they guard the program's
exact matching of P1, P2 and P3 on these bodies. Run against the launcher
before the program existed, they failed because the program was absent, which
shows they run the gate and not that they catch a model's misjudgement: no
fixture can hold a model's verdict. They stay as the regression check.

## Tasks

- [ ] T-001 TSK-2470 replace the prompt hook with a command hook running the
      unit's program, in `plugins/meow-prose-gate/` and `crates/meow/`
