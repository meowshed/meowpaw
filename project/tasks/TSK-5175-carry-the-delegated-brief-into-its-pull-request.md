---
id: TSK-5175
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2620
closes: [REQ-1764]
issue: 1015
projected: 6992effa5692
tracked: b1988ec313f5
---

# Carry the delegated brief into its pull request

The brief and implement step make a delegated pull request cite its task and
brief without naming an agent.

## Acceptance criteria

1. Given a delegated fixture task, `paw brief` and the implement instruction
   produce the fields ADR-2730 specifies and no agent attribution. Closed by:
   record and prompt fixtures for REQ-1764.

## What to do

Complete the brief output and implement-step pull request contract.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by the record fixture
`the_brief_asks_the_pull_request_for_the_task_and_the_brief_command` in
`crates/meow/tests/record_brief.rs`, which reads that `paw brief` names the
agent definition on its first line and asks the pull request for the task
and `paw brief <task>` and no agent, model or vendor, and by the prompt
fixtures `test_a_delegated_pull_request_names_the_task_and_the_brief_and_no_agent`
and `test_the_steps_example_passes_the_message_check` in
`plugins/meow-flow/tests/test_delegation.py`, each naming REQ-1764. The record
fixture passed when written, because TSK-4945 had already put the pull request
line into the brief, so it was not seen failing.

Every stage passed in pull request #PR.

## Left alone

Non-delegated pull requests.
