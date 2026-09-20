---
id: RES-0203
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0004, RES-0202
---

# Hooks

## Summary

A hook is the only enforcement the platform has; everything else the harness
ships is context that is usually followed. Three findings change the design. A
timed-out hook does not block, so a blocking hook does constant work and an
expensive check is no hook. Silence from a hook is abstention and never
approval. And hooks do not run before workspace trust, when disabled, or under
a restrictive policy, so nothing is safe only because a hook blocks it.

Research for the only mechanism in the platform that enforces anything. Every
other thing the harness ships is context: an instruction the model reads and
usually follows. A hook runs whether the model agrees or not.

It covers which events exist, how a hook decides, how one fails, what it cannot
do, which events this harness needs, and the conditions under which none of
them run at all.

It does not cover the loading tiers, which are
[RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md), nor
the platform in general, which is [RES-0004-platform.md](RES-0004-platform.md).

## The question

The memory documentation states the division plainly: instructions are _"context,
not enforced configuration"_, and _"to block an action regardless of what Claude
decides, use a PreToolUse hook instead."_

So every rule this harness carries falls into one of two categories, and the
category is not a matter of how firmly the rule is written. The question is
which rules can be hooks, what a hook can actually guarantee, and where the
guarantee stops.

## Method

We fetched and read the platform's hooks reference in full on 2026-09-20. It
supplied the event list, the decision protocol and its exit codes, and the
timeout values with what a timeout does. It also supplied the output fields,
which events deliver output to the model, and the conditions under which hooks
do not run.

The memory documentation was fetched for the statement that instructions are
context rather than enforced configuration, which is the premise the document
rests on.

Nothing was installed or run. No hook was written and timed out to observe the
fail-open behaviour; it is quoted from the documentation.

## Findings

### The event surface is large, and six events matter to this harness

The platform fires hooks on session lifecycle, prompt submission, and every
tool call and its outcome. It also fires them on subagents, tasks, compaction,
model switches, working directory changes, file changes, worktree creation and
removal, configuration changes, and the loading of instruction files.

The ones a harness of this shape needs:

| Event                | Why                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `PreToolUse`         | The only event that can block an action                                                   |
| `PostToolUse`        | Fires after a tool call **succeeds** - the revision counter                               |
| `PostToolUseFailure` | Fires after one **fails** - and a failed call may still have changed the tree             |
| `SessionStart`       | Report a pending gate, since its stdout reaches the model                                 |
| `Stop`               | Redirect an autonomous run back to work while its condition is unmet                      |
| `PreCompact`         | The moment before context is summarised, which is when evidence is most likely to be lost |

Two of these are discoveries, and no choices this harness made.

`PostToolUseFailure` is a separate event, and a revision counter bound only
to `PostToolUse` under-counts. A shell command that exits non-zero can still
have written files, and evidence collected before it would be treated as
current. The counter has to advance on both.

`InstructionsLoaded` fires when `CLAUDE.md` or a rule file loads, which
makes it possible for the harness to know what instruction the session actually
received - a thing it otherwise has to assume.

### The decision protocol has one rule that matters more than the rest

A `PreToolUse` hook decides in one of two ways: exit code 2 blocks the call, or
JSON output carries a `permissionDecision` of `deny`, `allow` or `ask` with a
reason. `deny` has the same effect as exit 2; `allow` skips the normal
permission flow; `ask` puts it to the user.

And the rule that decides how a harness must write one:

> No JSON output (exit 0): Tool call continues through normal permission
> flow - silence doesn't approve

Silence is not approval and it is not denial. It is abstention. A hook that
means to block must say so, and a hook that crashes before printing has
abstained rather than blocked.

`allow` deserves its own caution. A hook that answers `allow` has skipped the
permission flow entirely, which means a harness convenience - pre-approving its
own gate commands - is a hook that disables a protection for whatever matched
its pattern. That is a decision for the repository to make explicitly rather
than something a pack installs.

### A hook fails open, and the timeout is where that happens

The default timeout is 600 seconds, reduced to 30 on `PreToolUse` unless the
hook is declared asynchronous. And:

> Timed-out hooks don't block; the call continues through normal permission
> flow

So an enforcement hook that is slow does not delay the action - it stops
enforcing. That inverts the intuition a slow safety check invites, and it makes
the timing a correctness property rather than a performance one.

The consequence for anything this harness ships: **a blocking hook does
constant work**. It reads its input, matches a pattern, and answers. A hook
that consults the network, walks the tree, or runs a verification verb has
turned enforcement into something that fails open. It fails open under exactly
the conditions that make it count: a large repository, a loaded machine, a slow
link.

Where the check is genuinely expensive, the hook denies by default and the
expensive part runs elsewhere, because failing closed is a decision and failing
open by accident is not.

### Hooks do not run in three situations, and all three are ordinary

Before workspace trust. Hooks in a project's settings run only after the
workspace trust prompt is accepted, and hooks declared in skill or subagent frontmatter
follow the same rule. In a non-interactive session the folder has not been
trusted, so frontmatter hooks do not run.

When they are turned off. `disableAllHooks` in user or project settings
disables user, project and plugin hooks; only managed policy hooks survive it.

When policy forbids them. An administrator can set `allowManagedHooksOnly`,
after which user, project and plugin hooks do not run at all.

This is the finding that bounds the whole mechanism, and it has to be stated
wherever the harness relies on a hook. **A hook is enforcement where it runs,
and it does not always run.** A design that is safe only because a hook blocks
something is unsafe in a fresh clone, in a headless run and under an
administrator's policy. Between them those are most of the cases a harness
meets.

So the honest arrangement is layered: the hook enforces, the gate checks, and
the instruction explains. A rule that exists only as a hook is absent in three
ordinary situations; a rule that exists only as an instruction is advisory
everywhere.

### A hook can inject context, change input and speak to the user

Beyond deciding, a hook's JSON may carry `additionalContext`, which puts text
in front of the model; `updatedInput`, which rewrites the tool's input before
it runs; and `systemMessage`, which shows the model a message.

`additionalContext` is what makes `SessionStart` useful here: a pending gate is
reported by the hook rather than by hoping the model reads a state file.
Plain-text stdout also reaches the model on `SessionStart`, `UserPromptSubmit`,
`UserPromptExpansion` and `PostModelSwitch`. On every other event it goes to
the debug log alone, which is what makes a hook's output look silently lost
when somebody uses it on the wrong event.

`updatedInput` is powerful and is the one to be careful about. A hook that
rewrites what a tool was asked to do has changed the work, and the change
appears nowhere the model or the user can see it. That is the opposite of what
this method is for. This harness does not rewrite tool input; it denies with a
reason and lets the work be redone visibly.

### What a hook cannot do

It runs in its own session **without a controlling terminal** and cannot open
one, so it cannot prompt. Anything needing a person goes through `ask` rather
than through the hook's own interaction.

It can read the transcript, but the transcript _"lags behind the in-memory
conversation"_, so a hook reasoning about what was just said may be reading a
version that does not include it.

It inherits the parent environment, which means it sees whatever the session
sees - including material this method forbids reading. A hook that logs its
input logs whatever was in the tool call.

Ordering between hooks from different plugins is unsupportable, so a design
that needs the kernel's hook to run before a pack's cannot be built.

`SessionEnd` hooks share a 1.5-second budget by default, so an end-of-session
hook that writes a report is writing a small one.

### Hooks are code that runs on the developer's machine

They execute with the user's environment on every matching event. A plugin that
ships hooks is asking for that, and the trust prompt exists because of it.

The same reasoning the harness applies to `mise trust` and to remote Taskfiles
applies to itself here. **The harness's own hooks are declared, few, and
explicable**, because somebody is being asked to let them run. A hook whose
purpose cannot be stated in a sentence should not be shipped.

HTTP hooks add a network dependency and are constrained by an allowlist of URLs
and of which environment variables may be interpolated into headers. This
harness has no use for one: a hook that reaches the network fails open under
exactly the conditions where it is slowest.

## Conclusions

1. A hook is the only enforcement the platform has, and every other rule the
   harness ships is context that is usually followed.
2. A rule is layered rather than placed once: the hook enforces, the gate
   checks, the instruction explains.
3. A design is never safe only because a hook blocks something, since hooks
   do not run before workspace trust, when disabled, or under a policy that
   allows only managed hooks.
4. Silence from a hook is abstention, not approval, so a hook that means to
   block says so explicitly and a hook that crashes has abstained.
5. A blocking hook does constant work, because a timed-out hook does not
   block and the call proceeds - enforcement fails open exactly when the
   machine is slow.
6. An expensive check is not a hook. Where it must be, the hook denies by
   default and the expensive part runs elsewhere, so the failure is a decision.
7. The revision counter advances on both `PostToolUse` and
   `PostToolUseFailure`, because a failing shell command can still have
   changed the tree.
8. A pending gate is reported through `SessionStart`, whose output reaches
   the model, rather than by hoping a state file is read.
9. A hook's plain-text output reaches the model on four events only, and on
   the rest goes to the debug log, which is why output can appear lost.
10. The harness does not rewrite tool input. It denies with a reason, so
    the change is visible and is redone deliberately.
11. A hook never answers `allow` on the harness's behalf, since that skips
    the permission flow for whatever matched, which is the repository's
    decision to make.
12. A hook cannot prompt, having no controlling terminal, so anything
    needing a person uses `ask`.
13. A hook does not log its input, because it inherits the session's
    environment and its input may contain material this method forbids reading.
14. Hook ordering across plugins is not relied on, since it is
    unsupportable.
15. The harness's hooks are few, declared and explicable in a sentence,
    because installing them asks a person to run code on every matching event.
16. No hook reaches the network.

## Sources

All read 2026-09-20.

- [Hooks reference](https://code.claude.com/docs/en/hooks) - the full event
  list including `PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
  `SessionStart`, `Stop`, `PreCompact`, `InstructionsLoaded`, `SubagentStart`
  and `SubagentStop`, `TaskCreated` and `TaskCompleted`, and `SessionEnd`; exit
  code 2 blocking and the `permissionDecision` values `allow`, `deny` and
  `ask`; that no JSON output on exit 0 continues the normal permission flow and
  silence does not approve; the 600-second default timeout reduced to 30 on
  `PreToolUse` without `async`, and that timed-out hooks do not block; the
  `additionalContext`, `updatedInput` and `systemMessage` output fields; that
  plain-text stdout reaches the model only on `SessionStart`,
  `UserPromptSubmit`, `UserPromptExpansion` and `PostModelSwitch`; that hooks
  run without a controlling terminal and inherit the parent environment; that
  the transcript lags the in-memory conversation; the 1.5-second `SessionEnd`
  budget; the workspace-trust requirement for project and frontmatter hooks and
  its absence in non-interactive sessions; `disableAllHooks` and
  `allowManagedHooksOnly`; and the allowlists constraining HTTP hooks.
- [How Claude remembers your project](https://code.claude.com/docs/en/memory) -
  that instructions are context rather than enforced configuration and that a
  `PreToolUse` hook is what blocks an action regardless of what the model
  decides.
- [RES-0004-platform.md](RES-0004-platform.md) - that ordering between hooks
  from different plugins is unsupportable.
- [RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md) -
  the tiers, and the rule that the first question asked of any instruction is
  whether a program could settle it.
