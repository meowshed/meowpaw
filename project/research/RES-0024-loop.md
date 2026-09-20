---
id: RES-0024
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Long autonomous runs

## Summary

Long autonomous runs fail in five ways, and the ecosystem has converged on the
same guardrails for each. The completion condition and the budget are written
before the run and it cannot extend either. The runner enforces the ceiling,
and nobody asks the model to respect it. Completion requires evidence at the
current revision, no phrase substitutes for it, and two iterations that change
nothing end the run. A loop stays inside one step and never crosses an approval
gate.

Research for `meow-loop`. How the technique works, the five ways long runs
fail, what the ecosystem settled on as guardrails, and what the harness adds
that the original does not have.

## Method

The official loop plugin's documentation was fetched and read on 2026-09-20,
including its own statement of the weakness in exact-string completion
detection, which is the finding the evidence rule replaces.

The published guardrail material and the agent-framework documentation were
fetched for how other runners enforce limits, which is where the distinction
between a limit the runner enforces and one the model is asked to respect came
from.

No loop was run. Every failure mode listed is taken from the sources rather
than observed here.

## The technique

The Ralph loop, named after Ralph Wiggum and implemented as an official
Anthropic plugin, is deliberately simple: intercept the agent's attempt to
finish and feed the same prompt back in.

- `/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"`.
- A `Stop` hook decides: permit the exit if the completion phrase appeared or
  the iteration limit is reached, otherwise restart.
- Each iteration begins from the **same allocated context** - the same prompt,
  the same agent instructions, the same specifications.
- `fix_plan.md` is the mutable to-do list. Git history is what the next
  iteration reads to see what happened.

The insight to keep: **progress lives on disk, not in the conversation.** That
is what makes an iteration cheap and a compaction survivable.

## The five failure modes

The 2026 literature on long-running agents is unusually consistent about how
they fail. Long autonomous processes **forget, overspend, chase a bad goal, lie
to themselves about success, and break things they touch.**

| Failure         | What it looks like                                 | What stops it                                                         |
| --------------- | -------------------------------------------------- | --------------------------------------------------------------------- |
| Forgetting      | Re-deciding something settled three iterations ago | Identical context per iteration; progress in a file                   |
| Overspending    | The run costs more than the work is worth          | A budget checked _before_ the next call, not after                    |
| Bad goal        | Perfect execution of the wrong objective           | A completion condition written and approved before the run            |
| Self-deception  | "Done" with nothing demonstrating it               | Evidence rules                                                        |
| Breaking things | Silent regressions, environmental damage           | Approval gates on world-changing verbs; the gate verbs each iteration |

The fourth is the one that matters most here and the one the original technique
is weakest on. Its own documentation names the weakness: exact-string
completion detection has no room for more than one outcome, and the iteration
limit is the only real safety mechanism. Agents "often produce superficially
successful executions while silently introducing regressions".

## The guardrails the ecosystem settled on

Three, and they are described as the things to build _before_ the loop sees
traffic:

1. A step ceiling: a maximum number of iterations, which the runner enforces
   and nobody asks the model to respect. LangGraph defaults to 25 and raises a
   hard error; the OpenAI Agents SDK uses `max_turns` and raises
   `MaxTurnsExceeded`. The pattern is a hard limit that the loop cannot talk
   its way past. 2. A per-run budget, checked before the next paid call, so the
   abort happens before the spend. 3. An approval gate on the verbs that change
   the world - publishing, deploying, deleting, anything outward-facing.

A fourth is added by the loop-problem literature and this harness takes it:
no-progress detection. The characteristic runaway is not a crash but an agent
re-planning and retrying long after it stopped making progress. Something must
notice that two consecutive iterations changed nothing and stop.

## What the harness adds

The original loop has no notion of evidence, which is exactly the gap that
produces failure four. The harness already has one, so the addition is small,
and it is the whole reason to wrap the technique where pointing at it would do
nothing:

An iteration cannot declare completion without satisfying the evidence
obligations. The completion condition is not "the model said the phrase" but
"the gate verbs relevant to the change pass at the current tree revision, and
the plan's tasks are marked with what closed them". Evidence bound to a
revision is what makes that checkable across iterations, where an unbound claim
holds only within one.

The second addition is the plan file. The original's `fix_plan.md` is a free
to-do list; the harness already specifies a plan with tasks, dependencies,
evidence and the four marks. A loop driving _that_ file
produces a reviewable record of what each iteration did, which is what makes a
long unattended run inspectable afterwards.

## The tension with approval gates

A method built on human gates and an unattended run that must not stop are in
obvious tension, and it needs an answer that nobody has to fudge.

The answer: **a loop runs inside one step of the chain, never across a gate.**
`/meow:implement` over an approved plan is a legitimate loop - the requirements,
design and plan are already approved, and the work is bounded by them. A loop
that would cross from implementation into amending a requirement stops and
reports, because the gate is the point. This also keeps the run's scope
comprehensible: the plan is what it is working through.

## Conclusions

1. The completion condition and the budget are written before the run and are
   not extendable by the run. 2. The runner enforces the step ceiling, and
   nobody asks the model to respect it. 3. The budget is checked before the
   next call. 4. Identical context each iteration; progress lives in a durable
   file. 5. Completion requires evidence at the current revision, and no phrase
   substitutes for it. 6. No-progress detection - two iterations that change
   nothing end the run. 7. A loop runs within one step and never crosses an
   approval gate. 8. Stopping leaves an inspectable state, and the run log says
   what each iteration changed.

## Sources

- [anthropics/claude-code `plugins/ralph-wiggum`](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md), read 2026-09-20 - the
  commands and flags, the `Stop` hook, identical context per iteration,
  `fix_plan.md`, and the documented weakness of exact-string completion
  detection. - [Ralph loop failure modes: context rot and runaway
  cost](https://ralphloop.sh/blog/ralph-loop-failure-modes), read 2026-09-20. -
  [Agent guardrails: loop limits, cost caps, and human approval gates](https://dev.to/gabrielanhaia/agent-guardrails-loop-limits-cost-caps-and-human-approval-gates-56fn), read 2026-09-20 - the three guardrails, and the rule that a
  budget is checked before the next paid call. - [The agent loop problem: when
  "smart" won't stop](https://medium.com/@Modexa/the-agent-loop-problem-when-smart-wont-stop-ccbf8489180f), read 2026-09-20 - no-progress detection as
  distinct from an iteration limit. - [What breaks when LLMs code?
  Characterizing operational safety failures of agentic code
  assistants](https://arxiv.org/pdf/2605.30777), read 2026-09-20 -
  superficially successful executions that introduce silent regressions. -
  [What is an AI agent loop?](https://www.jetbrains.com/pages/ai-agents/architecture/ai-agent-loops/), read 2026-09-20 - termination conditions, and the
  runner-enforced limits in LangGraph and the OpenAI Agents SDK.
