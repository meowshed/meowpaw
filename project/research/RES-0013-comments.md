---
id: RES-0013
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Code comments

## Summary

Four language communities publish comment conventions that agree on more than
they disagree about: documentation on everything publicly reachable, and inline
comments by exception. Restating the code is the defect they all name, and the
counterfactual-surprise test is where the line falls. A licence header is
declared per repository and generated, and typed never, and the executable
example is the only form of comment that can fail.

Research for the `code-comments` skill in `meow-prose`. What the conventions
actually require, where the disagreement is, and what a skill must decide so
that "write fewer comments" does not become "write no documentation".

## Method

The four language conventions listed below were fetched and read directly on
2026-09-20, in full, and through no summaries, because the disagreements
between them are in the detail.

The internal repositories were read for what they actually do, which is how the
gap between the published conventions and practice was found.

Nothing was run. The claim that an executable documentation example can fail is
taken from the conventions that describe running them, and we ran none here.

## The one rule everyone agrees on

Comment the why, because the code says the what. A comment restating the code
is noise: `// increment i by 1`, `// return the user`. It is worse than noise,
because it turns wrong the first time the line below changes, and it teaches
the reader to skip comments.

What survives that rule is the non-obvious:

- a constraint - "must be sorted before merge"
- a workaround - "upstream bug #1234 returns 200 on failure"
- a business rule - "weekends excluded per SLA"
- a surprising choice - "O(n^2) here beats the hash for n < 32"

The common formulation: a good comment answers a question the code cannot -
why this approach, what invariant holds, what breaks if you change it.

## The distinction that matters more

The "fewer comments" advice is routinely misread as applying to documentation
comments, and it does not. These are two different things with two different
rules:

|                          | Inline comment                         | Documentation comment                               |
| ------------------------ | -------------------------------------- | --------------------------------------------------- |
| Audience                 | Someone reading this function          | Someone calling it without reading it               |
| Rule                     | By exception, only for the non-obvious | On everything publicly reachable, without exception |
| Failure                  | Restating the code                     | Absent, so the caller reads the implementation      |
| Generated into reference | No                                     | Yes                                                 |

A skill that says only "write fewer comments" produces undocumented public
APIs, which is the more expensive failure of the two. The harness therefore
states both halves: **documentation on everything publicly reachable, and
inline comments by exception.**

## Per-language convention

Each language pack owns the syntax; the obligation is the same everywhere.

| Language   | Doc comment                                                       | Notable rules                                                                                                                                            |
| ---------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rust       | `///` and `//!`, Markdown body                                    | Examples in doc comments are compiled and run by `cargo test --doc` - so a stale example fails the build                                                 |
| Go         | A plain comment immediately before the declaration, no blank line | Every exported name, in complete sentences, with a package comment beginning "Package <name>" and a `Deprecated:` paragraph as a machine-readable notice |
| Python     | Docstrings; `doctest` executes the examples                       | The same executable-example property as Rust                                                                                                             |
| TypeScript | JSDoc/TSDoc                                                       | Types come from the type system, so the comment carries intent rather than signature                                                                     |
| C#         | XML doc comments                                                  | `<summary>`, `<param>`, `<returns>`; the compiler can warn on missing ones                                                                               |
| Lua        | LuaLS annotations (`---@param`, `---@return`)                     | They are also the type information the language server has                                                                                               |
| GDScript   | `##` doc comments                                                 |                                                                                                                                                          |

Go's convention is the one to generalise from, because it is the strictest and
the most mechanically checkable: every exported name, complete sentences, a
fixed opening form, and a deprecation marker tools act on.

The executable-example property in Rust and Python does more than it appears
to: it is the only mechanism here that makes a comment _fail_ when it becomes
untrue, where every other comment goes quietly wrong.

## Licence headers

`hephaestus` carries a full SPDX header on every file: copyright line, licence
identifier, a sentence naming the project, and the terms. It is generated and
checked by `mise run check-headers` / `fix-headers`, which is the right shape -
a header nobody checks drifts, and a header nobody generates gets pasted wrong.

The [SPDX](https://spdx.dev/) short-form identifiers are the standard this
project cites:

```text
SPDX-FileCopyrightText: 2026 Name <email>
SPDX-License-Identifier: Apache-2.0
```

Two things vary per repository, so the repository declares them and the harness
assumes neither: whether a header is required at all, and what it says. An
Apache-2.0 library and a source-available game have different headers, and both
exist among the five source repositories.

## Markdown, where the header cannot go first

A document corpus makes the licence header awkward, and the awkwardness is
structural: **YAML front matter must be the first thing in the file**, so a
comment cannot precede it. Three mechanisms exist and they are not
interchangeable.

Inside the front matter. REUSE 6.2.0 annotates Markdown with front matter by
writing comment lines _within_ the delimited block:

```markdown
---
# SPDX-FileCopyrightText: 2026 Name <email>
# SPDX-License-Identifier: Apache-2.0
id: RES-0001
artifact: research
---
```

The metadata lives where the file's other metadata already is, and nothing
renders. This is the right answer when a header must be present in every copy of
every file.

`REUSE.toml`. A bulk declaration with glob patterns, for cases where editing
individual files is undesirable or impossible. Several projects adopt exactly
this split - headers in source, `REUSE.toml` for Markdown, JSON, lock files and
the root licence.

A `.license` sidecar. A companion file per file, after which "the contents
of the original file are subsequently ignored". For a corpus this doubles the
file count for nothing, and it is the wrong answer here.

### Which one, and why it is a project's choice

For a **documentation corpus**, `REUSE.toml` is usually right. Sixty Markdown
files carrying three lines each is a hundred and eighty lines of metadata, in
documents whose whole purpose is being read. The first thing a reader meets
after the title is then a copyright notice. The prose standard's instruction to
prune every excess word applies to the file as much as the sentence.

For a **source-available or restrictively licensed project** the opposite is
right, and `hephaestus` is the worked example. A full header on every file,
naming the project and the terms, because the licence's value depends on
travelling with each copy. Its headers are generated and checked by a task, and
typed never, which is what keeps them consistent.

So the repository declares this, and the harness decides none of it, and the
declaration says which of the three mechanisms is in use. Whichever it is,
**two tags are required**: `SPDX-FileCopyrightText` and
`SPDX-License-Identifier`. One without the other is no complete statement, and
a repository stating only the licence has not said who holds the copyright.

## The trade-offs a skill has to resolve

Where is the line between "non-obvious" and "obvious"? It is a judgement,
and a skill that pretends otherwise produces either comment spam or
undocumented invariants. The workable test is counterfactual: _would a
competent reader of this code, unfamiliar with the project, be surprised?_ If
yes, comment it. That is checkable in review even though it is not checkable by
a script.

What about a comment that explains badly-named code? The preferred fix is the
name, and the skill says so. But an agent that renames a public symbol to avoid
writing a comment has made a breaking change to avoid a sentence. So: rename
where it is local, comment where the name is part of an interface.

TODO comments. Conventions differ on whether they are acceptable at all.
The position that survives contact with the method: a TODO with no issue behind
it is a defect, because it records an intention nobody is accountable for. The
harness already has somewhere better for it - an open question, or a task added
to the plan, marked as added after approval.

Commented-out code. Deleted, always. Version control is the archive, and a
commented-out block is an archive nobody can search or trust.

## Conclusions

1. Two rules, stated separately. Documentation on everything publicly
   reachable; inline comments by exception. 2. Restating the code is a defect,
   with the counterfactual-surprise test as the line. 3. The licence header
   form is declared per repository, generated and checked, and typed never. 4.
   Prefer the name over the comment where the name is local, and the comment
   where the name is an interface. 5. No TODO without an issue; route it to an
   open question or a plan task. 6. No commented-out code. 7. Prefer the
   executable example where the language runs doc examples, since that is the
   only form of comment that can fail.

## Sources

- [Go Doc Comments](https://tip.golang.org/doc/comment), read 2026-09-20 - the
  strictest of the conventions: every exported name, complete sentences, the
  package-comment opening form, and `Deprecated:` paragraphs that tools warn
  on. - [How to write documentation - the rustdoc
  book](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html),
  read 2026-09-20 - `///` and `//!`, Markdown bodies, and examples compiled and
  run as tests. - [Comments in code: best practices and 4 mistakes to
  avoid](https://swimm.io/learn/code-collaboration/comments-in-code-best-practices-and-mistakes-to-avoid)
  and [10 code commenting best
  practices](https://daily.dev/blog/10-code-commenting-best-practices-for-developers/),
  read 2026-09-20 - comment the why not the what, and the four categories of
  comment that survive that rule (constraint, workaround, business rule,
  surprising choice). - [SPDX](https://spdx.dev/), read 2026-09-20 - the
  short-form identifiers. - [REUSE FAQ](https://reuse.software/faq/), read
  2026-09-20 - `.license` companion files, `REUSE.toml` as a bulk mechanism
  with glob patterns, and when editing individual files is undesirable or
  impossible. - [reuse changelog,
  6.2.0](https://reuse.readthedocs.io/en/stable/history.html), read 2026-09-20
  - Markdown with YAML or TOML front matter annotated with comment lines inside
    the delimited block. - Adoption reports showing the split in practice -
    headers in source, `REUSE.toml` for Markdown, JSON and lock files - in
    [ecmwf/eckit#341](https://github.com/ecmwf/eckit/pull/341) and
    [alunduil/zfs-replicate#712](https://github.com/alunduil/zfs-replicate/issues/712),
    read 2026-09-20, together with the reminder that REUSE requires **two** tags,
    where one is the common mistake. - `~/workspace/hephaestus` file headers and
    `mise.toml` header tasks, read 2026-09-20 - a generated-and-checked licence
    header in practice.
