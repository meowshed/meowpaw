---
id: TSK-1210
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3038]
issue: 58
---

# Run the suite locally, at release and on a new model

One task, one branch, one pull request, one review.

## What to do

Add a task named `eval` to `mise.toml` that runs every shipped unit's
evaluation in both arms and publishes each table. Keep it out of `all`, because
every run is a real model call and the gate runs on every change.

The suite runs on the owner's machine and never in CI. The owner decided that
no workflow under `.github/workflows/` makes a model call, so this task adds
none, and the task reads the model credential from the local environment
without printing it.

Accept a model name, and write on each unit's documentation page that a new
model release is a reason to run the suite (REQ-3038). An instruction that
compensated for an older model's limit becomes overhead once that limit is
gone, and only a run on the new model shows which ones.

Report a usage limit or a cost ceiling as a run error, and never as a
regression in a unit.

## Depends on

TSK-1170, because a runner for a suite that cannot discriminate spends a model
call on every run and reports nothing.

## Evidence

Run on 2026-09-22, judged by `claude-opus-5-5`, five runs per arm, no run
errors. Every judged score is a smoke check (REQ-3028).

```bash
mise run eval                                       # claude-sonnet-5, $3.13
mise run eval -- --model claude-haiku-4-5-20251001  # $1.81
```

| Case                     | Sonnet 5 delta | Haiku 4.5 delta |
| ------------------------ | -------------- | --------------- |
| `error-report`           | +0.05          | 0.00            |
| `gap-list-kept`          | -0.20          | -0.20           |
| `no-preamble-no-recap`   | +0.10          | +0.10           |
| `one-line-keeps-the-gap` | +0.15          | +0.15           |
| Weighted, with 2SE       | +0.02 (0.14)   | +0.01 (0.12)    |

On Haiku 4.5 `error-report` scores 1.00 in both arms, so that case measures
nothing on that model. The style costs 1,452 tokens on Sonnet 5 and 1,077 on
Haiku 4.5, because each model counts the same text with its own tokenizer.

`mise run all` still runs no model: `eval` is not among its dependencies.

## Left alone

The schedule REQ-3034 asks for, which needs a runner nobody is watching. EPC-1010
defers it with the reason.
