---
id: RES-0026
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Memory and context gathering

## Summary

Once memory is separated from retrieval, the finding is that the artifacts are
the memory and a separate store is not wanted. What matters is when retrieval
happens: searching before generating a solution changes the answer, and
searching afterwards is only a consistency check. Titles and identifiers come
before whole documents, an index is optional and its absence is reported, and a
decision that is found is followed or amended, and never silently ignored.

Research for `meow-memory`. What "memory" means once it is separated from
retrieval, what the 2026 consensus says about vector search in agent systems,
what `meowary` proves, and where the harness should draw the line.

## Method

The published material on context engineering and agent memory was fetched
and read on 2026-09-20, read against each other because they disagree about
whether a separate memory store is needed.

The internal repositories were read for what they currently keep and where.

Nothing was measured. The claim that searching first changes the answer while
searching afterwards only checks it is taken from the sources and from the
method's own reasoning, and we ran no comparison here.

## Memory is not retrieval

The distinction the field converged on during 2026, and the one that decides
this plugin's shape:

|                   | What it is                                                | Lives              | Example                        |
| ----------------- | --------------------------------------------------------- | ------------------ | ------------------------------ |
| Short-term memory | The conversation so far, including tool calls and results | The context window | What we decided ten turns ago  |
| Long-term memory  | What persists across sessions                             | The repository     | Why the ledger is double-entry |
| Retrieval         | Finding relevant material to put in context               | A tool             | "Where is this decided?"       |

Context engineering is the broader practice - deciding what the model's context
actually contains - and has four pillars: instructions, retrieval, memory, and
the tool surface. Retrieval is one input. A system can run excellent retrieval
and still fail because it has no durable memory, an overloaded tool set, or no
token-budget discipline.

For the harness this resolves a naming confusion: `meow-memory` is about
**long-term memory**, and `meow-qmd` is about **retrieval**. They are different
plugins because they are different problems, and the design's rule that the
tool pack is optional only makes sense once that is clear.

## Where the harness's memory already lives

The harness has a strong advantage most agent-memory systems do not: **its
long-term memory is already written down, in the repository, as artifacts.**
Decision records, requirements with identifiers, design documents with rejected
alternatives, plans with the reason a task was dropped.

That is memory that survives compaction, is reviewable, is diffable, and can be
cited. No vector database, no separate store, no synchronisation problem. The
question for `meow-memory` is therefore not "how do we remember" but "how does
the right part of that get into context at the right moment, cheaply".

## Is a vector index needed at all?

This was contested through 2026 and the honest answer is: often not.

The case against. Long context plus `grep` handles a large fraction of what
vector search was introduced for, particularly over a repository where the
material is structured and named. One documented production pattern
consolidates memory by greping transcripts asynchronously and treating the
result as a tip that settles nothing - with no embeddings and no vector
database in either layer.

The case for. Semantic search finds the decision recorded under vocabulary
nobody would search for. "Why don't we cache this?" does not textually match a
record titled "Staleness beats a second source of truth", and that is exactly
the record that answers it.

What settles it here: the harness's material is _small and well-named_. A
repository has tens of decision records, where these systems index millions of
documents. `grep` over titles and identifiers answers most questions, and the
index earns its place on the remainder - which is real, because the remainder
is precisely the re-litigation `meow-memory` exists to prevent.

So: the index is a genuine improvement and never a prerequisite. That is the
optionality rule, arrived at from evidence and from no wish for tidiness.

## Progressive disclosure applies here too

The pattern reported as roughly a 10x saving against naive retrieval injection
is the same three-tier idea as section 13 of the design, applied to search results:

1. Index result - title, date, identifier. Tens of tokens each.
2. Surrounding context - what this sits next to.
3. Full document - hundreds to a thousand tokens, and only when needed.

The failure it replaces is dumping five whole documents into context because
they matched. `meow-memory` should return titles and identifiers first, and
read the document only when the title does not settle the question.

## What `meowary` proves, and what it warns about

Proves: a context-gathering step before solution generation earns its turn.
`meowary` runs it as "Step 0.5 (Clarify)", searching internal notes and the web
in parallel, and it has an explicit rule that durable findings are written back
into a resource article, and none is left in the conversation. That write-back
is the part most systems omit and is what turns retrieval into memory.

Warns: it depends on `qmd` hard enough that the harness does not work without
it. That is the failure optionality exists to prevent, and it is a real
precedent, where a hypothetical risk convinces nobody.

Two further things transfer: search runs **in parallel**, never sequentially;
and queries are specific - "OAuth port-range error handling", not "error
handling".

## The question this plugin actually answers

Not "what do we know" but **"has this been decided before?"** - asked before
design work starts, so the harness stops re-litigating settled questions.

The obligation that makes it useful: when a decision record is found, the work
either follows it or amends it. Finding a record and ignoring it is
worse than not searching, because the record now has a counterexample in the
history.

## Conclusions

1. Search before generating a solution, because searching afterwards only
   checks it. After is a consistency check; before is what changes the answer. 2. Titles and identifiers first; the whole document only when needed. 3.
   Parallel searches, specific queries. 4. Write durable findings back into an
   artifact, or they are lost with the conversation. 5. The index is optional;
   its absence is reported. 6. A found decision is followed or amended, never
   silently ignored. 7. No separate memory store. The artifacts are the memory,
   which is what makes it reviewable.

## Sources

- [Context engineering: a practical guide for AI
  agents](https://sourcegraph.com/blog/context-engineering), read 2026-09-20 -
  the four pillars, and retrieval as one input among several. - [Agent memory
  is not RAG: a 2026 production field
  guide](https://dev.to/memos/agent-memory-is-not-rag-a-2026-production-field-guide-35ih),
  read 2026-09-20 - short-term against long-term memory, and the grep-the-
  transcripts consolidation pattern with no vector database in either layer. -
  [Is RAG dead? Long context, grep, and the end of the mandatory vector
  DB](https://akitaonrails.com/en/2026/04/06/rag-is-dead-long-context/), read
  2026-09-20 - the case against a mandatory index. - [Context engineering AI:
  how to build smarter LLM agents in
  2026](https://mem0.ai/blog/context-engineering-ai-agents-guide), read
  2026-09-20 - the three-tier retrieval pattern and its reported ~10x saving
  against naive injection. -
  [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) README,
  read 2026-09-20 - Cog Memory's temperature tiers and their line and entry
  caps. - [tobi/qmd](https://github.com/tobi/qmd), read 2026-09-20 - BM25,
  vector search and LLM re-ranking, all local; the three search modes. -
  `~/workspace/meowary/.claude/skills/context-gathering/SKILL.md`, read
  2026-09-20 - Step 0.5, parallel search, query specificity, and the rule that
  durable findings are written back into an article.
