---
id: RES-0221
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0014, RES-0201
---

# The `conventional-commits` skill

## Summary

The specification requires a type and a description, defines only two types and
permits any other. So the type vocabulary is the repository's decision, and a
check validates against that declaration and never against a list baked into a
tool. What the method adds is where the value is: a body only where the reason
is not evident from the diff, and the body says why, which is the one thing a
commit message can carry that the diff cannot.

Research for one source-control convention: what a commit message looks like.
It is a method question - the commands that produce a commit belong to a tool
pack, because a method plugin may not name a tool.

Its siblings are [RES-0222-branching.md](RES-0222-branching.md),
[RES-0223-pull-requests.md](RES-0223-pull-requests.md) and
[RES-0224-attribution.md](RES-0224-attribution.md).

## Method

We fetched and read the specification on 2026-09-20 and quote its normative
clauses in full, because most projects that claim to follow it follow a folk
version.

The method's own additions come from the existing commit research and the
public-repository research, and we opened no new source for them.

Nothing was measured; no history was sampled to check how well the convention
is followed.

## The specification, and what it actually requires

The published specification is short, and its normative parts are quoted here
in full, because most projects that claim to follow it follow a folk version.

> Commits MUST be prefixed with a type, which consists of a noun, `feat`,
> `fix`, etc., followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED
> terminal colon and space.
>
> A description MUST immediately follow the colon and space after the
> type/scope prefix.

The body and footers are optional. A breaking change is marked either by `!`
before the colon or by an uppercase `BREAKING CHANGE:` footer.

The mapping to versioning is stated: `fix` is a patch, `feat` is a minor, a
breaking change is a major.

And the clause most often forgotten: _"Types other than `feat` and `fix` MAY be
used"_. The type vocabulary is the project's, and the specification does not
supply one beyond those two.

## Which means the type vocabulary is a decision, and must be declared

A project that uses `chore`, `refactor`, `docs`, `test` and `build` is using a
convention that is conventional only by repetition. The specification permits
it and defines none of it.

So the repository declares its type vocabulary, and a check validates against
that declaration, never against a list baked into a tool. This project's own
vocabulary includes `spec:`, which no published list contains and which is
correct for a repository whose main product is a record.

## What the method adds beyond the specification

The subject is imperative and short. _Add_, and never _added_ or _adds_,
because the subject completes the sentence _this commit will…_.

A body only where the reason is not evident from the diff. A body that
restates the diff is a comment restating the line below it, with the same
failure: it is wrong the first time the code changes and nobody notices.

The body says why. That is the whole of what a commit message can carry
that the diff cannot, and it is the reason a generated commit message is
insufficient - a generated message describes what changed, which is the one
thing the reader can already see.

Trailers are part of the contract. This repository requires a `Signed-off-by`
trailer and a cryptographic signature on every commit, which makes the trailer
block a structured part of the message that a check can read.

## The squashed commit changes what a message is for

A unit of work lands on the main branch as **one squashed commit**, so the
history reads as a list of what the project gained, and never as a transcript
of how it got there.

That changes the audience. The messages on a branch are notes to the author;
the squashed message is the one a reader of the history sees, and it is the
only one that has to stand alone.

It also means the squashed message is written at the end, when what the work
turned out to be is known - which is a better moment to write it than the
beginning.

## What it must refuse

A subject that describes the process and not the change: _address review
comments_, _fix tests_, _wip_.

A body generated from the diff.

A type outside the declared vocabulary, which a check settles and no judgement
is needed for.

Any attribution, which is
[RES-0224-attribution.md](RES-0224-attribution.md).

## Conclusions

1. The subject carries a declared type, an optional scope, an optional breaking
   marker, and a description, in the specification's form. 2. The type
   vocabulary is declared by the repository, because the specification defines
   only `feat` and `fix` and permits any other. 3. A check validates types
   against the repository's declaration, and never against a list baked into a
   tool. 4. The subject is imperative and short. 5. A body is written only
   where the reason is not evident from the diff, and it says why the change
   was made. 6. A generated message is insufficient, since it describes what
   changed, which the reader can already see. 7. Trailers are part of the
   message contract, including sign-off where the repository requires one. 8. A
   breaking change is marked in the subject or in an uppercase footer, and maps
   to a major version. 9. A unit of work lands as one squashed commit, whose
   message is written at the end and is the only one that must stand alone. 10.
   A subject that describes the process and not the change is refused.

## Sources

All read 2026-09-20.

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
  - the required type and description with optional scope and breaking marker;
    optional body and footers; breaking changes by `!` or an uppercase
    `BREAKING CHANGE` footer; the mapping of `fix` to patch, `feat` to minor and
    a breaking change to major; and that types other than `feat` and `fix` may be
    used, with none defined.
- [RES-0014-commits.md](RES-0014-commits.md) - the method's commit rules, the
  squashed commit, and where the reason belongs.
- [RES-0066-public-repository.md](RES-0066-public-repository.md) - sign-off and
  signing as part of the commit contract in this repository.
