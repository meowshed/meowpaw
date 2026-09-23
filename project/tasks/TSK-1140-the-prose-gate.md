---
id: TSK-1140
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3182]
issue: 51
---

# Block a publish that carries a named defect

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-prose-gate/` with its manifest and its marketplace entry.
It installs without `meow-prose` and requires neither the skill nor the agent
(REQ-0012, REQ-0076), so it carries its own criteria in its own prompt.

Write `plugins/meow-prose-gate/hooks/hooks.json`: a `PreToolUse` hook of type
`prompt`, naming Haiku in its `model` field. It matches the calls that publish a
text: a commit, an issue, a pull request body, a review comment and a release
note (REQ-3182). Start from the third text in the appendix of ADR-1010, the
gate's draft.

The hook blocks with `permissionDecision: "deny"` and a reason naming the rule.
It judges only what a reader names without weighing taste: an idiom, an
unexplained acronym, an American spelling outside a technical term, a bold
fragment standing in for a heading. Name, in the gate's prompt, the rows of the criteria table TSK-1110 publishes
that the gate judges, and take its labelled cases for those rows from the
examples in the appendix of ADR-1010, each failing example a text to block and
its correction a text to pass. Keep the criteria that narrow, because a
verdict fit to block on has to be one a small model settles the same way twice.

The hook reads the call's input and opens no file. It denies a publish that
hides its text behind a path, such as `git commit -F`, `--body-file` or
`$(cat notes.md)`, and its reason names the inline form to use instead.

A prompt hook stops blocking when it times out, so a long text would pass
unread. Set the timeout deliberately and state it on the unit's documentation
page.

Measure the gate on that labelled set before it lands, and improve its
criteria with the runner TSK-1170 builds. State a ceiling on false blocks
before the first run, because a false block costs more than a miss: a gate
that stops a good text teaches an author to route around it. A candidate lands
when false blocks stay under the ceiling and misses do not rise, and every
candidate is published, including the ones that lost. If Haiku cannot hold the
ceiling, the result is evidence that the criteria are too wide, and they are
narrowed rather than the model changed.

## Depends on

TSK-1110, because the gate's criteria are drawn from the rewritten standard,
and the two must agree about what a defect is.

TSK-1170, because the criteria are improved with the runner that task builds.

## Evidence

In progress. The unit, its hook and 12 labelled cases are in the draft pull
request for #51, which waits for the measurement pass before it lands. Two
smoke runs on Sonnet 5 with Haiku 4.5 in the hook show why: the hook fired on
`git commit` and on nothing else, and then passed the case whose commit names
"DLQ" unexpanded while blocking its correction, which expands it. The ceiling on false blocks, stated before the first run: at most one clean
run in ten blocked, across the clean cases. Misses have no ceiling and are
published beside it. Each case asks the model to run its command once and
print the hook's reason without retrying, and every `gh` command in the set
names `--repo meowpaw-eval/none`, so a text the gate lets through creates
nothing. The task closes on a labelled case set run through the hook, as
SPC-1020 describes for measuring a gate: texts carrying one named defect each,
which it must block, and clean texts, which it must pass, with the block rate
on each kind published for the baseline and for every candidate. A false block counts against the
criteria and not against the text. The same run shows `git commit -F` and `--body-file` denied
with the inline form named.

## Left alone

This repository's own publishing. The gate changes how a body is written here,
which goes inline, and `tools/sync_issues.py` sends a record's text to an issue
through the same calls. Whether that script passes the gate is checked in this
task, and a failure is fixed in the script and not by weakening the hook.
