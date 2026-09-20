---
id: RES-0021
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Editing and code intelligence

## Summary

Three ways of finding and changing code - text, structural and semantic -
know different things, and only the semantic layer can supply resolved
references and diagnostics. So symbols go to the language server, mechanical
rewrites go to a structural tool, and literals go to text search. The editing
discipline that follows is to read before writing, make the smallest correct
change, never reformat while changing behaviour, and report absence rather than
substituting a weaker answer for a stronger one.

Research for the `editing` and `lsp` skills in `meow-editing`. What the three
ways of finding and changing code actually give you, where each is the wrong
choice, and what a skill has to decide so an agent stops greping for symbols.

## Method

We fetched and read the published material on the two standards on 2026-09-20
for what each layer knows. That included the claim that text and structural
search supply no resolved references and no diagnostics, which is the finding
the conclusions turn on.

The internal repositories were read for which of the three layers they
currently use.

Nothing was run. No search was compared against a language server here, so the
failure modes listed - the shadowed binding, the re-export, the generated call
site - are taken from the sources rather than demonstrated.

## Three layers, and what each knows

The 2026 tooling landscape has settled on two standards - **LSP** for semantic
intelligence and **Tree-sitter** for syntactic structure - with plain text
search underneath both.

| Layer       | Knows   | Examples                                                         | Blind to                                     |
| ----------- | ------- | ---------------------------------------------------------------- | -------------------------------------------- |
| Text search | Bytes   | `grep`, `rg`                                                     | Scope, types, re-exports, generated code     |
| Structural  | Syntax  | `ast-grep`, Comby, Tree-sitter queries, Semgrep                  | Resolution - what a name refers to           |
| Semantic    | Meaning | LSP: definitions, references, diagnostics, rename, type at point | Nothing relevant, but needs a running server |

The distinction that matters: **text and structural search find _names_; only a
language server resolves _bindings_.** A `rg 'fn connect'` finds the string. It
misses the shadowed local, the trait implementation, the re-export under a
different name, the generated call site, and the identically-named function in
a module you were not thinking about. It also finds the same name in a comment,
a test fixture and a changelog.

Reported performance for the semantic path is dramatic where it applies: a
navigation that takes tens of milliseconds through a language server against
tens of seconds of text search across a large repository. The number matters
less than the direction, and the direction is not close.

## When each is right

Text search is right for what it is: finding a literal, a string in a
configuration file, a TODO, a spelling. It is also the honest fallback when no
server is available - as long as the answer says so.

Structural search is the underrated middle. `ast-grep` uses Tree-sitter, so it
matches on syntax rather than bytes, needs no running server, and can _rewrite_
as well as match. For a mechanical change across many files it beats either
neighbour: a parameter added to every call, an import form changed, a
deprecated pattern replaced. It is more precise than `sed`, far cheaper than
editing each site by hand, and available where nobody configured a language
server.

Semantic is right for every question about a symbol: where is this defined,
who calls it, what type is this, what does the compiler already complain about,
rename this everywhere.

The practical ordering for an agent: **semantic if a server is running,
structural for mechanical multi-file rewrites, text for literals and as the
declared fallback.**

## Diagnostics before running anything

The most under-used LSP capability in agent work is diagnostics. A language
server already knows what the compiler will complain about, and reading that is
free compared with running a build. It does not replace the `lint` and
`typecheck` verbs - those are the evidence - but it is the right
first move after an edit, and it shortens the loop before anything is claimed.

## Editing: the failure to design against

The characteristic agent editing failure is the **oversized rewrite**: a change
to one line delivered as a rewritten file, mostly reformatting, with the actual
change buried. It is unreviewable, it conflicts with everything else in flight,
and it defeats the review step the method depends on.

Everything else follows from avoiding it:

- **Read the region before writing it.** An edit made from memory of a file is
  an edit against a file that may have changed.
- **Smallest correct change.** Not the smallest diff that compiles - the
  smallest change that is actually right, which sometimes is larger.
- **Never reformat while changing behaviour.** Formatting is the `fmt` verb's
  job and belongs in its own change, where review can skip it safely.
- **One structural edit beats several textual ones** where a tool can express
  it, because the structural form states the intent and cannot half-apply.
- **Batch independent operations.** Reading four files that do not depend on
  each other is one step, not four.
- **Verify by the gate, not by re-reading.** Re-reading a file to confirm an
  edit landed is a habit that costs tokens and proves less than `lint` does.

## The honest-degradation rule

The temptation when no language server is running is to answer the symbol
question with `rg` and present the result as though it were authoritative. That
is the unresolved-verb failure in a different costume: an answer that was not earned,
delivered with the confidence of one that was.

The rule: say the server is unavailable, say what the search found, and say
what that cannot tell you - "these are textual matches; shadowing, re-exports
and generated call sites are not covered". A reader who knows the limits can
use the result. A reader who does not will trust a rename that missed three
sites.

## Which server, and when it breaks

The server is per-language and therefore a pack's business: `rust-analyzer`,
`gopls`, `pyright` or `ty`, `tsserver`/`tsgo`, OmniSharp,
`lua-language-server`. What is universal, and belongs in `meow-editing`, is the
behaviour when one fails to start, which happens often enough to matter. A
server that has not finished indexing returns empty results and no error, and
empty results look exactly like "no references". `meowctl`'s `rust` skill
already documents this for one language; the general form is that **an empty
result from a server that is still indexing must not be reported as "no
callers"**.

## Conclusions

1. Semantic first for symbols, structural for mechanical rewrites, text for
   literals.
2. Read before writing; smallest correct change; never reformat while
   changing behaviour.
3. One structural edit over several textual ones, where expressible.
4. Batch independent reads and edits.
5. Diagnostics after an edit, before claiming anything.
6. Absence is reported, not substituted - and a text-search answer states
   what it cannot cover.
7. An empty result from an indexing server is not an answer.
8. Evidence still comes from the gate verbs, never from the language
   server's opinion.

## Sources

- [LSP and Tree-sitter ecosystem 2026](https://www.youngju.dev/blog/culture/2026-05-16-lsp-tree-sitter-ecosystem-2026-ast-grep-biome-helix-zed-neovim-treesitter-deep-dive.en),
  read 2026-09-20 - the two standards, what each layer knows, and the claim that
  text and structural search cannot supply resolved references or diagnostics.
- [Language Server Protocol ecosystem 2026](https://zylos.ai/research/2026-01-13-language-server-protocol-ecosystem/),
  read 2026-09-20 - the reported navigation latency difference between a
  language server and repository-wide text search.
- [ast-grep](https://github.com/ast-grep/ast-grep) and its
  [language server documentation](https://deepwiki.com/ast-grep/ast-grep/6-language-server-protocol),
  read 2026-09-20 - Tree-sitter-based structural search and rewrite without a
  running server.
- [TypeScript repository indexing for code agent retrieval](https://arxiv.org/pdf/2604.18413),
  read 2026-09-20 - retrieval over a repository for agent use.
- `~/workspace/meowctl/.claude/skills/rust/SKILL.md`, read 2026-09-20 - what an
  LSP answers and what to do when the server fails to start, from which the
  still-indexing caveat generalises.
