---
id: RES-0141
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0026, RES-0005
---

# qmd

## Summary

Retrieval over this corpus has to run locally, because a tool that sent the
documents to a service would be sending the repository to a third party on
every search. The three modes answer different questions, and none of them is
merely faster, and the highest-quality one involves a model's judgement - which
makes it the best answer and the least explainable. So an absence is asserted
from keyword search, and a hit is a chunk of a document.

Research for one supported tool. qmd is local semantic search over a corpus of
Markdown, which is what the harness uses to find the document that answers a
question when nobody remembers its name.

It covers what it indexes, how it chunks, what its three search modes cost and
answer, where its state lives, what the pack authors, and what the skill has to
contain.

It does not cover memory and context gathering as a method question, which is
[RES-0026-memory.md](RES-0026-memory.md).

## The question

A corpus of several hundred linked documents cannot be found by reading it, and
cannot be found by grep either, because the question a person asks rarely
contains the words the document used.

So the question is what a retrieval tool over this corpus can honestly return,
and what a pack must say about a result so that a citation from it is
trustworthy.

## Method

The tool's repository was fetched and read on 2026-09-20 for the three
search modes, the chunking parameters, the models it downloads and where its
index lives.

We read the index location under a cache directory and assumed nothing, because
it is what justifies treating results as machine-local and regenerable.

Nothing was installed, indexed or searched. No comparison between the modes was
run here, so their differences are taken from the tool's own description.

## Findings

### Everything is local, which decides more than it sounds like

qmd runs entirely on the machine, with three GGUF models downloaded and cached:
an embedding model of around 300MB, a reranking model of around 640MB, and a
query expansion model of around 1.7B parameters.

That is the property that makes it usable here at all. A retrieval tool that
sent the corpus to a service would be sending the repository's documents to a
third party on every search, which is the same exposure repomix's security
check exists to limit - and a search happens far more often than a pack.

The cost is real and the pack states it: roughly a gigabyte of model weights,
and a first run that downloads them.

### The three modes answer three different questions

| Mode      | What it does                                        |
| --------- | --------------------------------------------------- |
| `search`  | BM25 full-text keyword matching                     |
| `vsearch` | Vector similarity over embeddings                   |
| `query`   | Both, with query expansion and reranking by a model |

The difference that matters to a pack is not latency. `search` finds documents
containing the words; `vsearch` finds documents about the subject; `query`
expands the question, searches both ways and has a model rank the results.

So a `search` miss means the words are absent, which is a fact about the
corpus. A `vsearch` miss means nothing was semantically near, which is a fact
about the embedding. And a `query` result has been through a model that decided
what was relevant, which makes it the best answer and the least explainable
one.

For a method built on citing evidence, that ordering is backwards from the
usual preference. The highest-quality mode produces a result whose provenance
includes a model's judgement, so a report says which mode produced a hit, and a
claim that something is _not_ in the corpus is made with `search`, because
`query` ranks and settles nothing.

### Chunking is boundary-aware, which changes what a citation points at

Documents are split into roughly 900-token chunks with about 15% overlap, and
the split points are chosen by scoring, where counting tokens would cut
mid-sentence: headings from H1 to H6, code blocks and paragraph boundaries
score higher, so a chunk tends to be a semantic unit.

Two consequences. A hit is a chunk of a document, so a citation names the
section it came from, and the tool guessed that boundary from the document's
structure. And the 15% overlap means the same text can appear in two chunks, so
a count of hits is not a count of places.

For this corpus the boundary scoring is favourable: these documents are
heading-structured by requirement, so chunks align with the sections a person
would cite anyway.

### The index is a cache, and treating it as one avoids a class of error

State lives in `~/.cache/qmd/index.sqlite`: the collections, the full-text
indexes, the vector embeddings and a cache of model responses.

Being under a cache directory is the honest placement, and it is what a pack
must assume. The index may be absent, stale or deleted at any time; it is not
part of the repository and does not travel with it. A result is therefore
_what this machine's index knows_, and a stale index answers about a document
that has since changed.

So a pack re-indexes before it relies on a negative result, and a citation
resolves back to the file, because the index holds a copy.

### It speaks JSON, which is what makes it usable by a program

qmd exposes collection management, embedding generation, search and document
retrieval as commands, with JSON output among its formats for programmatic use.

That is the minimum bar for a tool the harness calls, and it is met.

### What the pack authors

The collection configuration - which directories are indexed and under what
name - and nothing inside the repository, since the index is a cache rather
than a project artifact.

### What a reviewer needs that no command reports

Whether a claim that something is absent from the corpus was made with keyword
search or with the model-ranked mode.

Whether the index was current when the search ran.

Whether a cited chunk's boundary cut a qualification off the end of a
statement, which is the specific way a chunked retrieval misleads.

Whether the same passage was counted twice because of the overlap.

### What the skill has to contain

In the body, in this order:

1. Which mode for which question. Keyword for presence and absence, vector for
   subject, hybrid for the best single answer. 2. The negative-result rule. An
   absence is asserted from keyword search, never from a model-ranked result. 3. Freshness. The index is a cache; re-index before relying on it, and
   resolve a hit back to the file. 4. Citation shape. A hit is a chunk; name
   the file and section, and read the surrounding text before quoting. 5. What
   must never happen. Citing the index's copy of a document. Asserting absence
   from `query`. Reporting a hit count as a count of places.

In supporting files: the mode comparison; the chunking parameters; the
index location and re-indexing commands; and the dated facts with what to
re-check.

## Conclusions

1. qmd runs entirely locally, which is why it is usable over a corpus the
   harness must not transmit, and the model weights it downloads are a cost the
   pack states. 2. The search mode is recorded with every result, because the
   three modes answer different questions and only one of them involves a
   model's judgement. 3. An absence is asserted from keyword search, never from
   the model-ranked mode, since a reranked miss is a statement about ranking
   rather than about the corpus. 4. A hit is a chunk of a document, so a
   citation names the file and the section and the surrounding text is read
   before anything is quoted. 5. A hit count is not a count of places, because
   chunks overlap by about a sixth and the same passage can appear twice. 6.
   Chunk boundaries are the tool's guess, scored from headings, code blocks and
   paragraphs, so a quotation near a boundary is checked against the file for a
   qualification that fell outside. 7. The index is a cache and may be absent
   or stale, so it is refreshed before a negative result is relied on and a
   citation resolves back to the file. 8. The index is not part of the
   repository and does not travel with it, so a result describes this machine
   and never the project. 9. JSON output is used, since the pack calls the tool
   as a program rather than reading it. 10. The pack authors the collection
   configuration and nothing in the repository. 11. The skill body carries mode
   selection, the negative-result rule, freshness, citation shape, and the
   prohibitions, in that order.

## Sources

All read 2026-09-20.

- [tobi/qmd](https://github.com/tobi/qmd) - an on-device search engine over
  Markdown notes, transcripts and documentation running entirely locally; the
  three modes `search` for BM25 keyword matching, `vsearch` for vector
  similarity and `query` for a hybrid with query expansion and model reranking;
  chunking at roughly 900 tokens with about 15% overlap using a scoring
  algorithm that favours headings, code blocks and paragraph boundaries over
  hard token cuts; the three cached GGUF models for embedding, reranking and
  query expansion; the index at `~/.cache/qmd/index.sqlite` holding collection
  metadata, full-text indexes, vector embeddings and a model response cache;
  and command-line access with JSON among the output formats.
