---
id: RES-0059
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:loop`

## Summary

An unattended run repeats until a stated condition holds or a stated budget
is spent, and both are written before the run and cannot be extended by it. The
ceiling is enforced by the runner rather than requested of the model,
completion requires evidence at the current revision rather than a phrase, and
two iterations that change nothing end the run. The loop stays inside one step,
never crosses a gate, and is user-invocable only.

An unattended run that repeats until a stated condition holds or a stated
budget is spent.

The failure modes and guardrails are in [RES-0024-loop.md](RES-0024-loop.md);
this is the surface.

## Who has an equivalent

| Harness                 | Command                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| ralph-wiggum (official) | `/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"`, and `/cancel-ralph` |
| spec-kit                | `speckit-converge` - implement and converge repeat until convergence is reported                 |
| cc-sdd                  | `kiro-impl` runs autonomously across tasks                                                       |
| superpowers             | The subagent chain, bounded by a five-round fix loop                                             |

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## The surface

```text
/meow:loop [unit] --iterations <n> --until <condition>
```

Three deliberate differences from the original.

No `--completion-promise`. The official plugin detects completion by exact
string match on a phrase the model emits, and its own documentation names this
as the weakness: one outcome, no flexibility, and a model that can end the run
by saying a word. Ours ends on **evidence** - the gate verbs relevant to the
change pass at the current revision, and the plan's tasks are marked with what
closed them.

The iteration ceiling is enforced by the runner. A limit the model is asked
to respect is a limit the model can talk itself past. The `Stop` hook counts;
the prompt does not.

A budget, not only a count. Iterations are a poor proxy for cost when one
iteration can be ten times another. The literature is explicit that the check
belongs _before_ the next paid call rather than after it.

## `disable-model-invocation: true`

Not optional. A model that can start its own unattended run can start one
during a task the user asked for something else in.

## Scope: inside one step

The tension between a method built on human gates and a run that must not stop
resolves one way: **a loop runs within one step of the chain and never crosses a
gate.**

`/meow:implement` over an approved plan is a legitimate loop - requirements,
design and plan are approved, and the work is bounded by them. A loop that would
cross into amending a requirement stops and reports.

This also bounds the run's scope comprehensibly: the plan is what it works
through, and "how far did it get" has an answer anyone can read.

## Conclusions

1. Condition and budget stated before starting; neither extendable by the run.
2. Ceiling enforced by the runner; budget checked before the next call.
3. Completion on evidence, never on a phrase.
4. Identical context per iteration; progress in a durable file.
5. Stop after two iterations that change nothing.
6. Never cross a gate.
7. User-invocable only.
8. Leave an inspectable state and a log, so the run can be stopped.

Stopping the run is its own command,
[RES-0155-cancel-command.md](RES-0155-cancel-command.md).

## Sources

All read 2026-09-20.

- [anthropics/claude-code `plugins/ralph-wiggum`](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
  - the command surface, the `Stop` hook, and the documented weakness of
    exact-string completion detection.
- [github/spec-kit](https://github.com/github/spec-kit) - `speckit-converge` as
  the repeat-until-converged variant.
- [Agent guardrails: loop limits, cost caps, and human approval gates](https://dev.to/gabrielanhaia/agent-guardrails-loop-limits-cost-caps-and-human-approval-gates-56fn)
  - the three guardrails and the before-the-call budget check.
- [What is an AI agent loop?](https://www.jetbrains.com/pages/ai-agents/architecture/ai-agent-loops/)
  - runner-enforced limits in LangGraph and the OpenAI Agents SDK.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) -
  `disable-model-invocation`.
