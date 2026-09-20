---
id: RES-0002
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The six private harnesses

## Summary

Six private repositories run six copies of roughly the same harness, and the
copies have already diverged. They diverged because there was nothing to
diverge from: each documents its process in its own instructions file, and
nobody installs, versions or upgrades a document. Seven conventions hold across
all or nearly all six, and they need no argument in the design because they are
already the observed consensus.

What each one does today, read from its `CLAUDE.md`, its `.claude/` tree and
its settings. The last column of each section is the part that does not
transplant, and naming it is the point of the exercise.

## Method

Six working trees were read on 2026-09-20, each at its then-current commit on
its default branch. The table in the sources section names the files read in
each repository: the instructions file, the command and skill trees, the
settings, and the documentation entry points.

Nothing was run. The findings are comparisons between what the files say, and
a repository's harness changes, so this is a re-check list rather than a set of
durable facts.

The session's own tool record survives and was consulted when this section was
written. It confirms the reading and shows no command run against these
repositories, but it does not resolve which read produced which finding,
because several documents were written from one pass over the six trees.

## meowctl

A dotfiles and environment manager, mid-rewrite from Go to Rust. Its harness is
the most developed of the five and is the main donor.

Constitution. `CLAUDE.md` is XML-structured: `<role>`, `<project>`,
`<principles>` with one `<principle name="...">` per rule, then
`<architecture>`, `<build>`, `<workflow>` and `<maintenance>`. Each principle
states its rule and the defect that justifies it - `effects_are_traits` cites
the dry-run bug that already shipped. The file declares itself canonical and
says that anything under `.claude/` adds routing and must not override it.

Commands. `/spec`, `/plan`, `/implement`, `/verify`, `/review`,
`/amend-spec`. Each has front matter with `description` and `argument-hint`,
an explicit list of skills to load first, a numbered procedure, and a fixed
stopping point. `/spec` ends with "Do not implement. Do not create a branch. Do
not open an issue." `/verify` states that it fixes nothing, because deciding
whether the code or the spec is wrong is a judgement someone has to make.

Skills. `spec-driven` (identifiers, tombstones, traceability, the
divergence protocol, what a spec is not, scope discipline), `technical-english`
(always loaded, governs all prose), `scm` (branches, conventional commits, pull
request bodies, the attribution ban), `rust`.

Mechanisms this harness keeps.

- Requirement identifiers `R-<AREA>-<n>`, allocated and never reused, with
  tombstones for withdrawn ones.
- Tests that name the requirement they check in a doc comment, which makes
  `/verify` mechanical rather than a matter of opinion.
- Bidirectional verification: specified-but-untested, and tested-but-unspecified,
  are both findings.
- The divergence protocol. Implementation contradicting the spec stops work;
  the fix is an amendment with a blast radius and a migration, reviewed on its
  own. The stated failure mode is a requirement quietly reworded to match what
  was built.
- "Say plainly when the pull request is clean. Do not manufacture findings to
  look thorough."
- The attribution ban, with the exact `grep` that checks it and the reasoning
  for matching patterns rather than the bare word.

Does not transplant. The crate table and the three boundaries; the Go
binary as a parity oracle; `starlark-rust`; the milestone order of one rewrite.

## meowg1k

A Starlark-programmable agent CLI. Its harness is `meowctl`'s, transplanted.

The commands and skills are the same six and the same four, with the
project-specific paragraphs swapped. This is the evidence for the central
claim: the method survived being moved between two projects that share no code,
and what had to change was exactly the knowledge of the project.

Its own product design is also an input, because it is a study in the same
problem: `meow.tool`, `meow.agent` and `meow.command` are three declarations
that carry a whole surface, and a handler gets eight standard modules with
`fs` and `shell` confined to the workspace. A harness that wants a small
vocabulary of verbs has a working example to copy from.

Does not transplant. Starlark, the provider runtime, the budget model.

## hephaestus

A Godot game in pre-alpha. Its harness is the only one that enforces anything
mechanically.

Hooks. `PostToolUse` on `Write|Edit` runs `gd-quality.sh`: for an edited
`.gd` file it formats with `gdformat`, lints with `gdlint`, and on failure
exits 2 so the linter output is fed back to the model to fix. A second hook
spell-checks Markdown. Tools are called by absolute path inside the project's
virtualenv so the hook does not depend on the shell `PATH`.

Settings. A long `permissions.allow` list of `mise run ...` tasks, with
`deny` on `mise run bump` and `clean-all` and `ask` on the build tasks. The
allow list is the harness's real interface to the project: the tasks are the
vocabulary.

Domain skills. `worldbuilding`, `narrative-design`, `canon-check`,
`game-design`, `system-design`, `presentation-design`, `writing`, plus
`gdscript`, `gdshader` and `run-hephaestus`. A `canon-auditor` agent checks new
fiction against established canon.

Mechanisms this harness keeps. The edit-time quality hook, exit code 2 as the
channel that returns a failure to the model, and the demonstration that the
pack pattern works for a domain (canon) and not only for a language.

Does not transplant. Godot, the Limb, the ten races.

## meowhub

A self-hosted household operations platform, currently all specification and no
running system. It is the donor for artifact layout.

- `specs/NNNN-slug/` with `spec.md`, `plan.md`, `tasks.md`, `notes.md`. One
  directory is one feature - meowhub's arrangement, not one to copy: it binds a
  specification to the unit of work that happened to produce it.
- A lifecycle in front matter: `draft -> review -> approved -> in-progress -> done
| rejected | superseded`, and the front matter is the source of truth.
- Commands named for the artifact: `/spec-new`, `/spec-plan`, `/spec-tasks`,
  `/spec-implement`, `/spec-review`, `/spec-status`, `/adr-new`.
- A spec describes behaviour, not implementation: no service names or table
  schemas in `spec.md`.
- Every requirement is verifiable and is closed by citing a named passing test.
  "Prose is not evidence."
- Open questions are classified by what they block - `design`, `build`,
  `deploy`, `data` or `nothing` - and **only an open `design` question stops a
  spec proceeding**. This is the cure for a harness that stalls on questions
  that block nothing.
- Project-level decisions become numbered records; feature-local decisions stay
  in that feature's plan.
- One commit per slice, squashed, so the history reads as a list of what was
  gained rather than a transcript of how it was built.

Does not transplant. n8n, the double-entry ledger, the butler persona, the
household.

## meowary

A second brain for a developer, maintained by the agent. The donor for memory
and for multi-agent portability.

- `.shared/` is the canonical source; `generate.sh` produces `.claude/` and
  `.opencode/` from it. One body of workflows, two agents. A harness that wants
  to support more than Claude Code has a working pattern here.
- Skills are XML-structured with a house vocabulary: `<role>`, `<summary>`,
  `<contracts>` as numbered obligations, `<patterns>`, and a front-matter
  `related:` list.
- `context-gathering` defines a Step 0.5 that runs before solution generation:
  semantic search over the repository's own notes and a web search in parallel,
  with a rule that durable web findings must be written back into a resource
  article rather than left in the conversation.
- Workflows are separate from commands: `.shared/workflows/` holds the
  procedure, commands are thin entry points.
- Agents are narrow and typed: `code-reviewer` returns severity-graded findings
  (Blocker, Major, Minor, Nit) with `maxTurns` set.
- Tiered execution - `quick`, `standard`, `full` - controls depth, and
  HARD-GATE checkpoints pause for confirmation.
- Stated preference for CLI tools over MCP servers: visible, reproducible, no
  server lifecycle.

Does not transplant. PARA, Jira and Confluence, the journal framing, `qmd`
as a hard dependency.

## vlie

A native JVM language server platform in Rust. Surveyed last, and it changes two
conclusions the other five supported.

Its commands are already the chain. `/research`, `/design`, `/plan`,
`/implement`, `/work`, `/self-review`, `/debug`, `/corpus-fix`. Nobody
coordinated this with `meowctl`; two repositories arrived at the same sequence
separately, which is the strongest available evidence that the sequence is not
an invention of one author's taste.

Its commands are a tenth the size of anyone else's. Compare `meowctl`'s
`/implement` - ninety lines of prose, each instruction carrying its reason -
with vlie's `/work`:

```xml
<role>Autonomous Vlie issue implementer.</role>
<trigger>/work</trigger>

<workflow>
<step n="1" name="issue">Pick the highest-priority open issue with no unimplemented dependencies.</step>
<step n="2" name="branch">Create a new branch from updated `main`; never work directly on `main`.</step>
...
<step n="10" name="wait">Do not merge without explicit user approval.</step>
</workflow>

<output>Issue, branch, PR, verification, and merge-readiness.</output>
```

Ten steps in fifteen lines, and the same ten steps `meowctl` takes ninety to
state. The reasons are not lost - they live in the `rust`, `scm` and `writing`
skills that the steps invoke.

This is the tier split from
[RES-0005-skill-format.md](RES-0005-skill-format.md) found in practice rather
than derived: **a command is a procedure and carries no reasons; a skill is a
judgement and carries them all.** It also suggests the harness's command budget
should be far tighter than its skill budget, and that `meowctl`'s command prose
is the part of it this harness leaves behind.

The caveat is real: a procedure with no reasons is the "scripture voice"
failure when it is asked to carry judgement. vlie gets away with it because its
steps are genuinely mechanical and the judgement is elsewhere. A command that
tries this with a step like "decide whether the spec covers this" would fail.

The other mechanisms this harness keeps:

- **Revisit conditions.** Both `/research` and `/design` end by defining the
  conditions under which the decision is revisited. `meowctl` reached the same
  idea independently as "what would reverse it" in its trade-off register. Two
  repositories, two vocabularies, one mechanism.
- **A devil's-advocate step inside research**: "Argue against the leading option
  and define revisit conditions." The adversarial pass is not a separate
  command.
- **"Compare at least three alternatives."** A number rather than an
  exhortation.
- **Index maintenance is a step, not a hope.** Both `/research` and `/design`
  end with "Update `docs/index.md`". `meowctl` states the same obligation in its
  constitution, where it depends on memory.
- **Frozen historical material is labelled.** `docs/dev/initial-design/` is
  "frozen historical design reference", and `/design` instructs that it and the
  research directory be used "only as historical context". Superseded design
  neither rots in place nor gets deleted - it is demoted to a named state.
- **A development log.** `docs/dev/dev-log.md`, a session log, which none of the
  other five has.
- **A corpus as an oracle.** `docs/dev/corpus-java-true-positives.md` and a
  `/corpus-fix` command: the analyser is checked against a curated corpus of
  known-true findings. The same shape as `meowctl`'s v0.1.0 parity corpus, for a
  different kind of tool.
- **`/work` selects its own issue**: "the highest-priority open issue with no
  unimplemented dependencies" - autonomous selection from the dependency graph
  rather than from a human's choice.

Does not transplant. Java and Kotlin semantics, the parser pipeline, the
mdBook layout, the Starlark rule surface.

## Conclusions

These need no argument in the design; they are the observed consensus, and the
first five hold across all six.

1. English everywhere, including commit messages.
2. Conventional commits, and one long-lived branch with feature branches off it.
3. No AI attribution in any git or GitHub text. Two of the six state it as an
   explicit override of the default harness guidance.
4. Specification before code, with a named exception for trivial changes.
5. A human approves between phases.
6. `mise` as the task runner, and the allow list of tasks as the interface.
7. Skills as XML-structured documents with front matter that explains when to
   load them.

## Sources

Six working trees, read on 2026-09-20. Each was read at its then-current commit
on its default branch; a repository's harness changes, so a reader a year from
now should re-read rather than trust this.

| Repository               | Read                                                                                                                                                                       |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `~/workspace/meowctl`    | `CLAUDE.md`, `.claude/commands/*.md`, `.claude/skills/{spec-driven,scm,technical-english,rust}/SKILL.md`, `.claude/settings.json`, `docs/README.md`, `docs/spec/README.md` |
| `~/workspace/meowg1k`    | `CLAUDE.md`, `.claude/` tree, `docs/spec/README.md`, `docs/spec/index.md`, `README.md`                                                                                     |
| `~/workspace/vlie`       | `CLAUDE.md`, `.claude/commands/{research,design,work,self-review}.md`, `.claude/skills/`, `docs/index.md`, `docs/dev/dev-log.md`, `README.md`                              |
| `~/workspace/hephaestus` | `CLAUDE.md`, `.claude/hooks/{gd-quality,md-spell}.sh`, `.claude/settings.json`, `.claude/skills/` listing, `.claude/agents/canon-auditor.md`                               |
| `~/workspace/meowhub`    | `CLAUDE.md`, `.claude/commands/*.md`, `project/README.md`, `specs/_templates/spec.md`, `docs/standards/*.md`                                                               |
| `~/workspace/meowary`    | `CLAUDE.md`, `README.md`, `.claude/` and `.shared/` trees, `.claude/skills/context-gathering/SKILL.md`, `.claude/agents/code-reviewer.md`                                  |
