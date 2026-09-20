---
id: RES-0268
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0066, RES-0013
---

# Licensing and provenance

## Summary

This repository already declares its licensing in a bulk file and puts
identifiers in code, and no decision records why. The specification behind that
choice has three requirements and one rule that bites: the licence directory
must contain only licences actually used, so a stale entry is a defect rather
than harmless. The bulk file exists for exactly the case this corpus is: many
small files where a header per file is undesirable. The specification still
prefers headers, because they travel with the file when somebody copies it,
which is what happens to a prose corpus constantly. And provenance is a
separate claim from licensing: the publishing research already found a
mechanism that proves where an artifact was built and explicitly does not prove
what is in it.

Research for how the project declares who owns its material and under what
terms. It does not cover publishing to a forge, which is
[RES-0066-public-repository.md](RES-0066-public-repository.md), nor comment
conventions, which are [RES-0013-comments.md](RES-0013-comments.md).

## The question

The repository carries a bulk licensing declaration, identifiers in its tools,
and a licence file. Every one of those was written without a decision, and the
questions they answer have real answers. Does prose carry a header. What
happens to a licence that stops being used. And what the harness does when it
writes a file into someone else's repository.

## Method

The licensing specification was fetched and read on 2026-09-20 for its three
requirements, the two declaration mechanisms and the rule governing the licence
directory.

The publishing research already in this corpus supplied the provenance side,
and the public-repository research supplied what is already decided about
attribution and signing.

This repository's own state was read: the bulk declaration, the licence
directory and the identifiers in the tools.

Nothing was validated with the specification's own checker, which is the
obvious next step and was not taken, so the claim that this repository complies
is untested.

## Findings

### Three requirements, and the third is the one that decays

The specification requires that every covered file declares its copyright
holders and licences. It also requires that every licence in use has its text
in a licence directory named by its identifier, and that the information reads
for both a machine and a person.

The rule attached to the second is the one that fails quietly over time: a
project _"MUST NOT include License Files for licenses under which none of the
files in the Project are licensed."_

So a licence directory is not an archive. Removing the last file under a
licence obliges removing its text, and a project that accumulates licence files
for dependencies it no longer has is non-compliant while looking thorough.

That is a check rather than a judgement, and it is the kind this corpus prefers.

### Headers travel and bulk declarations do not, which decides where each is right

Two mechanisms. A comment header in the file itself is the recommended form,
and the reason is mechanical: it travels with the file if the file is copied.
A bulk declaration file assigns licensing to many files by pattern, and the
specification names its case - _"large directories where including a comment
header in each file ... is impossible or undesirable"_ - with precedence rules
for overlapping declarations.

For this project the split is already made in practice and this document writes
the reason down. Code carries headers because a source file is copied, vendored
and extracted. Prose is declared in bulk for two reasons. A header above a
document's front matter is noise in the one place the reader looks first, and
the corpus is hundreds of files that move as a set.

The cost of that choice is exactly the property the header has: a document
lifted out of this repository carries no licensing. For a corpus whose
documents are meant to be read elsewhere, that is a real trade and no
technicality. The honest form is to say so, and never to claim the bulk file is
equivalent.

### Provenance is a different claim, and the mechanism says so itself

The publishing research already found the attestation mechanism. It signs a
link between an artifact and the source and build instructions that produced
it, logged publicly. Its own documentation states that it _"does not guarantee
the package has no malicious code."_

So there are three separate claims a project can make, and they are routinely
conflated:

| Claim                             | Answered by                           |
| --------------------------------- | ------------------------------------- |
| Under what terms may this be used | The licence declaration               |
| Who wrote it                      | The commit history and its signatures |
| Where this artifact came from     | A build attestation                   |

The harness touches all three and should never merge them in a report. A signed
commit says who committed; it says nothing about licensing. An attestation says
where a build ran; it says nothing about authorship.

### What the harness does in someone else's repository

This is the part with no prior art and the part that matters most, because the
harness writes files into repositories it does not own.

Three rules follow from what is already decided elsewhere in this corpus.

It declares nothing on the project's behalf. A licence identifier is a legal
claim about ownership, and a tool that writes one into a new file has made that
claim for its user. The harness copies what the repository already does,
reading the header style from neighbouring files as the comment research
requires. Where a repository declares nothing, the harness writes nothing and
reports it.

It never rewrites an existing header. Reformatting a licence header is
modifying a legal notice, and the editing discipline's smallest-correct-change
rule is at its most literal here.

Attribution stays banned and this does not change it. A copyright line
names the holder, which is the person or organisation, and is not attribution
to a tool. The two are separate and the rule against one does not touch the
other.

### The project's own position, stated rather than assumed

Read against the above, this repository's arrangement is defensible and was
undeclared:

- A permissive licence, chosen because the harness is meant to be installed and
  adapted rather than only read.
- Identifiers in the tools, because they are source files that get copied.
- A bulk declaration for the corpus, because hundreds of prose files with
  headers would put a legal notice above every document's first line.
- Sign-off on every commit, which the public-repository research already
  settled and which is a statement about the right to contribute rather than
  about the licence.

The gap is that none of that was written down, which is what makes it a
research document rather than a note.

## Conclusions

1. Every file the project owns is covered by a declaration, either a header
   in the file or a pattern in the bulk file.
2. Code carries headers, because a source file is copied out and the
   declaration travels with it.
3. Prose is declared in bulk, and the cost is stated: a document lifted out
   of the repository carries no licensing.
4. The licence directory contains only licences in use, and a licence that
   stops being used has its text removed, because an unused licence file makes
   the project non-compliant.
5. That rule is enforced by a check rather than by discipline, being
   mechanical.
6. Licensing, authorship and build provenance are three separate claims and
   are never merged in a report.
7. A build attestation proves where an artifact was built and not what is in
   it, as its own documentation states.
8. The harness declares no licence on a project's behalf. It copies the
   style the repository already uses, and where the repository declares
   nothing it writes nothing and reports that.
9. The harness never rewrites an existing licence header, because
   reformatting a legal notice is modifying it.
10. A copyright line is not attribution to a tool, so the attribution ban
    does not touch it.
11. Sign-off is a statement about the right to contribute and is separate
    from the licence declaration.
12. The project's own choices are recorded rather than left implicit, since
    every one of them was made in practice before it was decided.

## Sources

All read 2026-09-20.

- [REUSE Specification 3.3](https://reuse.software/spec-3.3/) - the three
  requirements of per-file licensing information, licence texts in a directory
  named by identifier, and machine and human readable form; comment headers as
  the recommended mechanism because they travel with the file when it is
  copied; the bulk declaration file for large directories where a header per
  file is impossible or undesirable, with its precedence rules; the copyright
  and licence identifier tags; and the rule that a project must not include
  licence files for licences none of its files use.
- [RES-0104-typescript-and-javascript.md](RES-0104-typescript-and-javascript.md)
  - the publishing attestation that links an artifact to its source and build
    instructions, and its own statement that it does not guarantee the package
    has no malicious code.
- [RES-0066-public-repository.md](RES-0066-public-repository.md) - sign-off and
  signing as part of the commit contract, and the attribution ban.
- [RES-0013-comments.md](RES-0013-comments.md) - the licence header form
  declared per repository, generated and checked rather than typed.
- This repository, read 2026-09-20: the bulk declaration, the licence
  directory, and the identifiers carried by the tools. Not validated with the
  specification's own checker.
