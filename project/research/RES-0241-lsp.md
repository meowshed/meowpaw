---
id: RES-0241
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0021, RES-0201
---

# The `lsp` skill

## Summary

A text search for a symbol finds the string and misses the shadowed binding,
the re-export, the generated call site and the aliased import. It produces an
answer that is too small, which is the dangerous direction. Support is
negotiated, and guaranteed nowhere, so a connected server does not mean a
question can be answered, and three states have to stay distinct: answered by a
server, answered by search because none runs, and answered by search because
the server cannot.

Research for one skill: when a language server is connected, symbol questions
go to it, and never to a text search.

Its sibling is the editing skill, whose research is
[RES-0021-editing.md](RES-0021-editing.md).

## The question

An agent answering _where is this used_ with a text search gets an answer that
looks complete and is not. The failure is silent, which is why a skill carries
it, where a habit is forgotten.

## Method

The protocol specification was fetched and read on 2026-09-20 for the request
vocabulary, the capability negotiation at initialisation, the statement that
not every server supports every feature, and the instruction to ignore unknown
properties.

The editing research already in this corpus supplied what each of the three
layers knows.

Nothing was run. No search was compared against a language server here, so the
four failure modes come from the sources, and we demonstrated none.

## Findings

### What a search misses that a server does not

A grep for a symbol name finds the string. It misses:

- **The shadowed binding** - a different symbol with the same name, counted as
  a use.
- **The re-export** - a use that names the symbol through another module.
- **The generated call site** - a use that exists after a macro, a derive or a
  code generator has run.
- **The aliased import** - a use under a different name, which the search never
  sees at all.

The first three produce answers that are wrong in a way the reader cannot
detect. The fourth produces an answer that is too small, which is the more
dangerous direction: a rename based on it compiles and breaks something else.

### The protocol's vocabulary, and which requests answer which question

| Question                     | Request                                                  |
| ---------------------------- | -------------------------------------------------------- |
| Where is this defined?       | `textDocument/definition`                                |
| Where is this used?          | `textDocument/references`                                |
| What is this?                | `textDocument/hover`                                     |
| What type is this?           | `textDocument/typeDefinition`                            |
| Who implements this?         | `textDocument/implementation`                            |
| What is in this file?        | `textDocument/documentSymbol`                            |
| Where is this name anywhere? | `workspace/symbol`                                       |
| Rename this everywhere       | `textDocument/prepareRename`, then `textDocument/rename` |
| What is wrong here?          | `textDocument/publishDiagnostics`                        |
| Who calls this?              | the call hierarchy requests                              |

Two of those are underused and are the reason this skill pays for itself.

`workspace/symbol` answers _where is anything called this_ across the
project, which is the question a search is usually a bad proxy for.

`prepareRename` before `rename` validates that the rename is possible
before anything is edited, which is the difference between a refused rename and
a half-applied one.

### Support is optional and negotiated, which is the operational finding

The specification is explicit that _"not every language server can support all
features defined by the protocol"_, and that a server announces what it
implements through capability flags exchanged during initialisation.

So _a server is connected_ does not mean _this question can be answered_. The
skill checks the capability and assumes nothing, and a server without rename
support is a different situation from a server that is absent.

The specification also tells clients to ignore unknown properties, which means
the negotiation is forward-compatible and a capability set may contain more
than the skill knows about. Reading it defensively is the same rule every other
machine-readable interface in this survey gets.

### The honest degradation is the point of the skill

When no server is available, the skill says so and the work proceeds with
search. That is the honest degradation, and the rule that makes it honest is
the one that is easy to omit: **it never presents a search result as though a
server had answered.**

Three states, and they are distinct:

- **Answered by a server**, with the request named.
- **Answered by search, because no server is available.**
- **Answered by search, because the server does not support this request.**

Collapsing the second and third loses the action: one is fixed by starting a
server and the other by choosing a different question.

### Which server serves which language is a pack's business

This skill names no language, which is what keeps it in the method layer. What
belongs here is what to do when a server fails to start, how to tell a missing
server from a failing one, and how long to wait before degrading.

A server that is starting is not a server that is absent, and a skill that
degrades immediately will degrade every time on a large project, which is the
same class of error as reading a check status while a workflow is queued.

## Conclusions

1. A symbol question goes to the language server where one is connected,
   because a text search misses shadowed bindings, re-exports, generated call
   sites and aliased imports. 2. The request that answers the question is named
   in the report, so the answer's provenance is visible. 3. A capability is
   checked, and assumed never, since the protocol states that not every server
   supports every feature and support is announced during initialisation. 4. A
   rename is prepared before it is applied, so an impossible rename is refused,
   and half-applied never. 5. Answered by a server, answered by search because
   none is available, and answered by search because the server lacks the
   capability are three distinct states, and the report says which. 6. A search
   result is never presented as though a server had answered it. 7. A starting
   server is not an absent server, and degrading immediately degrades every
   time on a large project. 8. The capability set is read defensively, because
   the protocol allows properties the skill does not know about. 9. The skill
   names no language, and which server serves which language belongs to the
   pack.

## Sources

All read 2026-09-20.

- [Language Server Protocol specification 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
  - the requests `textDocument/definition`, `references`, `documentSymbol`,
    `hover`, `typeDefinition`, `implementation`, `prepareRename`, `rename` and
    `publishDiagnostics`, `workspace/symbol` and the call hierarchy; capability
    negotiation through `ClientCapabilities` and `ServerCapabilities` at
    initialisation; the statement that not every server can support all features;
    and the instruction to ignore unknown properties.
- [RES-0021-editing.md](RES-0021-editing.md) - the editing discipline this
  skill sits beside, and the code intelligence material it is split from.
