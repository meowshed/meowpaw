---
id: RES-0265
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0011, RES-0264
---

# Migrating the record

## Summary

When the method changes, every artifact already written was written to the old
shape, and nothing in this corpus says what happens to them. The established
answer is expand, migrate, contract: accept both forms, move everything, then
remove the old. The wire-format conventions add the rule that makes it safe
over time. A retired name is reserved and never reused, because reuse silently
reinterprets old data and fails for nobody. Both rules apply here, with one
difference that makes the harness's job easier and its mistakes worse. The
corpus is small enough to rewrite in an afternoon, which is exactly what makes
an unreviewed bulk rewrite tempting. This project has already corrupted its own
sources that way twice.

Research for changing the shape of artifacts that already exist. It does not
cover what a record is, which is
[RES-0011-artifact-lifecycle.md](RES-0011-artifact-lifecycle.md), nor how
releases are numbered, which is
[RES-0264-versioning-and-release.md](RES-0264-versioning-and-release.md).

## The question

Today a template changed and a hundred and seventeen documents were rewritten
by hand to match it. Two artifact kinds were renamed earlier in the same
project. A status vocabulary was unified. Each time, the question _what happens
to what already exists_ was answered by doing it, and no rule decided.

## Method

We fetched and read the established interface-change technique on 2026-09-20
for its three phases and its stated costs. We fetched the wire-format
compatibility guidance for which changes are safe, which are not, and the
reserved-name rule.

The modernising tool in one language's toolchain, already researched in this
corpus, supplied the automated-rewrite precedent.

This project's own history supplied the failure cases, which we observed and
hypothesised nowhere: two bulk renames that corrupted material outside their
intended scope.

Nothing was migrated as an experiment. No migration tool was written.

## Findings

### The three phases, and the one that gets skipped

Expand augments the interface to support both the old and the new form,
without changing existing users. **Migrate** moves them across, incrementally.
Contract removes the old form once nothing uses it.

The stated costs are the honest part. Two forms are maintained during the
migration, users can be confused about which to use, and the whole thing takes
discipline. And _"if the contract phase isn't completed, the codebase ends up
worse than initially."_

That last one is the failure to design against here. A corpus that accepts two
front-matter spellings forever is worse than one that accepted only the old
one, because every check, every reader and every generator now has to know
both.

So a migration is finished or it is never started. The way to make that true is
to name the release that removes the old form at the moment the new one is
introduced.

### A retired name is reserved, and reuse is the dangerous mistake

The wire-format guidance draws a line this corpus has drawn for identifiers and
not for anything else. Adding a field is safe, and removing one is safe
**provided the retired number is reserved**. Reuse is prohibited outright:
_"Field numbers should never be reused."_ The reason is that reuse fails for
nobody and silently reinterprets old data.

The corpus already applies exactly this to artifact identifiers: permanent once
cited, a withdrawal leaves a gap, never reallocated. What it has not applied it
to is **field names and vocabulary values**.

A status value that is retired and later reused for a different meaning makes
every old artifact carrying it wrong without anything failing. Same for a
front-matter key, a commit type, a verb name.

So the rule generalises: a retired name is recorded as retired and is not
reused, and the record of retirements is part of the method, where folklore
remembers nothing.

### What is safe to change, mapped onto this corpus

| Change                             | Safe?               | Why                                                |
| ---------------------------------- | ------------------- | -------------------------------------------------- |
| Add an optional front-matter field | Yes                 | Old artifacts parse; readers default it            |
| Add a value to a vocabulary        | Yes                 | Old artifacts never used it                        |
| Make an optional field required    | No                  | Every existing artifact becomes invalid at once    |
| Rename a field                     | No                  | Two names for one thing until every artifact moves |
| Change a field's meaning           | No, and worst       | Nothing fails; every old artifact is now misread   |
| Remove a field                     | Yes, after contract | Provided the name is reserved                      |
| Add a section to a template        | Yes, with a window  | Existing documents lack it until migrated          |

The fourth row has no mechanical signal, and it is the one this project keeps
meeting. The research template's conclusions were always required, and the
requirement that each conclusion trace to a finding is new. Nothing about the
old documents becomes invalid; they are only unchecked for something they were
never asked for.

That is the case where the method has to decide between migrating and
grandfathering, and the honest options are only two: migrate everything, or
record explicitly that documents before a given release are exempt. What is not
honest is a check that quietly passes because the older documents are not
examined.

### Automated rewriting exists, is safe in one language, and is the model

One language's toolchain ships a modernising tool that rewrites source to use
newer features, with a preview mode, and which discards any fix touching
generated files. Its safety comes from operating on a parsed representation,
where text substitution has none.

That is the distinction this corpus has twice failed on. Two bulk renames done
with text substitution corrupted material outside their scope. A published URL
was rewritten into a link to one of this project's own documents, and a path
inside quoted external material was rewritten to match this project's layout.
Both were textually correct and semantically wrong, and both survived until
something else checked the links.

So a migration that touches many files parses, and substitutes nothing: front
matter as structured data, links as links, quoted material as quoted material.
Where no parser is available, the migration gets smaller and never cleverer.

### A migration is a reviewable change, and a big one is worse

The temptation specific to a small corpus is that a hundred documents can be
rewritten in one command, which produces a single change too large for anyone
to review. The review research already says what happens past a size: the
review becomes an approval and nothing distinguishes the two.

So a migration is split the way any large change is - by kind, by directory, or
by mechanical step - and each part is separately checkable. The mechanical part
is separated from the editorial part, because a rename can be verified by a
check and a rewritten paragraph cannot.

### Migration needs its own evidence, and the check is the trace

The corpus already checks coverage in both directions and identifier
resolution. A migration's evidence is that those checks pass **and** that a
count was preserved: the same number of artifacts, the same identifiers, no
new orphan.

The honest addition is a before-and-after count, where a claim proves nothing,
because a migration that loses an artifact loses it silently - the file is
gone, nothing references it, and every check passes.

## Conclusions

1. A change to the record's shape runs as expand, migrate, contract, and the
   release that removes the old form is named when the new one is introduced. 2. An unfinished migration is worse than none, because every check, reader
   and generator then has to know both forms forever. 3. A retired field name
   or vocabulary value is reserved and never reused, since reuse does not fail
   - it silently reinterprets artifacts already written. 4. The retirements are
     recorded as part of the method, because nobody remembers them. 5. Adding an
     optional field or a vocabulary value is safe; making a field required,
     renaming one, or changing its meaning is not. 6. Changing a field's meaning
     is the worst change, because nothing fails and every old artifact is now
     misread. 7. A new obligation on existing artifacts is either migrated or
     explicitly grandfathered, and a check that passes because older artifacts
     are not examined is dishonest. 8. A bulk migration parses, and substitutes
     nothing. Front matter is edited as structured data, links as links, quoted
     material left alone - because this project has twice corrupted its own
     sources with text substitution that was correct and wrong. 9. Where no
     parser is available, the migration gets smaller and never cleverer. 10. A
     migration is split into separately reviewable parts, since one hundred-file
     change is approved, and reviewed by nobody. 11. The mechanical part is
     separated from the editorial part, because one can be verified by a check
     and the other cannot. 12. A migration's evidence includes a before-and-after
     count, because a lost artifact is lost silently and every check still
     passes.

## Sources

All read 2026-09-20.

- [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) - the
  expand, migrate and contract phases and what each does; the stated costs of
  maintaining two interfaces, client confusion and the discipline required; and
  the warning that a codebase whose contract phase is never completed ends up
  worse than it began. - [Protocol Buffers language
  guide](https://protobuf.dev/programming-guides/proto3/) - which changes to a
  message type are safe and which are not; the requirement to reserve a removed
  field's number; and the rule that field numbers should never be reused, with
  silent misinterpretation of existing data as the reason. -
  [RES-0102-go.md](RES-0102-go.md) - the modernising tool that rewrites source
  on a parsed representation, offers a preview mode, and discards fixes that
  touch generated files. - [RES-0070-who-verifies.md](RES-0070-who-verifies.md)
  - that review effectiveness falls with the size of what is reviewed, which is
    why a migration is split. - This project's own history, observed 2026-09-20:
    two bulk text substitutions that corrupted material outside their intended
    scope - an external address rewritten into a link to an internal document,
    and a path inside quoted material rewritten to match this project's layout -
    both found later by a link check, which the review had missed.
