---
id: RES-0019
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Tooling over the artifacts

## Summary

Executable tooling over a corpus of structured Markdown settles far more than
this method had assumed. The prior-art tools validate front matter as a schema,
answer queries with identifiers before bodies, generate the index, and derive
the traceability matrix. Every one of them derives the matrix, which is the
strongest agreement found in the survey.

Research for what executable tools can do with a corpus of structured Markdown

- requirements, specifications, plans, decisions - and what that buys.
  [RES-0023-helpers.md](RES-0023-helpers.md) argues that a mechanical
  determination is computed, where reading for it costs the context; this is
  the concrete answer to _which_ ones, against the prior art of tools that have
  managed requirements as text for a decade.

## Method

The comparison of requirements-management tools was fetched and read on
2026-09-20, along with the documentation of the individual tools it names, for
what each actually stores and what each derives.

The tools were not installed or run against this corpus. That is the main
limitation: the claim that the matrix should be derived rests on every surveyed
tool deriving it, and we measured the cost of neither approach here.

## The prior art is older than the problem

Requirements management in version control is a solved genre with working
implementations, and none of them was built for an agent:

| Tool                          | Format                | Granularity                  | Notable                                                                                                             |
| ----------------------------- | --------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Doorstop**                  | Markdown-ish, YAML    | **One file per requirement** | Git-native hierarchy of linked requirements and verification items                                                  |
| **StrictDoc**                 | RST, HTML, text modes | One file per document        | Described as Doorstop's successor; the most comprehensive traceability matrix support, exporting interactive graphs |
| **Sphinx-Needs / Open-Needs** | RST, in Sphinx        | Objects inside documents     | Requirements as first-class objects with links and filters; a docs-as-code toolchain                                |
| **OpenFastTrace**             | Markdown, others      | Tags in any text             | A tracing suite: artifacts declare what they _need_ and what they _cover_, and it computes the gaps                 |

Three things transfer directly.

The needs/covers vocabulary. OpenFastTrace's model is exactly the harness's
two identifier sets: an artifact declares coverage of an identifier, and the
tool computes which are uncovered and which cover nothing. That is bidirectional verification
with a decade of prior implementation behind it, and it confirms the decision
not to store a matrix - the matrix is derived, and every one of these tools
derives it.

Granularity: the prior art disagrees with itself, and so did this project.
Doorstop is file-per-requirement; StrictDoc and Sphinx-Needs moved deliberately
to file-per-document. The harness ended at Doorstop's answer for a reason
neither had - its reasoning lives in decision records, and never beside the
obligation, so a requirement has no motivating prose to be separated from
([RES-0012-catalogues.md](RES-0012-catalogues.md)).

Validation is what makes the corpus reliable. All four validate structure
before anything else uses it. A corpus that nothing checks drifts into
unparseable shapes, and then the tooling silently reports on a subset.

What none of them has: **status that moves with the work**, **evidence bound to
a tree revision**, and **the artifacts as context for a model**. Those are the
harness's additions, and they are why this project would build the tooling
where adopting somebody else's would not do.

## What the front matter makes possible

Structured preambles are what turn a pile of prose into a queryable corpus, and
the harness already requires several fields.
Extended to carry `artifact`, `status`, `revised`, `checked-at`, `elaborates`,
`area`, `id` and `supersedes`, the corpus supports queries that are currently
answered by reading:

| Question                             | Today               | With front matter    |
| ------------------------------------ | ------------------- | -------------------- |
| What is approved?                    | Read every artifact | One filter           |
| What has drifted since revision _n_? | Read and compare    | Compare `checked-at` |
| What elaborates this design?         | Search and infer    | Follow `elaborates`  |
| What superseded this?                | Read the tombstones | Follow `supersedes`  |
| Which units are in progress?         | Open each directory | One listing          |

The cost is one block per file. The gain is that every one of those becomes a
determination the harness computes, where it used to be a reading. That is the
whole argument of [RES-0023-helpers.md](RES-0023-helpers.md), applied where the
harness spends most of its context.

## What the tools would be

One determination each, structured output, absence reported.

`req` - the requirements corpus as a queryable set.

- `req <id>` - one requirement with its status, its section, and **every place
  it is cited**. Today that is a repository-wide search. - `req --search
<text>` - matching requirements, as identifiers and first lines, and never
  whole sections. Progressive disclosure applied to search: titles first,
  bodies on request. - `req --status <state>` - filter. - `req --coverage` -
  the four directions of bidirectional verification in one table. - `req
--next` - the next free identifier in a topic block, which is what makes
  numbering in blocks with gaps survivable by hand.

`plan` - the plan as a dependency graph.

- Tasks with their marks, their dependencies and their evidence. - **What is
  ready** - unmarked tasks with no unmet dependency. This is what `vlie`'s
  `/work` does by reading the whole tracker, and it is one graph walk. - What
  is blocked, and by what. - The coverage check a decomposition carries, as a
  command that runs, where a section heading only asserts it.

`find` - search across artifacts that returns headings and paths before bodies,
so a search costs tens of tokens where reading the bodies costs thousands.

`index` - regenerate the documentation index from the tree, making the index
rule automatic, so nobody has to remember it. The check that currently fails
when the index drifts becomes a command that fixes it.

`lint` - front matter against a schema. The prior art all does this, and the
JavaScript ecosystem has the pieces. `remark`/`unified` for the Markdown AST
with `@types/mdast`, and `remark-frontmatter` for the preamble. Then
`remark-lint-frontmatter-schema` for JSON Schema validation, or Zod for the
same job in TypeScript terms.

`amend` is the mechanical half of the amendment path. It allocates the
replacement identifier, writes the tombstone, and lists every citation of the
withdrawn one, so the blast radius arrives as a fact nobody has to search for.

## What this buys

Three things, in descending order of how much they matter.

Correctness first. The checks written for this repository found, on their
first run, a requirement identifier allocated twice, eleven dangling links and a
weak opener - none of which careful reading had caught over several days. A
determination that a script makes is one a person stops making incorrectly.

Context second. Every query above replaces reading a document with reading a
line. The reported figures for this class of change are consistent.
`claude-code-spec-workflow` claims 60-80% against loading files individually,
and `Specbound`'s output-compressing proxy reports 60-90% on development
commands. The three-tier retrieval pattern is reported at roughly 10x against
naive injection. None of those is a measurement of this corpus, and the harness
measures its own, inheriting no number.

Latency third, and it is not nothing. A coverage question answered in one
command, where twenty file reads used to answer it, is a shorter loop, and a
shorter loop is where the method stops feeling expensive.

## The dashboard, and why it is a separate tool

A terminal interface over the same corpus - units, their step, pending gates,
plan progress, what is ready, what has drifted - is genuinely useful and must
not be part of the harness.

The reason is a rule the harness already has. `claude-code-spec-workflow` ships
a WebSocket dashboard with a tunnel and optional passwords. The design rejects
it, because a dashboard duplicates what the artifacts say, adds a service to
run, and rots first ([RES-0062-status.md](RES-0062-status.md)). That argument
concerns the harness's dependencies and says nothing about the value of a view.

Separating it resolves the tension cleanly:

- The harness keeps the no-service rule - no service, no daemon, nothing to install for
  the method to work.
- The dashboard is **optional** in exactly the sense the method means: it makes
  work pleasanter and never makes it possible.
- It reads the same files a person reads, so it cannot become a second source
  of truth.
- It can be as elaborate as it likes without any of that landing in a plugin's
  context budget.

For the implementation, the TypeScript terminal ecosystem is unusually mature in
2026, and the reason is adjacent to this project: TypeScript powers the terminal
layer of most agentic coding tools, Claude Code among them.

| Option                       | Trade                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Ink**                      | React for the terminal; the established default, used by Copilot CLI, Wrangler and Prisma, at about 50 MB and a 32 FPS rendering cap |
| **OpenTUI**                  | React or Solid with a Zig rendering core over Bun's FFI; lower memory, no FPS cap, flexbox via Yoga                                  |
| Bubble Tea, ratatui, Textual | Go, Rust and Python - each excellent and each a second language in this tree                                                         |

Ink is the right default here: the corpus is small, the view is mostly static
text, and 32 FPS is irrelevant to a status table. OpenTUI's advantages are real
and are advantages for something this is not.

The honest caveat: a dashboard is a **view**, and the moment it writes anything
it becomes a second way to change state, which the harness has to verify
against. It reads.

## Conclusions

1. One determination per tool, structured output, absence reported -
   [RES-0023-helpers.md](RES-0023-helpers.md)'s contract applies unchanged. 2.
   Front matter is the schema, validated before anything relies on it. 3.
   Queries return identifiers and headings first, bodies on request. 4. The
   index is generated, so no discipline maintains it. 5. The traceability
   matrix stays derived, never stored - as every tool in the prior art does. 6.
   The dashboard is a separate, optional, read-only tool, and its absence
   changes nothing about the method.

## Sources

- [Open source requirements management tools](https://gist.github.com/stanislaw/aa40eb7de9f522ad482e5d239c435ff8),
  a comparison maintained by StrictDoc's author, read 2026-09-20 - the
  file-per-requirement against file-per-document split, and the format
  differences between Doorstop, StrictDoc and Sphinx-Needs.
- [StrictDoc](https://strictdoc.readthedocs.io/en/latest/sphinx/strictdoc_03_faq.html)
  F.A.Q., read 2026-09-20 - its relationship to Doorstop and its traceability
  matrix export.
- [Self-hosted requirements management: rmtoo vs Doorstop vs StrictDoc](https://www.pistack.xyz/posts/2026-06-15-self-hosted-requirements-management-rmtoo-doorstop-strictdoc/),
  read 2026-09-20 - practical positioning of the three.
- [OpenFastTrace](https://github.com/itsallcode/openfasttrace), read 2026-09-20
  - the needs/covers tracing model.
- [remark](https://github.com/remarkjs/remark) and
  [unified](https://unifiedjs.com/explore/package/remark-parse/), read
  2026-09-20 - the Markdown AST, `@types/mdast`, and the typed plugin model.
- [remark-lint-frontmatter-schema](https://github.com/JulianCataldo/remark-lint-frontmatter-schema),
  read 2026-09-20 - JSON Schema validation of front matter as a lint rule.
- [Contentbase](https://contentbase.soederpop.com/), read 2026-09-20 - Zod
  schemas over front matter for types and defaults.
- [OpenTUI](https://github.com/anomalyco/opentui) and
  [OpenTUI: React-based terminal UIs with a Zig rendering core](https://betterstack.com/community/guides/scaling-nodejs/opentui-react/),
  read 2026-09-20 - the architecture, and the Ink comparison including the
  ~50 MB and 32 FPS figures.
- [Terminal UI development guide: Ink, OpenTUI, Bubble Tea, ratatui, Textual](https://labhub.hopto.org/blog/2026-07-31-terminal-ui-development-guide?lang=en),
  read 2026-09-20 - when to use which.
- [From browser to terminal: how TypeScript quietly conquered the AI agent TUI](https://thamizhelango.medium.com/from-browser-to-terminal-how-typescript-the-webs-darling-quietly-conquered-the-ai-agent-tui-d93a4eda62a5),
  read 2026-09-20 - TypeScript as the terminal layer of most 2026 agentic tools.
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow)
  and [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness), read
  2026-09-20 - the two reported token-reduction figures, and the dashboard this
  document argues should be separate.
