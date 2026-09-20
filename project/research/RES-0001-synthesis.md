---
id: RES-0001
artifact: research
status: approved
revised: 2026-09-20
---

# Research

## Summary

Six private harnesses and ten public ones were read and compared. The method
transplants between projects and the specifics do not, which is the split the
whole project rests on. The largest gap in the survey is verification: nine of
the ten public harnesses assume they know how to test a repository, and none
treats an undeterminable command as an outcome distinct from success. The
second largest is that one failure wears eleven costumes: an answer that was
not earned, delivered with the confidence of one that was. So the harness has
one principle to enforce, and never eleven to repeat.

The first step of this unit of work, and the evidence everything downstream
rests on. It asks what a single harness must do so that six diverged private
copies can be dropped without loss. It also asks what a seventh repository gets
on the first day, in a language none of the six use.

Nothing in the requirements or the design may cite a claim that is not recorded
here or in the sources below.

| Source                                                                                       | What it found                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [The six private harnesses](RES-0002-internal-harnesses.md)                                  | Six private repositories run six copies of roughly the same harness, and the copies have already diverged.                                                                                           |
| [Ten public harnesses](RES-0003-external-harnesses.md)                                       | Ten public harnesses were read, each from its own repository.                                                                                                                                        |
| [The platform](RES-0004-platform.md)                                                         | The platform supports a marketplace of small plugins with declared dependencies, so no installer of the harness's own is wanted.                                                                     |
| [What a skill costs, and what makes one work](RES-0005-skill-format.md)                      | A harness is documents loaded into a context window, so the format is not a matter of taste.                                                                                                         |
| [Verification toolchains](RES-0006-toolchains.md)                                            | Eleven ecosystems answer the same four questions, and the five verbs covered every one of them with no sixth required.                                                                               |
| [What is permanent and what is living](RES-0011-artifact-lifecycle.md)                       | Documents divide by lifetime, and their kind decides nothing.                                                                                                                                        |
| [Catalogues, indexes and templates](RES-0012-catalogues.md)                                  | Three internal repositories organise their specifications differently, and each solved a real problem the others did not.                                                                            |
| [Code comments](RES-0013-comments.md)                                                        | Four language communities publish comment conventions that agree on more than they disagree about: documentation on everything publicly reachable, and inline comments by exception.                 |
| [Commits, branches and merges](RES-0014-commits.md)                                          | The published standards and the six internal repositories agree on the grammar and disagree about the subject limit, so the limit is stated and overridable, and nobody assumes it.                  |
| [Debugging](RES-0015-debugging.md)                                                           | Debugging is the one activity where the model's characteristic failure - offering a cause before recording the behaviour - is the whole of the problem.                                              |
| [Delegation](RES-0016-delegation.md)                                                         | Delegation is for context isolation or independent tracks, never for size.                                                                                                                           |
| [Design review lenses](RES-0017-design-lenses.md)                                            | One internal project wrote five standards that read as project-specific and are not: strip the ledger and the household from them and each becomes a question any design should answer.              |
| [The development log](RES-0018-dev-log.md)                                                   | One internal repository keeps a development log, and it is unlike what the phrase usually means.                                                                                                     |
| [Tooling over the artifacts](RES-0019-document-tooling.md)                                   | Executable tooling over a corpus of structured Markdown settles far more than this method had assumed.                                                                                               |
| [Documentation](RES-0020-documentation.md)                                                   | The four documentation kinds serve different readers in different states, and the most common defect is a document that is two of them.                                                              |
| [Editing and code intelligence](RES-0021-editing.md)                                         | Three ways of finding and changing code - text, structural and semantic - know different things, and only the semantic layer can supply resolved references and diagnostics.                         |
| [The forge: issues, commits and pull requests](RES-0022-forge.md)                            | The harness files its own issues and links them to branches, commits and pull requests.                                                                                                              |
| [Helpers: computing what a model would otherwise read](RES-0023-helpers.md)                  | A harness spends context on its own instructions and on the material the model reads, and an executable helper can remove most of the second.                                                        |
| [Long autonomous runs](RES-0024-loop.md)                                                     | Long autonomous runs fail in five ways, and the ecosystem has converged on the same guardrails for each.                                                                                             |
| [meow-book: a tool over the record](RES-0025-management-system.md)                           | A local-first management tool over the same Markdown corpus is possible and is deliberately not part of the harness.                                                                                 |
| [Memory and context gathering](RES-0026-memory.md)                                           | Once memory is separated from retrieval, the finding is that the artifacts are the memory and a separate store is not wanted.                                                                        |
| [The writing standard](RES-0027-prose.md)                                                    | The two dominant style guides agree closely enough that their intersection is a usable baseline, and one internal skill already implements it.                                                       |
| [Writing requirements](RES-0028-requirements.md)                                             | Four notations compete, and none of them is an alternative to the others.                                                                                                                            |
| [Research, brainstorming and adversarial review](RES-0029-research-technique.md)             | Elicitation is an iterative practice and no interview, and the strongest moves are about order.                                                                                                      |
| [Review](RES-0030-review.md)                                                                 | The established guidance sets the bar at improvement, and never at perfection.                                                                                                                       |
| [Routing, gates and evidence](RES-0031-routing.md)                                           | Only the agentic harnesses have had to solve routing, gates and evidence.                                                                                                                            |
| [Tests, and whether they prove anything](RES-0032-testing.md)                                | Coverage is no evidence, and the measured position is worse for generated code.                                                                                                                      |
| [Defects](RES-0033-defects.md)                                                               | The model had a gap: an epic realises a decision, and nobody decides to have a bug.                                                                                                                  |
| [Does every kind of work fit?](RES-0034-work-kinds.md)                                       | The model authorises work with two records and derives everything else, and this document tests that claim against two established taxonomies of work.                                               |
| [The vision, and how many living documents there are](RES-0035-vision.md)                    | A project needs a document saying what it is and where it is going, kept current.                                                                                                                    |
| [Project-specific artifact kinds, and the relations between them](RES-0036-extensibility.md) | A project may declare artifact kinds of its own, and three facts are enough to declare one: a prefix, a mode and a template, plus a path and optionally a check.                                     |
| [Onboarding an existing repository](RES-0037-onboarding.md)                                  | A repository with its own documentation, harness and code yields a recovered specification, and no requirements and no decisions.                                                                    |
| [How the harness reports to the person](RES-0038-reporting.md)                               | Every mechanism this method has against an unearned answer acts on artifacts, and none of them reaches the reply the person actually reads.                                                          |
| [`/meow:amend`](RES-0051-amend.md)                                                           | Work sometimes contradicts an approved artifact, and without a command for it the contradiction is resolved by quietly rewording the artifact to match what was built.                               |
| [`/meow:research`](RES-0052-chain.md)                                                        | The first step of the chain takes a question and produces one document with sources and conclusions.                                                                                                 |
| [`/meow:discover`](RES-0053-discover.md)                                                     | A harness that demands nine steps for a typo is worked around, and a worked-around harness reports process it did not perform.                                                                       |
| [`/meow:document`](RES-0054-document.md)                                                     | Of everything a project writes down, documentation drifts furthest from what shipped, because it describes the proposal and nobody revisits it.                                                      |
| [`/meow:epic`](RES-0055-epic.md)                                                             | Decomposition is where a plan silently stops matching the decision it came from.                                                                                                                     |
| [`/meow:gate`](RES-0056-gate.md)                                                             | Nobody in the survey has this command.                                                                                                                                                               |
| [`/meow:implement`](RES-0057-implement.md)                                                   | One task is built against its requirements, on a branch, ending in a pull request and never a merge.                                                                                                 |
| [`/meow:init`](RES-0058-init.md)                                                             | Initialisation writes a profile and a constitution into a repository that has neither, by reading what is already there.                                                                             |
| [`/meow:loop`](RES-0059-loop.md)                                                             | An unattended run repeats until a stated condition holds or a stated budget is spent, and both are written before the run and cannot be extended by it.                                              |
| [`/meow:brainstorm`](RES-0060-practice.md)                                                   | Brainstorming is a named phase before any code, and its mechanism is the sectioning: a design presented whole is approved whole, and a design presented in sections is argued with.                  |
| [`/meow:review`](RES-0061-review.md)                                                         | Review reads the diff against a recorded base and returns findings worst-first with two verdicts rather than one.                                                                                    |
| [`/meow:status`](RES-0062-status.md)                                                         | Two harnesses have a status command and one ships a dashboard.                                                                                                                                       |
| [`/meow:verify`](RES-0063-verify.md)                                                         | Verification reports how the work and its artifacts disagree, in every direction, and changes nothing but the status it is the act of moving.                                                        |
| [`/meow:run`](RES-0064-run.md)                                                               | One command drives the whole chain from a research question to a reviewed change, stopping at every gate exactly as the individual step would.                                                       |
| [Stacked pull requests](RES-0065-stacked-pull-requests.md)                                   | When the tasks of one epic depend on each other, one task becomes one proposal in a dependency-ordered series.                                                                                       |
| [Committing to a public repository](RES-0066-public-repository.md)                           | Making the repository open changes what the platform can enforce and what it cannot.                                                                                                                 |
| [Checking the record](RES-0067-checking-the-record.md)                                       | Checking whether the documents agree with each other is neither verification nor validation.                                                                                                         |
| [Verifying a task](RES-0068-verifying-a-task.md)                                             | Verifying a task asks whether the finished work did what it said, which is two completion tests and never one.                                                                                       |
| [Verifying an epic](RES-0069-verifying-an-epic.md)                                           | Verifying an epic asks whether the decision behind the work was realised.                                                                                                                            |
| [Who verifies, and what each can see](RES-0070-who-verifies.md)                              | The method contained a contradiction: one requirement said everything that verifies anything goes through the five verbs, while several others required judgements no verb can make.                 |
| [How finely the specification divides](RES-0071-specification-granularity.md)                | The specification had been divided one document per unit of installation, and that key is wrong.                                                                                                     |
| [The architecture discipline](RES-0072-architecture-discipline.md)                           | Decisions and requirements carry no structure, so an agent implementing a task makes every structural choice locally and the shape erodes one reasonable choice at a time.                           |
| [Diagrams in documents](RES-0073-diagrams.md)                                                | A diagram is written as text in the document and never embedded as an image, because a text definition diffs and an image drifts from its source silently.                                           |
| [The unattended run](RES-0074-unattended-mode.md)                                            | Running overnight with the harness approving its own gates removes the mechanism the survey says makes the method work, and three decisions already in the corpus argue against it.                  |
| [Rust](RES-0101-rust.md)                                                                     | Rust's toolchain is the one where the compiler already does most of what the verbs ask for elsewhere, which makes the mapping easy and hides where it is wrong.                                      |
| [Go](RES-0102-go.md)                                                                         | Go has the least ambiguity of any language surveyed and three real questions underneath it.                                                                                                          |
| [Python](RES-0103-python.md)                                                                 | Four of the five verbs now have an obvious answer.                                                                                                                                                   |
| [TypeScript and JavaScript](RES-0104-typescript-and-javascript.md)                           | This ecosystem moved twice in eight months.                                                                                                                                                          |
| [The C# toolchain](RES-0105-csharp.md)                                                       | Three verbs are the same command with different arguments, which makes the commands trivial and hides that everything deciding whether they mean anything is configuration spread across four files. |
| [Lua](RES-0106-lua.md)                                                                       | Lua ships an interpreter and nothing else, so every verb resolves to a tool the project installed and there is frequently nothing that says which.                                                   |
| [Neovim plugins](RES-0107-neovim-plugins.md)                                                 | A plugin is a Lua project plus a platform, and the platform supplies everything that makes this a separate document.                                                                                 |
| [Godot and GDScript](RES-0108-godot-and-gdscript.md)                                         | The engine supplies three verbs and an independent package supplies the other two, which is where the path problem comes from.                                                                       |
| [Starlark](RES-0109-starlark.md)                                                             | Starlark has a specification and no toolchain: the runtime is somebody else's program, and the same file may be evaluated by three implementations with different builtins.                          |
| [Scheme](RES-0110-scheme.md)                                                                 | The language is standardised and the implementations are not, so the tools do not transfer between them.                                                                                             |
| [Markdown](RES-0111-markdown.md)                                                             | Markdown is the only language here where the checkable part and the part that matters barely overlap: a document can pass every rule and say nothing.                                                |
| [Task runners](RES-0121-task-runners.md)                                                     | Three of the four runners answer in machine-readable form, and none of the three formats carries a stability promise.                                                                                |
| [mise](RES-0122-mise.md)                                                                     | mise is three things at once, which makes it the most informative runner and the one with the largest surface to understand before its answers can be trusted.                                       |
| [go-task](RES-0123-go-task.md)                                                               | Task declares more about each task than the other runners do, and four of those declarations change what a green result means.                                                                       |
| [just](RES-0124-just.md)                                                                     | just makes fewer promises than the other runners, and that turns out to be an advantage.                                                                                                             |
| [make](RES-0125-make.md)                                                                     | make has no concept of a task, so every resolution is an inference and the pack resolves narrowly or not at all.                                                                                     |
| [git](RES-0131-git.md)                                                                       | Exactly one status format carries a compatibility promise, and it is not the newer one - so the richer format is used for what only it provides and read as best effort.                             |
| [Jujutsu](RES-0132-jujutsu.md)                                                               | Jujutsu stores its history in a git repository, which makes it supportable as an alternative front end and hides where the two disagree.                                                             |
| [GitHub and gh](RES-0133-github-and-gh.md)                                                   | This is the only tool in the survey with a quota, a network dependency and a remote party, so it fails slowly and partially for reasons outside the repository.                                      |
| [Linear](RES-0134-linear.md)                                                                 | Supporting a tracker is no second forge to support.                                                                                                                                                  |
| [qmd](RES-0141-qmd.md)                                                                       | Retrieval over this corpus has to run locally, because a tool that sent the documents to a service would be sending the repository to a third party on every search.                                 |
| [repomix](RES-0142-repomix.md)                                                               | A tool that packs a repository for a model is where its secrets are most likely to leave it.                                                                                                         |
| [worktrunk](RES-0143-worktrunk.md)                                                           | This tool was built for the situation the harness creates: several agents in parallel, each needing a working directory the others cannot disturb.                                                   |
| [`/meow:requirements`](RES-0151-requirements-command.md)                                     | The step that turns approved research into requirements, and the approval that matters most because everything downstream cites these identifiers.                                                   |
| [`/meow:design`](RES-0152-design-command.md)                                                 | The step that turns approved requirements into decisions, one per coherent block.                                                                                                                    |
| [`/meow:spec`](RES-0153-spec-command.md)                                                     | Nobody in the survey has this step in this sense.                                                                                                                                                    |
| [`/meow:onboard`](RES-0154-onboard-command.md)                                               | Almost every surveyed harness assumes a new project, which is the finding: the overwhelmingly common case is a repository that already exists, and it is the case the survey handles worst.          |
| [`/meow:cancel`](RES-0155-cancel-command.md)                                                 | Only one surveyed harness can stop an autonomous run, and everything else relies on interrupting the session - which is not the same thing, because it stops at an arbitrary point.                  |
| [`/meow:options`](RES-0156-options-command.md)                                               | Laying out alternatives has one failure mode to design against: the straw-man survey, which looks like diligence and functions as manufactured consent.                                              |
| [`/meow:grill`](RES-0157-grill-command.md)                                                   | A red-team pass over a draft, run before implementation, where a missing edge case costs a paragraph, and after implementation it costs a rewrite.                                                   |
| [`/meow:decide`](RES-0158-decide-command.md)                                                 | The command that writes a numbered decision record.                                                                                                                                                  |
| [`/meow:learned`](RES-0159-learned-command.md)                                               | The development log records what turned out to be true without anybody deciding it, which no other artifact in the method has a place for.                                                           |
| [`/meow:doctor`](RES-0160-doctor-command.md)                                                 | Nobody in the survey has this command, and that absence is the finding.                                                                                                                              |
| [The `skill-authoring` skill](RES-0201-skill-authoring.md)                                   | The authoring surface moved since this project last read it.                                                                                                                                         |
| [Progressive disclosure](RES-0202-progressive-disclosure.md)                                 | Six loading tiers exist where this project used to read three, and the two above the skill are the expensive ones.                                                                                   |
| [Hooks](RES-0203-hooks.md)                                                                   | A hook is the only enforcement the platform has; everything else the harness ships is context that is usually followed.                                                                              |
| [The constitution](RES-0204-the-constitution.md)                                             | The one document loaded into every session had no research of its own.                                                                                                                               |
| [The `operational-ergonomics` skill](RES-0211-operational-ergonomics.md)                     | What a design asks of the people who live with it, how often, and what happens when they stop.                                                                                                       |
| [The `failure-vocabulary` skill](RES-0212-failure-vocabulary.md)                             | Naming every state in which the system is not working, giving each a next step and exactly one audience.                                                                                             |
| [The `budgets` skill](RES-0213-budgets.md)                                                   | Non-functional baselines kept in one place, each carrying the reason for its number, with a specification refining them and restating none of them.                                                  |
| [The `threat-model` skill](RES-0214-threat-model.md)                                         | Tests written without a threat model are mechanical, because they assert whatever the policy happens to say - which is the sharpest argument for the lens.                                           |
| [The `interface-design` skill](RES-0215-interface-design.md)                                 | Two rules survive the strip from a product-specific standard, and both attack the same failure: a surface organised around what the system has, and never around what someone wanted to know.        |
| [The `conventional-commits` skill](RES-0221-conventional-commits.md)                         | The specification requires a type and a description, defines only two types and permits any other.                                                                                                   |
| [The `branching` skill](RES-0222-branching.md)                                               | Work happens on short-lived branches off a single trunk, and the stated problem with the alternative is merge conflict and a broken build.                                                           |
| [The `pull-requests` skill](RES-0223-pull-requests.md)                                       | A proposal is the only artifact in the method written for somebody who was not there.                                                                                                                |
| [The `attribution` skill](RES-0224-attribution.md)                                           | The shortest rule in the corpus: nothing the harness produces claims to have been produced by a tool, anywhere in version control or forge text.                                                     |
| [The `code-review` skill](RES-0231-reviewing-code.md)                                        | The standard is improvement, and never perfection.                                                                                                                                                   |
| [The `artifact-review` skill](RES-0232-reviewing-project-artifacts.md)                       | Reviewing the record is not reviewing code with different nouns: the defects are mostly omissions, and an omission is invisible in a diff because nothing was written.                               |
| [The `documentation-review` skill](RES-0233-reviewing-documentation.md)                      | Documentation has a reader who is not on the team, cannot ask a question and will stop reading, so it can be accurate, complete, well written and useless.                                           |
| [The `lsp` skill](RES-0241-lsp.md)                                                           | A text search for a symbol finds the string and misses the shadowed binding, the re-export, the generated call site and the aliased import.                                                          |
| [The vision template](RES-0251-the-vision-template.md)                                       | The vision is the only document with no upstream artifact, so what it contains is a question about discipline, and nothing derives it.                                                               |
| [The specification template](RES-0252-the-specification-template.md)                         | Both published forms describe a document written once about a system being built, and this one is rewritten for as long as the system exists.                                                        |
| [The research template](RES-0253-the-research-template.md)                                   | A hundred documents were written to a shape nobody wrote down, and repetition is not evidence that it is right.                                                                                      |
| [The requirement template](RES-0254-the-requirement-template.md)                             | The standard defines eleven attributes and this corpus carries eight.                                                                                                                                |
| [The decision template](RES-0255-the-decision-template.md)                                   | Fifty decisions are written to a shape this project invented, and the published templates carry one field it has no equivalent for: how compliance with the decision will be confirmed.              |
| [The epic template](RES-0256-the-epic-template.md)                                           | The published form writes an epic as a hypothesis, and two of its mechanisms transfer.                                                                                                               |
| [The task template](RES-0257-the-task-template.md)                                           | A task is read by an agent that was not present for any of the discussion that produced it, which the published forms do not assume.                                                                 |
| [The defect template](RES-0258-the-defect-template.md)                                       | A defect is the one artifact kind that authorises work without a decision behind it, so its template is mostly about provenance.                                                                     |
| [The index template](RES-0259-the-index-template.md)                                         | The index is the only document in the record whose content could be computed, and the finding is that it should be.                                                                                  |
| [The repository profile](RES-0261-the-profile.md)                                            | The profile is what a repository declares to the harness, and seventeen documents in this corpus depend on one without any of them saying what it contains or where it lives.                        |
| [State outside the repository](RES-0262-state-outside-the-repository.md)                     | The synthesis concluded that run state lives outside the repository keyed by git root, and no document says what is in it, where it goes, or who removes it.                                         |
| [Agent definitions](RES-0263-agent-definitions.md)                                           | The delegation research settled when to delegate and never said what the delegate is.                                                                                                                |
| [Versioning and release](RES-0264-versioning-and-release.md)                                 | The harness ships as a set of plugins with declared dependencies, and nothing in this corpus says what a version number means, what a breaking change is, or how a repository upgrades.              |
| [Migrating the record](RES-0265-migrating-the-record.md)                                     | When the method changes, every artifact already written was written to the old shape, and nothing in this corpus says what happens to them.                                                          |
| [Measuring the harness](RES-0266-measuring-the-harness.md)                                   | The platform can measure what a plugin contributes, which turns _does this skill earn its cost_ from an argument into a number.                                                                      |
| [Monorepos and large repositories](RES-0267-monorepos.md)                                    | Several documents in this corpus assume one repository has one answer - one profile, one set of verbs, one record - and a monorepo has several.                                                      |
| [Licensing and provenance](RES-0268-licensing-and-provenance.md)                             | This repository already declares its licensing in a bulk file and puts identifiers in code, and no decision records why.                                                                             |

## The situation

Six repositories run six copies of roughly the same harness, and the copies
have already diverged. `meowctl` and `meowg1k` share a five-command
specification loop. `vlie` arrived at nearly the same sequence on its own, with
different command names and commands a tenth the size, and `meowhub` built the
idea a third time under a third naming and a different directory layout. Two
have something nobody else does: `hephaestus` has edit-time quality hooks, and
`meowary` has durable memory. A fix to one is a fix to one.

They diverged because there was nothing to diverge _from_. Each documents its
process in its own `CLAUDE.md`, and a document is not a thing you can install,
version or upgrade.

## Findings

### 1. The method transplants; the specifics do not

`meowctl` and `meowg1k` run the same six commands and the same four skills over
a Rust CLI and a Starlark runtime - two projects sharing no code. The commands
are identical in shape; what differs is the paragraphs naming crates, a Go
parity oracle and `starlark-rust`.

`vlie` is the stronger evidence, because nothing was copied between them: a
third project arrived at `/research`, `/design`, `/plan`, `/implement`,
`/self-review` on its own. The sequence is not one author's taste.

That is the whole claim of this project reduced to an observation: everything
that differs between the two is knowledge of one project, and everything that is
the same is method. The split falls in a clean, mechanically checkable place,
and it falls in the same place in every public harness surveyed.

### 2. Verification is where universality actually breaks

Every harness must eventually run a check and believe the result. `cargo nextest
run`, `dotnet test`, `busted`, `godot --headless` and `markdownlint-cli2` have
nothing in common but an exit code.

Of the ten public harnesses read, none treats "I could not determine how to
test this" as an outcome distinct from success. They assume one ecosystem,
shell out to a bespoke CLI, or leave it to prose asking the model to run the
tests. The last of those produces a green report whenever the guessed command
happens to exit zero. This is the single largest gap, and the only one where a
harness can report work as verified when nothing verified it.

### 3. Approval only has value when it stops the turn

Every harness with reported real-world success has at least one point where the
agent produces a document and ends. `spec-kit` has the constitution and the
spec; `harness4claude` has `approve-spec` and `approve-plan`; `cc-sdd` gates
between every phase; `meowctl`'s own skill states that the approval step is the
one the whole method exists to create.

Where approval is described as a recommendation rather than a stop, the
harnesses' own documentation reports that it gets skipped.

### 4. Evidence rots, and one mechanism fixes it

`harness4claude` advances a transactional revision on every file edit and every
shell command, so evidence collected before a mutation cannot satisfy a later
claim of completion.

This is the only mechanism found anywhere in the survey that answers "the tests
passed", said twenty edits ago. Everything else relies on the model remembering
to re-run, which is the behaviour being guarded against.

### 5. A written brief beats a long conversation

`superpowers` dispatches a fresh implementer per task with a written brief, the
interfaces from earlier tasks and a report contract, and explicitly no session
history. It then reviews the resulting diff against that brief. `cc-sdd` runs
an independent reviewer per task and an auto-debug pass in a clean context
after two rejections. BMAD arrives at the same place from the other direction,
with stories carrying rationale, constraints and embedded tests so the
implementer needs no prior context.

Three harnesses, three routes, one conclusion: the task's artifacts are the
source of requirements, not the conversation. Both `superpowers` and `cc-sdd`
report multi-hour autonomous runs that stay on plan.

### 6. Not every change deserves the full method

`harness4claude` classifies L0/L1/L2 before routing. `cc-sdd` routes discovery
into five paths, one of which is "implement directly, no spec". `meowhub` writes
the exception into its rules as "trivial changes: typo, formatting, revert".

A harness that demands nine steps for a typo is one people work around, and a
worked-around harness reports process it did not perform. Saying which route was
taken, and why, is what keeps the method honest about itself.

### 7. Artifacts must outlive the tool

`meowhub` keeps `project/NNNN-slug/` in the repository; BMAD treats every artifact
as a versioned asset; `spec-kit` writes Markdown into `.specify/` and `cc-sdd`
into `.kiro/`.

The failure mode is a harness whose record is meaningful only to its own CLI:
when the CLI goes, so does the record of what was decided. A specification is
part of a project's documentation, and belongs where documentation lives.

### 8. Artifacts drift, and one harness of the ten does something about it

Every harness writes a specification and a task list. None of the ten has an
obligation that the task list be updated in the commit that completes the task,
and none reports a document whose recorded state contradicts the tree.

`Specbound/sdd-harness` comes closest, and the harness takes its mechanism
whole. A detached post-commit job runs a `doc-sync` agent when non-Markdown
files change, updates the affected documents, and commits only the `.md` files
with a `docs: auto-sync` subject **that prevents re-firing**. That last clause
is the part that makes it work; the obvious implementation loops.

It addresses documentation rather than the method's own artifacts, so the gap
for plans and requirements stands.

The nearest anything comes is indirect, and all three carry information forward
where none keeps it true. `superpowers` keeps a ledger _because_ conversation
memory does not survive compaction, and `cc-sdd` feeds implementation notes
from earlier tasks into later ones. `meowctl`'s constitution has a
`<maintenance>` section listing what to update when something changes, which
reminds a reader and checks nothing. `meowhub`'s lifecycle front matter is the
only status anywhere that a tool could read.

A stale document is worse than a missing one, because people still cite it - and
the whole method rests on artifacts being citable. The fix has to be that status
moves in the same change as the work, and that verification reports the
contradiction. A tidying pass afterwards is a pass nobody runs.

### 9. Context is the harness's running cost

A harness is documents loaded into a context window, and context spent on the
harness is context not spent on the work.

The platform charges in six tiers, three of which are the skill's own and three
of which sit above it; they are enumerated in
[RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md), which
was written after this finding and corrects its count. Of the skill's three, a
description is loaded in **every session whether the skill is used or not**.
The body is charged once on invocation and then persists across turns, and
supporting files are charged only where the body sends the model to them.
Measured, the three-tier split costs about 40% fewer tokens than the same
content as one prompt _and_ completes tasks 15-20% better - so brevity and
effectiveness are not opposed here. A shorter relevant context beats a longer
complete one.

`Specbound` is the only surveyed harness with a **capped** memory: hot memory 50
lines, warm observations 50 entries, distilled patterns 70 lines, and an
uncapped cold archive, with progressive condensation between tiers. The caps are
the mechanism - a memory with no ceiling becomes a log nobody reads, and
condensation is forced by the ceiling rather than left to discipline.

The same harness attacks the other half of the cost directly: a shell-command
rewriter, a terse-mode ruleset, and an output-compressing proxy reported at
60-90% reduction on development commands. Compressing what tools return is
a larger lever than compressing what the harness says.

Two further platform facts constrain the format: compaction re-attaches only
the first 5,000 tokens of each skill, and the platform can report per-skill
cost against invocation count. The first makes ordering load-bearing; the
second turns "does this skill earn its cost" into a number.

On the format itself, the guidance and the internal evidence agree on four
things. **XML tags earn their few tokens where a document mixes kinds of
content**: instructions, context, examples and failures, which is what a reader
has to tell apart. They earn nothing in a document that is one instruction
after another, which wants to be shorter and never annotated. The tag
vocabulary must be consistent across documents, and nested by natural
hierarchy. **The front-matter description is what the model routes on**, so it
is written to say when to load the skill rather than to summarise it. And
**style propagates**: the formatting and voice of a prompt shape what the model
produces, which is why a skill written as terse commandments produces terse,
unreasoned work.

Two internal artifacts have needed the fewest corrections in use: `meowctl`'s
`technical-english` and `meowary`'s skills. Both already do all four, with a
house vocabulary of `<role>`, `<summary>`, `<contracts>` and `<patterns>`. That
is weak evidence, being two samples, but it points the same way as the
guidance.

Details in [research/skill-format.md](RES-0005-skill-format.md).

### 10. A rule without its reason gets applied wrongly

`meowctl`'s writing skill contrasts two samples of the same facts: one with an
author, a reader and a reason for each trade-off, and one written as truths
handed down by nobody in particular. The second is what most harness prompts
read like.

The difference is not aesthetic. A rule whose reason is stated survives contact
with a case its author did not foresee, because the reader can tell whether the
reason applies. A rule without one is followed literally and wrongly.

This pulls directly against finding 9, and the tension is real: that skill is
the most effective internal artifact and the most expensive one, and it is
effective _because_ of what makes it expensive. The resolution has to be
placement across the three tiers rather than a choice between the two.

### 11. The method has to be the product

None of the six internal harnesses runs its documented process as installed
software. That is why the copies diverged, and it is why each one's process is
slightly different from the others' without anyone having decided that.

Whatever is built has to be the same artifact for its own development and for a
repository that installs it. The same applies one level down. A harness whose
skills are written by a method it does not itself ship can be extended only by
its authors, and the first repository wanting a house skill has nothing to work
from.

### 11a. Nobody checks whether a test proves anything

Measured, model-generated tests score around **20% on mutation testing** for
complex real-world functions, and mutant survival is **15-25% higher on
AI-generated code at equivalent coverage**. Same coverage number, materially
weaker tests. The two commonest defects are named consistently: assertions that
tolerate a wrong value, and tests that mock the function they claim to test.

Of the ten harnesses, one has a check for it -
`Specbound/sdd-harness`'s `test-integrity-guard.sh`, which flags weakened
assertions and skipped tests, and which is advisory rather than blocking.
Everything else treats a passing suite as evidence.

This matters here more than it would elsewhere, because the method makes a check
the proof of a requirement. A hollow check is a requirement that is recorded as
proved and is not.

### 12. One failure, eleven costumes

Researching each planned skill separately surfaced something no single source
says: the same failure appears in most of the skill studies, wearing
different clothes.

A verb guessed because none resolved. A text search presented as though a
language server had answered. A review finding manufactured to look thorough.
"The tests pass", recalled from twenty edits ago. A loop iteration declaring
completion on a phrase. A comment restating code it no longer matches.
Documentation describing what was proposed rather than what was built. A
straw-man option survey. A requirement reworded to match what was built.

Every one is **an answer that was not earned, delivered with the confidence of
one that was** - and every one is stopped by the same move: say what you did not
do. Unresolved is reported. Absence is reported. Evidence names its revision. A
question is asked as a question.

That is a finding, and no design decision, and it is the most useful one in
this document. The harness has one principle to enforce in the kernel, where
the alternative is eleven repeated across eleven skills.

### 13. What nobody needs

Three things appear in public harnesses and are rejected on the evidence.

Role-playing personas. BMAD's analyst, architect and scrum master. A role
that changes neither the tool set, the context, nor the stopping point changes
only the prose, and the prose it produces is worse.

Dashboards. `claude-code-spec-workflow` ships a WebSocket dashboard that
duplicates what a status command prints, at the cost of an npm package and a
running service.

Anything that only survives one session. A workflow whose state is the
conversation loses to the first compaction.

## What the six already agree on

Observed consensus, needing no argument in the requirements. English
everywhere, including commit messages. Conventional commits with one long-lived
branch. No AI attribution in any git or forge text, which two of the six state
as an explicit override of the default tooling. Specification before code, with
a named exception for trivial changes, and a human approving between phases.
`mise` as the task runner, its task list acting as the harness's real interface
to the project. And skills as XML-structured documents whose front matter says
when to load them.

## Conclusions

What the evidence above requires of a harness. These are implications rather
than decisions, and each is elaborated by the research document it came from.

1. A kernel owning routing, gates, evidence and verification, knowing nothing
   about any language.
2. Verification behind a small fixed contract, with "unresolved" as a
   first-class outcome that is never a pass.
3. One unit per discipline rather than a monolith - argued by partial adoption in
   every real case, and independently by the per-session cost of descriptions for
   disciplines a repository does not have.
4. Language knowledge isolated in units answering that contract and nothing else.
5. Artifacts in the repository, in plain Markdown, in a layout that reads without
   the harness installed.
6. Status that moves in the same change as the work, and a verification step that
   reports the contradiction when it did not.
7. Run state outside the repository, so a resumed session knows which gate it
   is waiting on. This document said keyed by git root; that is corrected in
   [RES-0262-state-outside-the-repository.md](RES-0262-state-outside-the-repository.md),
   which keys by working tree path because worktrees and second clones of one
   repository collide otherwise.
8. Briefs, not conversations, as the input to delegated work.
9. A stated context budget per loadable unit, with obligations placed before
   explanations, and measurement as part of the harness's own verification.
10. The harness developed on itself, in its own layout, with its own authoring
    capability used to write its own material.

## Sources

This document states no claim of its own. Every finding above is drawn from one
of the research documents listed at the top, and each of those carries its
own sources with the dates they were read.

The six internal harnesses were read from their working trees on 2026-09-20:
`~/workspace/meowctl`, `~/workspace/meowg1k`, `~/workspace/vlie`,
`~/workspace/hephaestus`, `~/workspace/meowhub`, `~/workspace/meowary`.
