---
id: RES-0003
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Ten public harnesses

## Summary

Ten public harnesses were read, each from its own repository. Every one has
part of the answer and none has the whole of it, which is the case for building
rather than forking. Classification is the missing front door, evidence is
rarely bound to a revision, and gates held only in conversation are lost at the
first compaction. The methodological finding is that secondary coverage lags:
four of the ten were described wrongly by everything except their own
repository.

Read for what each one solved and how, with the mechanism named precisely
enough to copy or to reject. Every claim below comes from the project's own
documentation, read on 2026-09-20; the sources are listed at the end.

Where a project's README and its secondary coverage disagree, the README wins
and the disagreement is noted - two of the ten have moved far enough that
widely-cited descriptions of them are now wrong.

## Method

Each project was read from its own repository on 2026-09-20 - the README, and
where they exist the command templates, skill definitions and settings, which
is where the mechanisms are rather than in the summaries.

Secondary descriptions were read first and then discarded for four of the ten,
where they contradicted the repository. That is recorded as a finding rather
than silently corrected, because it is the reason the method here is to read
repositories.

Nothing was installed or run. The comparison table was built by reading, so a
claim about what a harness does at run time is a claim about what its own
documentation and templates say it does.

The session's tool record survives and was consulted for this section. It shows
the searches used to find the projects and the direct fetches of each
repository's raw files, in that order.

## 1. github/spec-kit

The reference implementation of specification-driven development, agent-agnostic
across thirty or more coding agents.

- Commands: `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`,
  `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`. Extensions add a
  bug path (`bug-assess`, `bug-fix`, `bug-test`) and an idea-assessment path
  ending in a go / needs-clarification / kill verdict.
- Artifacts: `constitution.md` once per project, then `spec.md`, `plan.md`,
  `tasks.md` per feature, under `.specify/`.

Reading the command templates themselves, rather than the README, turned up four
mechanisms the summaries omit:

An extension hook point around every command. `.specify/extensions.yml`
declares `hooks.before_<command>` and `hooks.after_<command>`, split into
mandatory, optional and conditional. Mandatory hooks run automatically; optional
ones are surfaced for the user to invoke. A project extends a command without
forking its prompt.

A bounded clarification budget. `/speckit-specify` permits at most three
`[NEEDS CLARIFICATION]` markers and instructs the model to make informed guesses
using industry defaults for the rest; its validation loop against a generated
ten-criteria checklist is capped at three iterations. Both numbers exist to stop
the specification step becoming an interrogation.

A checklist gate before implementation. `/speckit-implement` scans
`checklists/` and halts if items are unchecked unless the user overrides.

Task lines that carry four facts.
`- [ ] [T001] [P] [US1] Description with file path` - identifier, a parallelism
marker meaning different files and no blocking dependency, the user story, and a
required path.

`/speckit-analyze` is the closest thing in the survey to our verification step.
It is read-only, with six defect categories - duplication, ambiguity,
underspecification, constitution conflicts, coverage gaps, inconsistency - and
a four-level severity model. It ends in a coverage summary and a
**non-destructive** remediation offer the user opts into.

Rejected: the `specify` CLI as a dependency, and `.specify/` as a private home
for artifacts.

## 2. obra/superpowers

A skills framework and methodology; the most-installed harness of the survey.
Its README lists the skills by name, which is more precise than the secondary
coverage:

`test-driven-development`, `systematic-debugging`,
`verification-before-completion`, `diagnosing-superpowers`, `brainstorming`,
`writing-plans`, `executing-plans`, `dispatching-parallel-agents`,
`requesting-code-review`, `receiving-code-review`, `using-git-worktrees`,
`finishing-a-development-branch`, `subagent-driven-development`,
`writing-skills`, `using-superpowers`.

Three of those exist in no other harness. `verification-before-completion` as a
named skill where others make it a step. `writing-skills`, the harness
authoring its own kind of material. And `receiving-code-review`, which treats
responding to review as a discipline with its own failure modes.

Its workflow: brainstorming -> git worktrees -> writing plans -> subagent-driven
development -> test-driven development -> requesting code review -> finishing a
development branch.

Subagent-driven development is the mechanism to copy. One fresh implementer
per task, given a written brief, the interfaces from earlier tasks, ambiguity
resolutions and a report contract - and _not_ the session history. It returns a
short status from a fixed set: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED.
Review is a separate dispatch against the diff from a recorded base, with spec
compliance and code quality as two verdicts. The fix loop runs up to five
rounds; rounds four and five use a fresh implementer on a more capable model. A
ledger, not conversation memory, tracks addressed and open findings, so
progress survives compaction. A final whole-branch review runs on the most
capable model available.

A plan is written to be followable by "an enthusiastic junior engineer with poor
taste, no judgement, no project context, and an aversion to testing" - a usable,
checkable standard for plan quality.

TDD is enforced by deleting code written before its test.

Rejected: TDD as a universal kernel rule. Taken: nearly everything about
dispatch and review.

## 3. gotalab/cc-sdd

A minimal, adaptable SDD harness, v3.0, shipping seventeen identical skills to
eight agent platforms - Claude Code and Codex stable; Cursor, Copilot, Windsurf,
OpenCode, Gemini CLI and Antigravity in beta.

- `/kiro-discovery <idea>` routes into five paths: extend an existing spec,
  implement directly with no spec, create one spec, decompose into several, or a
  mixed decomposition. **Routing that includes a no-spec path is the mechanism
  to take.**
- Then `/kiro-spec-init`, `/kiro-spec-requirements`, `/kiro-spec-design`,
  `/kiro-spec-tasks`, `/kiro-impl`, plus `/kiro-spec-batch` for multi-spec
  initiatives, `/kiro-steering` and `/kiro-validate-gap`. The older `/kiro:*`
  colon form is deprecated.
- Artifacts: `brief.md` so work resumes without re-explanation, `roadmap.md`,
  `requirements.md` in **EARS** form, `design.md` with Mermaid diagrams and a
  file structure plan, `tasks.md` with `_Boundary:_` and `_Depends:_`
  annotations and an `## Implementation Notes` section fed by earlier tasks.
- Human approval sits between phases. Per-task independent review during
  implementation, with auto-debug in a clean context on rejection.
- Customisation is by editing `settings/templates/` and `settings/rules/`
  rather than forking prompts.

Stated principle: **code is the source of truth, specs are contracts between
parts of the system.**

## 4. Lharden/harness4claude

A spec-driven orchestrator built around classification, state and evidence. Its
README names the skills, which sharpens what the secondary coverage says:

`harness-workflow` (reads the hook's classification, selects the pipeline,
manages state transitions, records metrics), `write-spec`, `write-spec-light`
(~50 lines for L1), `design-doc`, `verify-against-spec`, `grill-me`, `discuss`,
`validate-plan`, `security-scan-python`, `compress-memory`.

Classification happens at a `UserPromptSubmit` hook by bilingual keyword
analysis. Pipelines per level:

- L0 - direct execution, no pipeline.
- L1 feature - `write-spec-light` -> `tdd` -> `verify-against-spec`.
- L1 bug - `systematic-debugging` -> `tdd` -> `verify`.
- L2 feature - `discuss` -> `brainstorming` -> `graph-context` -> `write-spec` ->
  `grill-me` -> `approve-spec` -> `design-doc` -> `validate-plan` -> `approve-plan`
  -> `tdd` -> `verify-multimodel`.

`discuss` captures user decisions in three tiers - **Locked, Deferred,
Discretion** - which is a sharper vocabulary than "open questions", and it sits
beside `meowhub`'s blocking classification.

Specs carry `[NEEDS CLARIFICATION]` flags and boundary definitions as
ALWAYS / NEVER / ASK.

Five hooks: `UserPromptSubmit` to classify, `SessionStart` to initialise state,
`PostToolUse` to advance the revision, `PreCompact` for handoff snapshots and
trace rotation, and a `context7-trigger` that injects library context hints.

State in `~/.claude/harness/projects/<slug>/`, keyed by git root: `state.json`
for the pipeline step and metrics, `signals.json` for inter-skill signals such
as spec-approved and plan-validated.

Every `PostToolUse` file edit or shell command advances a transactional code
revision, so evidence collected before a possible mutation cannot satisfy
completion. This is the single most valuable mechanism in the survey.

L2 verification runs five review dimensions in parallel then an adversarial
adjudication pass that tries to refute each finding. "Neither ships without
evidence."

Rejected: keyword classification, and a pipeline long enough that a small
feature costs eleven stages.

## 5. Specbound/sdd-harness

Recorded in an earlier revision of this document as unreachable. It is reachable
and is the most mechanically developed harness in the survey - 39 slash commands
under `commands/kiro/` and 34 subagents under `agents/kiro/`.

Four phases with human approval gates - requirements in EARS form, a
research-backed design, parallelisable tasks, then TDD implementation with
automatic self-review - and each phase ends in a collaborative review session
before proceeding.

Cog Memory is its distinguishing feature: temperature-tiered persistent
storage with explicit caps, and progressive condensation between tiers.

| Tier | File               | Holds                                              | Cap        |
| ---- | ------------------ | -------------------------------------------------- | ---------- |
| Hot  | `hot-memory.md`    | Current priorities, active specs, recent decisions | 50 lines   |
| Warm | `observations.md`  | Append-only session log with tags                  | 50 entries |
| Meta | `meta/patterns.md` | Distilled workflow rules                           | 70 lines   |
| Cold | `glacier/`         | Archived observations                              | Unlimited  |

Observations compound into patterns; patterns distil into rules. **The caps are
the mechanism** - a memory with no ceiling becomes a log nobody reads, and
condensation is forced by the ceiling rather than left to discipline.

Its hooks are the most extensive set found anywhere, and four are advisory
rather than blocking:

- `test-integrity-guard.sh` - **flags weakened test assertions or skipped
  tests.** No other harness checks this, and it is the exact failure the
  mutation-testing evidence predicts.
- `pr-evidence-hook.sh` - nudges when a pull request body lacks an `## Evidence`
  section.
- `js-quality-gate-hook.sh` - runs `oxlint`/`eslint` on TypeScript writes.
- `skill-permissions-gate.sh` - prompts a permissions review for new skills.

Plus session hooks that inject hot memory before every prompt, capture memory
after a commit, test failure or deploy, and check for re-explanation at stop.

Documentation sync is automatic and self-limiting. A detached post-commit
job runs a `doc-sync` agent when non-Markdown files change; it updates affected
documents and commits only the `.md` files with a `docs: auto-sync` subject
that prevents re-firing. That last detail is the whole trick - the obvious
implementation loops forever.

Three global mechanisms target context cost directly: a `lean-ctx-rewrite.sh`
that rewrites common shell commands to compressed forms, a `caveman-activate.js`
terse-mode ruleset, and an **RTK proxy compressing Bash output by 60-90% on
development commands**. This is the strongest external evidence for the
compute-and-compress argument in [RES-0023-helpers.md](RES-0023-helpers.md).

The commands it ships: `/kiro:verify` is a six-stage pipeline (build, types,
lint, test, audit, git); `/kiro:debug` is a six-step triage; `/kiro:reflect`
mines session learnings into memory; `/kiro:sync-docs`;
`/kiro:harness-validate` checks the harness's own structural integrity.

## 6. Pimzino/claude-code-spec-workflow

- Requirements -> design -> tasks -> implementation, with a separate shorter bug
  path: report -> analyse -> fix -> verify.
- **Steering documents** loaded by every phase: `product.md` (vision, users,
  metrics), `tech.md` (stack, tools, constraints), `structure.md` (organisation,
  conventions, patterns).
- Context commands - `get-steering-context`, `get-spec-context`,
  `get-template-context` - exist to load once and distribute to subagents,
  claiming **60-80% fewer tokens** than loading files individually.
- Per-task generated commands, `/spec-status`, and a WebSocket dashboard with
  tunnel sharing and analytics.

Rejected: the dashboard and the npm package.

## 7. BMAD-METHOD

Corrected. The widely-cited description - analyst, product manager,
architect, scrum master, product owner, developer and QA personas across two
phases - describes an earlier version. The current README states four phases:
Clarify -> Plan -> Build and Verify -> Learn and Adjust, with expertise brought
in through structured multi-agent discussion rather than a fixed persona roster.

Installation is now `npx skills add bmad-code-org/BMAD-METHOD`, or a plugin
marketplace for Claude Code and Codex.

The mechanism this harness takes is unchanged, and it survived its own
redesign: **an artifact carries its own context**. Rationale, explicit
constraints, embedded tests and links back to sources, so an implementer needs
no conversation history. Project briefs preserve decisions as durable context.

The fourth phase is the interesting addition: _Learn and Adjust_, feeding back
into planning, is the only place in the survey where a method has a named step
for changing itself.

Rejected: personas. A role that changes neither the tool set, the context nor
the stopping point changes only the prose.

## 8. buildermethods/agent-os

Version 3.0, January 2026. A four-step loop - **discover, inject, build,
refine** - with four commands: `/discover-standards`, `/inject-standards`,
`/plan-product`, `/shape-spec`.

Its subject is narrower than the others and its two ideas are sharper for it.

Standards are discovered, not declared. `/discover-standards` extracts
patterns from the existing codebase and writes them down - "extract tribal
knowledge from your codebase" - rather than asking for conventions up front and
then being contradicted by every file. `/refine` updates them as the patterns
change.

Standards are indexed so that only the relevant ones load. They live in
`agent-os/standards/`, organised by domain, with an `index.yml`:

```yaml
api:
  response-format:
    description: API response envelope structure, status codes
root:
  naming-conventions:
    description: File, class, and variable naming conventions
```

And the injection mechanism "reads one small index instead of loading all your
standards, then only injects the ones that match".

That is **progressive disclosure applied to project conventions**. It is the
same three-tier argument as section 13 of the design, arriving from a different
direction: a description cheap enough to load always, and a body loaded on
relevance. No other surveyed harness indexes its project-level material at all.

Its definition of a standard states exactly the command-against-skill split
this survey found independently:

> Standards are declarative documentation of your coding conventions. They
> describe patterns and rules without prescribing step-by-step procedures.

With three authoring rules that match `meow-prose`'s: lead with the rule and
explain why second; show code rather than describing it; bullets over
paragraphs, because scannable beats readable.

Specs accumulate in timestamped directories, such as
`agent-os/specs/2026-01-15-1030-user-authentication/`. That is the one choice
this harness rejects: a timestamp sorts and cites nothing, and nothing outside
the directory refers to that spec by a stable short name.

## 9. anthropics/claude-code - `ralph-wiggum`

The official autonomous-loop plugin, after Geoffrey Huntley's technique.

- `/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"`,
  and `/cancel-ralph`.
- A `Stop` hook intercepts the exit and either permits it - completion phrase
  seen, or iteration limit reached - or feeds the identical prompt back in.
- Each iteration starts from the same allocated context. `fix_plan.md` is the
  mutable to-do list; git history is what the next iteration reads.
- Documented weakness: exact-string completion detection has room for one
  outcome, and the iteration limit is the only real safety mechanism.

Taken: the loop, the immutable prompt, the mutable plan file, the stop hook.
Added: a budget and evidence rules.

## 10. Chachamaru127/claude-code-harness

Plan -> work -> review -> release, each stage with a gate and an artifact.

- Treats **"PR-ready" and "release-ready" as different outcomes**, and packages
  only verified evidence into changelogs and tags.
- A runtime floor blocks five categories before execution - billing, network
  egress, secret access, production deploys, out-of-scope destruction -
  separately from a configurable guardrail set (R01-R16: forced pushes,
  protected paths, direct pushes to main) with deny / confirm / warn verdicts.
- **Pre-approvals collected at plan time** for known operations, with expiry and
  use limits.
- A roster of active sessions across worktrees when several agents share a
  repository.

Taken: the two-layer safety split, and pre-approval with expiry. Rejected: the
HTML surfaces and the Go engine.

## Comparison

|                | Routing                  | Spec artifacts                        | Human gates                   | Evidence rules                             | Language-agnostic verification | Autonomous loop                    | State outside repo    |
| -------------- | ------------------------ | ------------------------------------- | ----------------------------- | ------------------------------------------ | ------------------------------ | ---------------------------------- | --------------------- |
| spec-kit       | -                        | constitution, spec, plan, tasks       | yes                           | converge loop                              | assumed                        | converge                           | `.specify/`           |
| superpowers    | -                        | plan, briefs, ledger                  | yes                           | test-first, ledger                         | assumed                        | subagent chain                     | ledger                |
| cc-sdd         | 5 paths                  | brief, requirements, design, tasks    | between phases                | per-task review                            | assumed                        | `impl`                             | `.kiro/`              |
| harness4claude | L0/L1/L2                 | spec, design                          | approve-spec, approve-plan    | revision-bound                             | assumed                        | -                                  | `~/.claude/harness/`  |
| Specbound      | -                        | EARS spec, design, tasks              | per phase                     | test-integrity guard, PR evidence nudge    | assumed                        | -                                  | `.claude/memory/`     |
| spec-workflow  | -                        | requirements, design, tasks, steering | yes                           | tests cited                                | assumed                        | -                                  | dashboard             |
| BMAD           | -                        | brief, spec, architecture             | yes                           | embedded tests                             | assumed                        | -                                  | -                     |
| agent-os       | -                        | standards, indexed; timestamped specs | -                             | -                                          | discovered                     | -                                  | -                     |
| ralph-wiggum   | -                        | PROMPT, fix_plan                      | no                            | none                                       | assumed                        | yes                                | `.ralph/`             |
| cc-harness     | -                        | spec, Plans                           | per stage                     | verified evidence only                     | assumed                        | plan->work->review                 | decision logs         |
| **the gap**    | **classify, and say so** | **in-repo Markdown**                  | **persisted across sessions** | **revision-bound, unresolved is not pass** | **a contract, with packs**     | **bounded by budget and evidence** | **keyed by git root** |

The bottom row is what none of the ten does completely, and it is the
justification for building rather than adopting.

## What the second reading changed

Re-reading the primary sources rather than the summaries corrected four things,
and the corrections share a pattern: **secondary coverage lags,
and the lag is largest where a project has redesigned itself.**

1. Specbound is reachable, and is the most mechanically developed of
   the ten. Its memory caps, its advisory hooks and its self-limiting doc-sync
   are all mechanisms nothing else has.
2. BMAD no longer has the persona roster it is famous for.
3. cc-sdd has moved to a slash-less command form and to v3.0.
4. spec-kit's most interesting mechanisms are in its command templates and
   absent from its README.

## Conclusions

1. Build rather than adopt. Every one of the ten has part of the answer and
   none has the whole of it. The bottom row of the comparison is the gap, and it
   is the justification for a new harness rather than a fork of an existing one.
2. Classification is the missing front door. Only two of the ten classify
   work before starting, and only one reports the class it chose. A harness that
   applies one process to every change is worked around for small changes, and a
   worked-around harness reports process it did not perform.
3. Verification is assumed everywhere. Nine of the ten assume they know how
   to test a repository. None treats an undeterminable command as an outcome
   distinct from success. That is the single largest opportunity in the survey.
4. Evidence must be bound to a revision. One harness advances a counter on
   every edit and invalidates prior evidence with it. Nothing else surveyed can
   tell a claim proved now from one proved twenty edits ago.
5. Gates must outlive the session. Approval held only in conversation is
   lost at the first compaction, and half the surveyed harnesses hold it there.
6. A subordinate agent is for isolation, not for size. The two harnesses
   that delegate well construct the subordinate's context from artifacts and
   take back a short structured result.
7. A loop needs a budget and a no-progress rule, both fixed before the run
   and neither extendable by it.
8. Secondary coverage lags the primary source, and the lag is largest where
   a project has redesigned itself. Four of the ten were described wrongly by
   everything except their own repository, so a survey reads repositories.

## Sources

All read 2026-09-20.

- [github/spec-kit](https://github.com/github/spec-kit), and its command
  templates: [`plan.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/plan.md),
  [`specify.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/specify.md),
  [`tasks.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/tasks.md),
  [`implement.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/implement.md),
  [`analyze.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/analyze.md)
- [obra/superpowers](https://github.com/obra/superpowers) README, and
  [`skills/subagent-driven-development/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) README, v3.0
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) README
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) README
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow) README
- [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) README
- [buildermethods/agent-os](https://buildermethods.com/agent-os), its
  [standards documentation](https://buildermethods.com/agent-os/standards),
  its [workflow documentation](https://buildermethods.com/agent-os/workflow),
  the [v3 announcement](https://github.com/buildermethods/agent-os/discussions/310)
  and the [repository](https://github.com/buildermethods/agent-os)
- [anthropics/claude-code `plugins/ralph-wiggum`](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
- [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) README
