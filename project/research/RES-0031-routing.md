---
id: RES-0031
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Routing, gates and evidence

## Summary

Only the agentic harnesses have had to solve routing, gates and evidence. One
of them has a mechanism nothing else does: a revision that advances on every
edit, so evidence collected before a mutation cannot satisfy a later claim.
Classification happens before work and reports the class and the reason,
ambiguity resolves to the more expensive route, a gate record survives the
session, and silence is not approval.

Research for the kernel's `/meow:discover`, the gate records and the evidence
ledger. Three mechanisms that only the agentic harnesses have had to invent,
because no pre-agent practice had this problem.

## Method

The surveyed harnesses were read from their own repositories on 2026-09-20,
including their state files and hook configurations, which is where the
revision mechanism and the state-outside-the-repository pattern were found -
neither is described in any of their readmes.

The platform documentation was fetched for the hook events these mechanisms
depend on.

Nothing was run. We describe the revision mechanism from its implementation as
committed, and watched it operate nowhere.

## Routing

### Why it exists

A method that costs the same for a typo and for an architectural change gets
bypassed for the typo, and once bypassing is normal it is also used for the
architectural change. Every surveyed harness that survived contact with real
work has some form of this, and the ones that do not are the ones whose
documentation quietly admits the process gets skipped.

### What others do

`harness4claude` classifies L0/L1/L2 at the `UserPromptSubmit` hook, before
anything runs. L0 bypasses the pipeline entirely; L1 gets a light specification,
TDD and verification; L2 gets the full eleven-stage treatment with two human
gates. Classification is by keyword analysis of the prompt.

`cc-sdd` routes `/kiro-discovery` into five paths: extend an existing spec,
implement directly with no spec, create one spec, decompose into several, or a
mixed decomposition. The second and fifth are the interesting ones - an explicit
no-spec path, and an explicit acknowledgement that one request may be several
units of work.

`meowhub` writes the exception into its rules in prose: "trivial changes
(typo, formatting, revert)".

`claude-code-spec-workflow` has no complexity classes but does separate the
bug path from the feature path: report, analyse, fix, verify. That is a
different axis and both are needed.

### The trade-offs

Keyword classification is fragile. `harness4claude` classifies on bilingual
keyword analysis, which is cheap and works until someone describes an
architectural change in plain words. A model reading the request and the
repository classifies better than a keyword list - but is non-deterministic,
which is why the class and the reason are _reported_ and never applied
silently, and why a one-word human override is required.

Which direction to err. Mis-routing down is a defect: an architectural
change made as a typo fix, with no requirement and no record. Mis-routing up
wastes an hour. The asymmetry is large enough that ambiguity should resolve
upward and the harness should say it did.

Decomposition is a routing outcome, and no separate step performs it. `cc-sdd`
is right that "this is three units of work" is a legitimate answer to a
request, and a harness that only classifies size will try to run one chain over
three unrelated changes.

### The bug path

Distinct because it starts somewhere else: with a **reproduction**. A defect
whose reproduction is not established is guesswork, and every step after
that is speculation. Once reproduced, a defect rejoins the normal classes - a
one-line fix is L1, a defect whose cause is an architectural mistake is L2.

This also gives the verification step something exact to check: the
reproduction that failed now passes, which is evidence in the strict sense and
asserts nothing about the bug being gone.

## Gates

### The mechanism, and where it usually fails

A gate is a stop. The failure is not that harnesses forget to stop - it is that
they stop **inside a session** and lose it at the boundary.

`harness4claude` is the only surveyed harness with a durable answer:
`approve-spec` and `approve-plan` are recorded in per-project state, and
responding to a pending gate **resumes the scoped task state** and starts
nothing fresh. `Specbound/sdd-harness` claims cross-session persistence for the
same reason.

Everything else assumes the approval and the work are in one conversation,
which loses to the first compaction.

### What a gate record has to contain

Drawn from the failure modes, and from no template:

- **Which artifact** was approved - otherwise "approved" is ambiguous when
  three artifacts are in flight. - **Which step** it gates. - **A content hash
  of the artifact**, because approval is of a _version_. Editing an approved
  artifact and proceeding is the commonest quiet violation, and a hash is what
  makes it detectable, where good faith detects nothing. - **When**, so a stale
  gate is visible.

### What is not approval

Worth stating because a model will accept all of them: silence, a change of
subject, an unrelated instruction, "looks good" about something else, and the
absence of an objection.

## Evidence

### The problem no pre-agent practice had

A human who says "the tests pass" has usually just run them. A model saying it
may be recalling a run from twenty edits ago, and the sentence reads
identically either way.

### `harness4claude`'s revision counter

The mechanism: every `PostToolUse` file edit or shell command advances a
transactional code revision, and **evidence collected before a possible
mutation cannot satisfy completion**. Verification demands concrete proof - test
files, diffs, logs - and every requirement, criterion and boundary gets explicit
coverage evidence or fails.

It is the only mechanism in the survey that addresses staleness, where the
others address absence, and it is why the design adopts it wholesale.

### The three properties that make something evidence

1. It is a command and its result, and no sentence stands in for it. The
   command, the exit status, the relevant output. 2. It is bound to a tree
   state. A revision number, because a timestamp tells you nothing about
   whether the tree changed. 3. It names what it closes. Evidence attached to
   nothing accumulates without being checkable.

### The interaction with long runs

This is where the counter pays off most. A loop iterating over a plan will
otherwise re-assert an earlier iteration's success, which is failure mode four
in [RES-0024-loop.md](RES-0024-loop.md). A revision-bound ledger makes "this
was proved at r417 and the tree is now r431" a mechanical statement that needs
no judgement.

## Conclusions

1. Classify before working, report the class and the reason, accept a one-word
   override. 2. Ambiguity resolves to the more expensive route, and says so. 3.
   "This is several separate changes" is a valid routing outcome. 4. Defects
   start at reproduction, and the reproduction becomes the verification
   evidence. 5. A gate record names the artifact, the step, the version hash
   and the time, and survives the session. 6. Silence is not approval. 7.
   Evidence is a command, its result, a revision and an identifier. 8. A
   mutation invalidates prior evidence mechanically, and nobody has to remember
   to do it.

## Sources

- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) README,
  read 2026-09-20 - L0/L1/L2 classification at the `UserPromptSubmit` hook, the
  per-level pipelines, `state.json` and `signals.json` keyed by git root, and
  the `PostToolUse` revision rule.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) README, read 2026-09-20 -
  `/kiro-discovery` and its five routes, including the no-spec path.
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow)
  README, read 2026-09-20 - the separate bug path.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) README, read
  2026-09-20 - phase gates with cross-session persistence, and `/kiro:debug` as
  a six-step triage.
- `~/workspace/meowhub/CLAUDE.md`, read 2026-09-20 - the trivial-change
  exception stated in prose.
