---
id: RES-0066
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Committing to a public repository

## Summary

Making the repository open changes what the platform can enforce and what it
cannot. Signing and sign-off join the commit contract, where they used to be
preferences, and the allowed-signers file becomes repository configuration that
no personal setting replaces. The attribution ban also has to survive tooling
that adds attribution by default. What the platform cannot enforce is the part
a person still has to do.

Research for what changes when the repository is open to everyone.
[RES-0014-commits.md](RES-0014-commits.md) already covers the commit
conventions, and [RES-0022-forge.md](RES-0022-forge.md) the forge mechanics.
This covers what a public repository owes a contributor who has never seen it,
and a consumer who will never read it.

It covers what the platform can and cannot enforce, the measurable standards
that exist, what a sign-off is and is not, and what makes a history usable a
year later. It does not cover licensing, which is
[RES-0013-comments.md](RES-0013-comments.md).

## The question

A private repository can rely on everyone already knowing how it works. A
public one cannot, and the cost of that assumption falls on people who arrive
later. A contributor who cannot tell what a good change looks like. A
maintainer who cannot tell whether a commit is from who it claims. And a
consumer who cannot tell what a release was built from.

The harness already writes commits. The question is which of these obligations
it must carry itself, which it must ask the repository to declare, and which it
must refuse to proceed without.

## Method

The platform's documentation on signing, verification and repository
protections was fetched and read on 2026-09-20, together with the published
guidance on open-source contribution practice.

The internal repositories were read for what they already require of a commit.

Nothing was configured or verified as an experiment for this document; the
signing behaviour described was taken from the documentation. Signatures on
this repository's own commits were checked separately, outside this
document.

## Findings

### The platform enforces some of the convention and none of the wording

GitHub's rulesets can require signed commits, require linear history, require a
pull request before merging, require status checks to pass, block force pushes
and require deployments to succeed. Knowing that set exactly matters, because
of what is absent from it: **no rule matches a commit message pattern and none
constrains the author's address.**

So the message convention cannot be delegated to the platform. A repository that
wants its subjects in the imperative, its trailers present and its types
meaningful has to check that itself, before committing, and the harness is the
only thing positioned to do it.

The signing rule is the sharpest of the six: with it enabled, only commits that
are signed **and verified** can be pushed at all. That turns a convention into a
precondition, and it turns an unsigned commit from a lapse into a rejected push.

### There is a measurable ladder, and it is tiered on purpose

OpenSSF Scorecard scores branch protection in tiers, and the tiers say which
protections carry the most weight:

| Score | What it takes                                                                   |
| ----- | ------------------------------------------------------------------------------- |
| 3     | Force pushes blocked and deletion blocked                                       |
| 6     | A pull request required, at least one reviewer, branches current before merging |
| 8     | At least one status check required                                              |
| 9     | Two reviewers, and code owner approval                                          |
| 10    | Stale reviews dismissed on new commits, and administrators included             |

Two of its other checks bear directly on a harness that writes workflows. Token
permissions: the top level is read-only and write is declared per job, which
applies the least-privilege rule to a token, where it usually applies to a
person. Dangerous workflows: never check out untrusted code under a trigger
that runs with write access, and never let an untrusted context value flow into
something executable.

Its code review check adds one thing the others do not say: **a review by a bot
does not count**, and unreviewed human changes cost significantly. A harness
that reviews its own work has not had its work reviewed.

### A sign-off is a declaration, and a signature is a proof

The Developer Certificate of Origin is four conditions, and the last one repays
careful reading. The contribution and the project are public, and a record of
the contribution, the personal information in the sign-off included, is
maintained indefinitely. Signing off is therefore a statement a person makes
about their right to contribute, made permanently and in public.

A cryptographic signature says something else entirely: that the commit was not
forged. Neither substitutes for the other, and a repository that asks for one
and not the other has half an answer. The two are routinely confused, including
by the tooling, including by tooling that calls both "signing".

The kernel's rule on the chain is the part most projects get wrong: the sign-off
chain reflects the **real route** a change took, with the first entry signalling
authorship. It is not a list of people who approve.

### Other trailers need the named person's permission

`Reviewed-by`, `Acked-by`, `Tested-by` and the rest attribute a position to a
named human. The kernel requires explicit permission before adding any of them,
excepting only `Cc`, `Reported-by` and `Suggested-by`.

For a harness this is a hard rule, and no matter of etiquette. An agent writing
`Reviewed-by` for a person who has reviewed nothing is fabricating a record,
which is a fabricated requirement wearing a different costume.

### A history is for bisecting

The kernel's two rules are one logical change per patch, and **the tree builds
and runs after every patch in a series**. The second is what makes `git bisect`
usable, and the reason given is exact: someone bisecting a later problem will
land on the broken middle commit and blame it.

Squashing a task into one commit satisfies the first. It does not by itself
satisfy the second, because a squashed commit can still leave the trunk red if
its checks ran against the branch and never against the merged result.

### The convention carries the release decision, and the breaking change

Conventional Commits maps `fix` to a patch release and `feat` to a minor one,
and a breaking change to a major one, marked either by `!` before the colon or
by a `BREAKING CHANGE:` footer. Its footers are git trailers, which is why a
sign-off, a `Fixes:` reference and a breaking-change note are one mechanism,
and never three.

The consequence for an agent is that the type is a release decision taken at
commit time by whoever writes the subject line, and a mis-typed commit is a
mis-numbered release.

### What a public repository owes a contributor is a short list of files

The community-health set is settled: a README, a licence, contributing
guidelines, a code of conduct, a security policy, issue and pull request
templates, and code owners. The mechanics are that **`CODEOWNERS` must live in
`.github/`** to take effect, and that an organisation can supply defaults for
all of them from a `.github` repository, so a project inherits them and copies
nothing.

### Provenance is the consumer's half of the same question

Signatures answer "who wrote this commit". Build attestations answer "what was
this artifact built from": a workflow with `id-token: write`, `contents: read`
and `attestations: write` produces a record a consumer verifies with
`gh attestation verify PATH -R OWNER/REPO`.

Scorecard scores a release signed with a detached signature at 8 and one
carrying provenance at 10. That is the clearest published statement that a
record of how an artifact was made beats a signature on the artifact.

## Conclusions

1. The message convention is the harness's job, because the platform has no
   rule for it. Signed commits, linear history, reviews and status checks can
   all be required by a ruleset; a subject in the imperative cannot. 2.
   Required signed commits turn signing into a precondition, so a harness that
   cannot sign refuses to commit, and produces no commit that the push will
   reject. 3. The protections have a known order of value: block force pushes
   and deletion first, then require a pull request with a reviewer, then a
   status check, then code owner approval. 4. A workflow's token is read-only
   at the top and write per job, and no workflow may check out untrusted code
   under a trigger that holds write access, or let an untrusted value reach
   something executable. 5. A review by the thing that wrote the change is not
   a review. Where the harness reviews its own work, it MUST say that the
   change is unreviewed by a human, and its own pass counts for nothing. 6. A
   sign-off and a signature are different obligations and a repository asking
   for one still needs the other. 7. The sign-off chain records the route a
   change took, and approves nothing; the first entry is authorship. 8. A
   trailer naming a person requires that person's permission, except the three
   that merely record where something came from. An agent MUST NOT write one on
   someone's behalf. 9. Every commit on the trunk leaves it buildable and its
   checks passing, because the next person to bisect will land on whichever one
   does not. 10. The type of a commit is a release decision, and a breaking
   change is marked in the commit, because nobody remembers it at release time. 11. A public repository carries a fixed set of files for people who arrive
   later, code owners among them, in the place the platform looks. 12. A
   consumer needs provenance as well as a signature: a record of what an
   artifact was built from, verifiable without trusting the publisher.

## Sources

All read 2026-09-20.

- [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
  - require signed commits, require linear history, require a pull request
    before merging, require status checks, block force pushes, require
    deployments; and the absence of any rule matching a commit message or an
    author address.
- [OpenSSF Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
  - the five branch-protection tiers and what each requires, that a bot review
    does not count toward code review, the least-privilege rule for workflow
    tokens, the dangerous-workflow patterns, and the scoring of a signed release
    against one carrying provenance.
- [Developer Certificate of Origin 1.1](https://developercertificate.org/) - the
  four conditions, and that the record including the sign-off is maintained
  indefinitely in public.
- [Submitting patches, the Linux kernel](https://www.kernel.org/doc/html/latest/process/submitting-patches.html)
  - one logical change per patch, the tree building and running after every
    patch in a series, the sign-off chain reflecting the real route with the first
    entry signalling authorship, and that every trailer except `Cc`,
    `Reported-by` and `Suggested-by` needs the named person's explicit permission.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) -
  the structure, the mapping of `fix` and `feat` onto patch and minor releases,
  the two ways to mark a breaking change, and that footers are git trailers.
- [Creating a default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
  and [Essential documents for new contributors](https://www.sonatype.com/blog/open-source-best-practices-key-documents-to-help-welcome-new-contributors-to-your-project)
  - the file set, that `CODEOWNERS` must be in `.github/`, and that an
    organisation can supply defaults from a `.github` repository.
- [Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds)
  - what an attestation establishes, the three permissions a workflow needs, and
    how a consumer verifies one.
