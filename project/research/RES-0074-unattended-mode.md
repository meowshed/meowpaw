---
id: RES-0074
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0024, RES-0070
---

# The unattended run

## Summary

Running overnight with the harness approving its own gates removes the
mechanism the survey says makes the method work, and three decisions already in
the corpus argue against it. What makes it defensible is built into the route,
and no enthusiasm for it. Judgement runs against written principles and never
against preference. The judge is not the worker and is not told whose work it
is. And reversibility draws the line between the gates a run may cross and
those it may not. The platform reports every permission it denied, which makes
the morning escalation list mechanical.

Research for a mode in which the harness starts in the evening and, by morning,
has produced research, requirements, decisions, a specification, tasks and
working code, verified, reviewed and merged. Every approval in that night is
one the harness made itself.

It covers what this contradicts in the method as it stands, and the published
precedent for a system approving against written principles. It covers what is
measured about a model judging its own work. And it covers what the platform
offers for an unattended session, where its trust boundary disappears, and what
has to be true in the morning for the night to have paid.

It does not cover the loop mechanics, which are
[RES-0024-loop.md](RES-0024-loop.md) and
[RES-0059-loop.md](RES-0059-loop.md), nor who may verify what, which is
[RES-0070-who-verifies.md](RES-0070-who-verifies.md).

## The question

The method's central mechanism is that work stops and waits for a person. This
mode removes it.

That is not a detail to design around; it is the thing being removed, and the
research is only honest if it starts by saying what it costs.

## Method

The platform's documentation on non-interactive runs, permission modes and
sandboxing was fetched and read on 2026-09-20, including the sandbox's own
limitations section, which states plainly that it is not a complete isolation
boundary.

The published account of judgement against a written constitution was fetched
for the precedent, and practitioner material on overnight runs was fetched for
what people actually do, and is marked as secondary.

The measured bias figures are taken from the separate study read for the
verification research, and re-read nowhere here.

Nothing was run unattended. No overnight session was performed and measured, so
every claim about how this mode behaves is a design claim.

## Findings

### Three decisions already in the corpus say no, and each says no for a different reason

Approval only has value when it stops the turn. Every surveyed harness with
reported real-world success has at least one point where the agent produces a
document and ends. Where approval was described as a recommendation and never
as a stop, the harnesses' own documentation reports that it gets skipped.

An agent must not judge its own work. Seventeen of twenty models show
statistically significant self-preference when evaluating their own output, and
the effect is strongest on open-ended tasks. Capability does not correct it:
advanced ability is uncorrelated with low bias and is sometimes negatively
correlated.

A loop never crosses a gate. The existing rule for autonomous runs is that
work bounded by an approved plan is legitimate and anything that would amend a
requirement stops and reports.

These are not obstacles to be argued past. They are the three failure modes the
mode has to answer, and the answers differ:

| Objection                            | What it actually requires                                          |
| ------------------------------------ | ------------------------------------------------------------------ |
| Approval must stop the turn          | Something else must play the part the stop played                  |
| An agent must not judge its own work | The judge must not be the worker                                   |
| A loop never crosses a gate          | Which gates may be crossed must be decided in advance, by a person |

### There is a published precedent for approving against written principles

Constitutional AI is the closest thing to what this mode needs, and it holds up
as a precedent, where an analogy would prove nothing.

Its mechanism has two parts. A model critiques and revises its own output
against _"a set of principles to make judgments about outputs"_, and then
preference learning uses _"AI-generated feedback based on the set of
principles"_ where human comparison would otherwise go. The reported result is
a Pareto improvement - more helpful and more harmless at once.

Two things transfer directly.

Judgement against explicit written principles is a different act from
judgement by preference. A model asked _is this good_ answers from taste; a
model asked _does this satisfy these stated principles, and where does it
fail_ answers against something a person can check afterwards. This harness
already has such a document: the constitution, plus the requirements, plus the
decision the work was authorised by.

Critique and revision are separated from acceptance. The precedent is not a
model declaring its work finished; it is a model finding its own faults against
a standard and fixing them, with acceptance a separate step.

The acknowledged limitation is the one to carry: the principles _"reflect our
own choices as designers"_ and _"constitutions aren't a panacea"_. A self-
approval is only as good as what it was checked against, which makes the
quality of the record the binding constraint on how much autonomy is safe.

### The bias literature gives the mitigations, and they are structural

The same research that says an agent must not judge its own work also says what
makes a judgement better, and none of it is exhortation:

- **The judge is not the worker.** A separate agent, dispatched with the
  artifact and the standard, and never the session history. - **The judge is
  not told which side it produced**, and where that cannot be arranged the
  result is reported as self-assessed, and never as a judgement. - **Order is
  controlled**, because position bias is large, judge-dependent and not noise.
  - **A cross-family judge is stronger than a same-family judge**, and where
    the same family is used that is recorded as a limitation of the measurement.

For an overnight run these are cheap. Every one of them is arranging who runs
what, which a scripted run can do exactly and a person under time pressure
frequently does not.

So the honest position is not _self-approval is unsafe_. It is:
self-approval without these arrangements is unsafe, and with them it is a
measurement with a known and stated bias.

### The platform's unattended surface, and the hole in it

Running without a person is supported and has a specific shape.

`claude -p` runs non-interactively. The starting permission mode is Manual on
every plan, so a run passes a mode deliberately. `auto` puts a classifier in
front of most actions and `acceptEdits` writes files without prompting.
`dontAsk` denies everything that would otherwise prompt, which the
documentation describes as useful for locked-down runs.

`--permission-prompts none` is the flag written for this case. Anything that
would prompt is denied unless a `PermissionRequest` hook allows it. The model
is told that nobody can approve and that it should not retry, and the tools
that need a person, `AskUserQuestion` among them, are removed so nothing can
call them.

And the instrument that makes the night auditable: with structured output,
denials appear as `permission_denied` messages and the final result lists them
in `permission_denials`. **That list is the morning's most valuable artifact**:
everything the run wanted to do and could not. It is the queue of decisions
that were actually escalated, produced mechanically, because a run remembers to
mention nothing.

The hole is in trust. Without `--bare`, the documentation states, quoted as
written:

> a `-p` session runs the hooks in a project's `.claude/settings.json` and
> connects the servers in its `.mcp.json`, even in a folder you've never
> trusted. A `-p` session shows no workspace trust dialog and no per-server
> approval prompt.

So the protection an interactive session has - a person deciding whether this
repository's code may run - is absent exactly where nobody is watching.
`--bare` closes it by skipping hooks, skills, commands, subagents, plugins, MCP
servers, auto memory and `CLAUDE.md`, and is _"the recommended mode for
scripted and SDK calls"_.

That produces a genuine tension for this harness, and the document states it
plainly: **the harness is a plugin, and `--bare` does not load plugins.** An
unattended run of _this_ method therefore loads the harness explicitly, by
directory or by URL, and relies on no discovery. What runs at night is then a
named set, and never whatever the working directory contained.

### Sandboxing is necessary and is not sufficient, and the documentation says so

The sandbox restricts which files and which domains commands may touch, with
the operating system enforcing the boundary for every shell command and its
children. For an unattended run it is not optional.

Its own limitations section is unusually candid and every line of it matters
here:

> Sandboxing reduces risk but is not a complete isolation boundary.

The specific ones that bear on a night run:

- **The proxy does not decrypt or inspect TLS by default**, so allow decisions are made
  from the client-supplied hostname. Broad allowances _"can create paths for
  data exfiltration"_, and domain fronting can reach hosts outside the
  allowlist.
- **A Unix socket can be an escape.** Allowing the container socket
  _"effectively grants access to the host system"_.
- **Broad write permissions escalate.** Writes to directories holding
  executables on the path, or to shell configuration files, become code
  execution in another context.
- **Subagents share the parent's sandbox**, which is the right default and
  means delegation does not widen the boundary.
- **Environment variables are inherited by default, credentials included**,
  unless they are masked or scrubbed.
- **Built-in file tools do not go through the sandbox** at all; they go through
  the permission system.

And the operational one: `--dangerously-skip-permissions` is blocked as root,
because root with no prompts can modify any file or service, with the check
skipped inside a recognised sandbox.

The combined reading is that an unattended run needs **both** filesystem and
network isolation, and the documentation says so directly. Without network
isolation a compromised agent exfiltrates keys, and without filesystem
isolation it backdoors its way to the network.

### Prompt injection is the risk that changes character overnight

During the day, an agent that reads a hostile instruction from a web page, an
issue comment or a dependency's readme is one turn away from a person noticing.
At night there is no such turn.

This is the reason the sandbox's network allowlist is a design decision rather
than a convenience, and it is the reason a night run should not be reading
arbitrary external material. A run that researches on the open web is a run
taking instructions from the open web.

The method's existing rule says the harness never reads, prints or transmits a
repository's secret material. It is a sound rule with a weak enforcement story
at night, because the party that would notice a violation is asleep. The
sandbox and the credential scrubbing enforce this, and the instruction enforces
nothing.

### Cost is a real budget and the platform reports it

Structured output carries `total_cost_usd` and a per-model breakdown for each
invocation, described as a client-side estimate that can differ from the bill.

That makes a spend ceiling a stop condition alongside the iteration budget. It
carries more weight here than in a supervised run, because an unattended loop
fails by running long where a wrong answer stops sooner.

### What the morning has to look like

The published practice converges on the same answer from several directions.
What an overnight run buys is never the code: it is waking to _"a short list of
'I needed your call on these,' not a pile of irreversible actions"_.

Which gives the design its acceptance criterion. A night run succeeded if, in
the morning:

- **Every approval it made is attributable and marked**, so the record shows
  which gates a person passed and which the harness passed. - **The escalation
  list is short and mechanical**, drawn from the denials and from the gates the
  run declined to cross. - **Nothing is irreversible.** Everything landed on a
  branch or a series of proposals; nothing was force-pushed, published,
  released or deleted. - **The evidence is complete**, each check naming the
  revision it ran at, so the morning review filters what happened, and
  re-derives nothing. - **The record is honest about itself**, reporting the
  work as unreviewed by a person, which states a limit of the evidence and
  apologises for nothing.

### Which gates may be crossed, and who decides

The decision that makes this safe is taken while a person is awake: **the run's
authority is declared before it starts and cannot be widened by the run.**

The shape that falls out of everything above:

| Gate                                                 | Unattended                                                              |
| ---------------------------------------------------- | ----------------------------------------------------------------------- |
| Research approved                                    | Yes, against the standard for its kind                                  |
| Requirements approved                                | Yes, with every defaulted question recorded as defaulted                |
| A decision approved                                  | Only where it addresses requirements a person approved                  |
| An epic's decomposition                              | Yes                                                                     |
| A task's verification                                | Yes - it is evidence, not judgement                                     |
| Code review                                          | Yes, by a judge that did not write it, marked as unreviewed by a person |
| Merge to a working branch                            | Yes                                                                     |
| Merge to the protected branch                        | Only where the repository opted in explicitly                           |
| Amending an approved requirement                     | Never - this is the gate the loop already may not cross                 |
| Withdrawing a decision a person approved             | Never                                                                   |
| Anything touching credentials, publishing or release | Never                                                                   |

The line through that table is **reversibility**. A night approval is
acceptable where a morning disagreement costs a revert, and unacceptable where
it costs something that cannot be taken back.

## Conclusions

1. Unattended approval is a declared route, and no mode switch, and the route
   is recorded in the run's own report like any other classification. 2. The
   run's authority is fixed before it starts and cannot be widened by the run,
   which is the same rule the budget and the stop condition already follow. 3.
   Nothing irreversible is done unattended. Reversibility is the criterion that
   separates the gates that may be crossed from those that may not. 4. The
   protected branch is not merged to unattended unless the repository opted in
   explicitly. 5. An approved requirement is never amended and an approved
   decision is never withdrawn by the run, which is the existing rule that a
   loop does not cross a gate, kept intact. 6. Approval is made against written
   principles, and never by preference - the constitution, the requirements in
   force, and the decision the work was authorised by - because that is what a
   person can check in the morning. 7. Critique and revision are separated from
   acceptance, following the precedent, so the run finds and fixes its faults
   against a standard rather than declaring itself finished. 8. The judge is
   never the worker. A separate agent receives the artifact and the standard,
   and never the session history. 9. The judge is not told which side it
   produced, and where that cannot be arranged the result is reported as
   self-assessed, and never as a judgement. 10. Order is controlled in any
   comparison, since position bias is large and judge-dependent. 11. A
   cross-family judge is preferred, and using the same family is recorded as a
   limitation of the measurement. 12. Every artifact the run approves is marked
   as approved by the harness, so a morning reader can tell which gates a
   person passed. 13. The record reports the work as unreviewed by a person,
   which states a limit of the evidence, and the rule requires it. 14. The
   morning artifact is a short escalation list, built from the reported
   permission denials and the gates the run declined to cross, rather than from
   the run remembering to mention them. 15. The run declares its permission
   posture explicitly, since a non-interactive session starts in the most
   restrictive mode and anything else is passed deliberately. 16. Tools needing
   a person are removed, and never left to fail, so the run cannot stall
   waiting for an answer nobody will give. 17. The harness is loaded by name in
   an unattended run, because the recommended scripted mode loads no plugins
   and the alternative runs a folder's hooks and servers in a folder nobody
   trusted. 18. A trust decision is never made by the run, which is the same
   rule already established for a task runner's configuration and a remote task
   file. 19. Both filesystem and network isolation are required, because the
   documentation states that without one a compromised agent exfiltrates keys
   and without the other it backdoors its way to the network. 20. The network
   allowlist is narrow and is a design decision, since the proxy does not
   decrypt TLS by default and a broad allowance is an exfiltration path. 21.
   Credentials are scrubbed from the environment of anything the run executes,
   because inheritance is the default and the prohibition on reading secret
   material has no witness at night. 22. A night run does not take instructions
   from open external material, because a hostile instruction read at night is
   not one turn away from someone noticing. 23. A spend ceiling is a stop
   condition alongside the iteration budget, since an unattended loop fails by
   running long, where a wrong answer stops sooner. 24. Sandboxing is necessary
   and not sufficient, stated as the documentation states it, so the design
   does not treat it as a hard boundary. 25. How much autonomy is safe is
   bounded by the quality of the record, because a self-approval is only as
   good as the principles it was checked against.

## Sources

All read 2026-09-20.

- [Constitutional AI](https://www.anthropic.com/news/claudes-constitution) -
  judgement against an explicit set of principles, and never against implicit
  preference; the self-critique and revision phase followed by preference
  learning from AI-generated feedback; the reported Pareto improvement in
  helpfulness and harmlessness; and the acknowledged limitations that the
  principles reflect the designers' choices and that constitutions are not a
  panacea. - [Run Claude Code
  programmatically](https://code.claude.com/docs/en/headless) - `-p` for
  non-interactive runs starting in the most restrictive permission mode; the
  `auto`, `acceptEdits` and `dontAsk` modes and what each approves;
  `--permission-prompts none` denying anything that would prompt, telling the
  model not to retry, and removing the tools that need a person; denials
  reported as `permission_denied` messages and listed in `permission_denials`;
  `--bare` skipping hooks, skills, commands, subagents, plugins, MCP servers,
  auto memory and `CLAUDE.md`, and being the recommended scripted mode; that
  without it a `-p` session runs a project's hooks and connects its MCP servers
  in a folder never trusted, with no workspace trust prompt and no per-server
  approval; `total_cost_usd` and the per-model breakdown as client-side
  estimates; exit codes and SIGTERM behaviour; and the ten-minute ceiling on
  waiting for background subagents. - [Configure the sandboxed Bash
  tool](https://code.claude.com/docs/en/sandboxing) - operating-system
  enforcement of filesystem and network boundaries for shell commands and their
  children; the statement that sandboxing reduces risk but is not a complete
  isolation boundary; that the proxy does not decrypt or inspect TLS by default
  and that broad domains create exfiltration paths including through domain
  fronting; privilege escalation through Unix sockets and through writes to
  executable or shell-configuration paths; that subagents share the parent's
  sandbox configuration; that sandboxed commands inherit the parent environment
  including credentials unless masked or scrubbed; that the built-in file tools
  go through the permission system and never the sandbox; the requirement for
  both filesystem and network isolation together; the unsandboxed retry escape
  hatch and `allowUnsandboxedCommands: false`; and that
  `--dangerously-skip-permissions` is blocked as root. -
  [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the measured
  self-preference bias across twenty models with seventeen significant, that
  capability does not correct it and open-ended tasks trigger it most; position
  bias as large, judge-dependent and not noise; the preference for a
  cross-family judge; and the rule that a judge not told which side it produced
  is what distinguishes a judgement from a self-assessment. -
  [RES-0001-synthesis.md](RES-0001-synthesis.md) - that approval only has value
  when it stops the turn, and that where it is described as a recommendation
  the surveyed harnesses report it being skipped. -
  [RES-0024-loop.md](RES-0024-loop.md) and [RES-0059-loop.md](RES-0059-loop.md)
  - the budget, the stop condition stated before the run, and the rule that a
    loop never crosses a gate. - [Claude Code automation, let agents build while
    you
    sleep](https://munderdiffl.in/blog/claude-code-automation-while-you-sleep/)
    and [The guide to guardrails for agentic coding
    workflows](https://www.coderabbit.ai/guides/guardrails-for-agentic-coding-workflows)
  - the practitioner consensus that an overnight run needs a loop, a permission
    posture and an escalation policy with an audit log, and that the morning
    should bring a short list of decisions needing a person, and no pile of
    irreversible actions. Recorded as secondary sources.
