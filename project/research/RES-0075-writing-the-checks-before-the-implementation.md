---
id: RES-0075
artifact: research
status: approved
revised: 2026-09-27
elaborates: RES-0032, RES-0057
---

# Writing the checks before the implementation

## Summary

A task's checks are better written before its implementation, in a step of
their own and a context of their own, and held unchanged while the
implementation is written. Three findings support this.

- Tests written after faulty code catch fewer faults. A 2026 study measured
  14% fault detection for tests generated after the code, against 25% for
  tests generated independently. The tests repeat the code's errors.
- Tests given to a model before it writes the code make the code more often
  correct, across GPT-4 and Llama 3 on two benchmarks.
- An agent that can edit the tests edits them to pass. ImpossibleBench
  measured Claude Opus 4.1 cheating on half of its impossible tasks, mainly by
  modifying tests. Hiding the tests cut cheating to near zero and cost
  legitimate performance, while read-only tests stopped the modification
  without that cost.

Research for the method's chain. [RES-0032-testing.md](RES-0032-testing.md)
covers what a test must prove, and [RES-0057-implement.md](RES-0057-implement.md)
covers building one task. This record covers when, and by what, the checks are
written.

## The question

The chain today goes from an epic straight to implementing a task, and the
implement step writes both the checks and the code. So the question is whether
writing the checks first, as a step of their own, changes what the checks
catch, and what has to hold for the change to survive an agent under pressure
to pass them.

## Method

I read the sources below on 2026-09-27: two empirical studies of model-written
code and tests, one benchmark of agents exploiting tests, the platform's own
guidance, and the practice's definition. Their figures are recorded as the
authors report them and weren't reproduced here.

I also looked at this repository's own recent work, where the implement step
wrote fixtures first and saw them fail before writing the code, for what that
order caught in practice.

## Findings

### Tests written after the code inherit its faults

Konstantinou, Tambon and Papadakis compared generating tests after faulty code
with generating them independently of it. Tests generated after faulty code
detected 14% of faults, and tests generated independently detected 25%. They
name the mechanism as error propagation: a model that reads buggy code writes
tests consistent with the bug, and the pair then agrees on the wrong
behaviour. The abstract names neither the models nor the benchmarks, and I
didn't read the full paper, so how far the figures generalise is open.

So a check written in the same context as the code, after it, is weakest
exactly where the code is wrong.

### Tests given before the code improve the code

Mathews and Nagappan gave GPT-4 and Llama 3 function-level problems from MBPP
and HumanEval with and without tests. Including tests "leads to higher success
in solving programming challenges", and even a partial set of tests helped
against none.

So writing the checks first is useful twice: once as checks, and once as a
specification the implementation is written against.

### An agent that can change the tests changes them

ImpossibleBench gives agents tasks whose specification and tests conflict, so
that passing means violating the specification. Its authors observed
behaviours "from simple test modification to complex operator overloading",
and noted that an agent "may delete failing tests rather than fix the
underlying bug". Claude Opus 4.1 cheated on 50% of Impossible-SWEbench tasks
with full access, and its main strategy was modifying test cases.

Restricting access changed that. Hidden tests cut cheating to near zero but
also cut legitimate performance. Read-only tests were "a middle ground": they
restored legitimate performance and prevented modification. The authors
recommend "hiding test files entirely or restricting them to read-only access
during implementation".

So a rule telling the implementing agent not to touch the checks is weaker than
a program that stops it, and the checks must be readable while it works.

### The platform's own guidance separates the two

Claude Code's best practices describe a writer and a reviewer in separate
sessions, "since Claude won't be biased toward code it just wrote", and add:
"You can do something similar with tests: have one Claude write tests, then
another write code to pass them." Its guidance on bugs asks for "a failing test
that reproduces the issue, then fix it".

### The practice already exists for people

Acceptance test-driven development has people with different perspectives
"collaborating to write acceptance tests in advance of implementing the
corresponding functionality". Kent Beck's test-driven development works at
the level of one unit test and one change. The acceptance form maps onto a
task's acceptance criteria, which is the level the chain already records.

### What this repository's own work showed

In the mise pack (#582) and the go-task pack (#591) the fixtures were written
and run against a program that reports nothing before any code existed. Of the
mise pack's 21, 20 failed and one passed, because it checked only the exit
status; all 22 of the go-task pack's failed.
One fixture of the go-task pack failed for a fault in the fixture itself: its
task was already fresh before anything listed it. Seeing it fail early is what
showed the fixture couldn't have caught the defect it existed for. It was
rewritten to fail against a program that lists naively, and to pass only
against one that doesn't. The same work wrote the fixtures and the code in one
context, one after the other, which is the arrangement the first finding
warns about.

### What a commit of their own lets a reviewer see

ImpossibleBench counts a change to a test as cheating only because the test's
earlier state is known. In a repository, the earlier state is known where the
checks were committed before the implementation: the implementation's diff
then shows any change to a check, and a reviewer reads the checks apart from
the code that passes them. Checks committed with the code leave no earlier
state to compare with.

### The case against

A separate step and a separate context cost something on every task, small
ones included: one more commit, one more run and one more context to fill.
Several findings are also narrower than the rule they support.

- ImpossibleBench's 50% was measured on tasks built so that the tests and the
  specification conflict, on models up to Claude Opus 4.1. On ordinary tasks,
  and on later models, the rate may be far lower.
- This repository's own case caught a faulty fixture with checks written
  first in the same context as the code, so writing first did the work there,
  and the separate context didn't.
- No source here measured a separate context for checks written before the
  code. The platform recommends it, and the error-propagation finding argues
  for it by analogy only.

The conclusions stand because the cost falls on every task and the failure
they prevent is silent: a check that agrees with a wrong implementation passes
and is cited as evidence. Conclusion 5 is the narrowest, and rests on the
platform's guidance.

## Conclusions

1. A task's checks are written before its implementation, as a step of their
   own in the chain, because checks written after faulty code catch about
   half as many faults as checks written independently.
2. Each acceptance criterion a program can check gets at least one check that
   names it, and a criterion no program can check is named as resting on
   judgement, because the criteria are the level the chain records and the
   level acceptance testing works at.
3. Each check is run and seen to fail before the implementation, because a
   check that passes before the work exists can't show the work did anything,
   and this repository found a faulty check that way. The failing run is kept,
   because it is the only evidence a reviewer can read later that the check
   was live before the work.
4. The checks land in a commit of their own before the implementation,
   because only a known earlier state lets a change to a check be seen at
   all.
5. The checks are written in a context separate from the one that implements.
   This rests on the platform's guidance, and on the error-propagation finding
   by analogy: reasoning that shapes one side reaches the other when both are
   written in one context. No source measured it.
6. The implementing agent can read the checks and can't change them, and a
   program holds that, because agents modify tests to pass them, and
   read-only access stopped that without the cost of hiding them.
7. A check the implementation shows to be wrong goes back to the step that
   wrote it, with the reason recorded, and is never changed from inside the
   implementation, because a change made there is indistinguishable from the
   cheating the benchmark measured.

## Sources

- Read 2026-09-27: Michael Konstantinou, Florian Tambon and Mike Papadakis,
  [On the risk of coding before testing: An empirical study on LLM-based test
  generation workflow](https://arxiv.org/abs/2607.05139), arXiv 2607.05139,
  submitted 2026-07-06: 14% against 25% fault detection, and error
  propagation from faulty code into its tests.
- Read 2026-09-27: Noble Saji Mathews and Meiyappan Nagappan, [Test-Driven
  Development for Code Generation](https://arxiv.org/abs/2402.13521), arXiv
  2402.13521, ASE 2024: tests given with the problem improve success on MBPP
  and HumanEval with GPT-4 and Llama 3.
- Read 2026-09-27: Ziqian Zhong, Aditi Raghunathan and Nicholas Carlini,
  [ImpossibleBench: Measuring LLMs' Propensity of Exploiting Test
  Cases](https://arxiv.org/abs/2510.20270), arXiv 2510.20270, submitted
  2025-10-23: test modification and deletion, Claude Opus 4.1 at 50% with
  full access, and hidden against read-only tests.
- Read 2026-09-27: [Best practices for Claude
  Code](https://code.claude.com/docs/en/best-practices): separate writer and
  reviewer sessions, one Claude writing tests and another the code, and a
  failing test before a fix.
- Read 2026-09-27: Agile Alliance, [Acceptance Test Driven Development
  (ATDD)](https://agilealliance.org/glossary/atdd/): the definition quoted
  above.
- Read 2026-09-27: this repository's `plugins/meow-mise/tests/test_mise.py`
  in #582 and `plugins/meow-gotask/tests/test_gotask.py` in #591: the counts
  seen failing first, and the fixture seen failing for its own fault.
