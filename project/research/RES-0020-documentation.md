---
id: RES-0020
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Documentation

## Summary

The four documentation kinds serve different readers in different states, and
the most common defect is a document that is two of them. The two dominant
style guides agree on more than they differ, so their intersection is the
default and the brevity rules are the editing pass. A tool generates the
reference for a public interface, nobody hand-writes it, and the reasons live
in an explanation where a how-to would only carry the steps.

Research for the `documentation` skill in `meow-prose` and for the
`/meow:document` step. What kinds of documentation exist, what the two most
influential style guides actually say, what the best examples do, and where the
trade-offs are.

## Method

We fetched and read the published guidance directly on 2026-09-20. The
four-kind framework gave the taxonomy. Both major style guides gave the style,
read against each other so we could take the intersection and pick neither.

We ran nothing and audited no existing documentation against the framework, so
the claim that mixing kinds is the commonest defect belongs to the framework
and we measured nothing here.

## The four kinds, and why mixing them fails

[Diátaxis](https://diataxis.fr/) is the framework to adopt, because it is the
only one that explains _why_ documentation goes wrong; the others list what
good documentation contains. It places every document on two axes - practical
against theoretical, and specific against general - which produces four kinds:

| Kind         | Serves        | Reader is                        | Answers                                       |
| ------------ | ------------- | -------------------------------- | --------------------------------------------- |
| Tutorial     | Learning      | A beginner being taught          | "Take me through this once so I have done it" |
| How-to guide | A task        | A competent user with a goal     | "I need to accomplish X"                      |
| Reference    | Information   | Someone who knows what they want | "What exactly does this do"                   |
| Explanation  | Understanding | Someone deciding or debugging    | "Why is it like this"                         |

The rule that does the work: a document is one of the four and never two.
The common failures are all mixtures - a tutorial that stops to explain the
architecture, a reference page that editorialises about best practice, a how-to
guide that teaches concepts before getting to the task. Each is unusable for
both audiences it tried to serve.

This maps onto the harness cleanly, and it _already_ does: `design.md` is
explanation, `requirements.md` is reference, a `plan.md` is neither and is
correctly not user-facing documentation at all. `/meow:document` touches the
project's tutorials, how-to guides and reference, and leaves the unit's own
artifacts alone.

### Where Diátaxis is weak

It says little about the README, which is the document most projects actually
have, and it is not opinionated about API reference generated from source. Both
gaps are filled below.

## The two style guides

The [Google developer documentation style guide](https://developers.google.com/style/highlights)
and the [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
agree on far more than they differ, which makes the intersection a safe default.

Both require:

- Second person. "You", and never "we" or "the user". - Active voice, with the
  actor named. - Present tense. - Sentence case for titles and headings, not
  title case. - No end punctuation on headings. - The serial comma. - Numbered
  lists for sequences, bulleted lists for everything else. - Code font for
  code-related text. - Writing for a global audience: no idiom, no cultural
  reference, no jargon that a second-language reader cannot resolve.

Microsoft adds, and it is the more useful half:

- _Bigger ideas, fewer words._ "Ready to buy? Contact us." replaces a sentence
  three times its length.
- _Write like you speak._ Read it aloud. Contractions are correct, not casual.
- _Get to the point fast._ Front-load keywords so the page can be scanned;
  make the next step obvious.
- _Revise weak writing._ Start statements with a verb. Cut "you can" where it
  adds nothing. Avoid "there is", "there are", "there were".
- _Be brief._ Give enough to decide confidently, and prune every excess word.

The last two are the ones that change text most. "You can access Office apps
across your devices, and you get online file storage and sharing" becomes
"Store files online, access them from all your devices, and share them with
coworkers" - same facts, verbs first, half the hedging.

### Where this collides with the harness's own standard

`meow-prose`'s standard, inherited from `meowctl`, requires that **a rule
carries its reason**. Microsoft's guidance is to prune every excess word, and a
reason is words. They are not actually in conflict, because they address
different documents: the reason belongs in _explanation_, and a how-to guide
that stops to justify itself is the mixture Diátaxis warns about. The
resolution is the same one section 13 of the design reaches for skills - placement,
not compromise.

## READMEs

The README is the document with the widest audience and the least agreement
about its shape. What the sources converge on:

- **Inverted pyramid.** The most critical information first, each section
  serving a smaller and more committed audience. A casual visitor reads the
  first few sections; a user reads further; only a contributor reads all of it.
- **A working quick start in the first screen.** Copy-paste-ready commands, not
  prose about installation.
- **Accuracy over completeness.** Every command in it runs.
- **Currency is the differentiator.** The best READMEs are not the ones written
  most carefully on day one but the ones still accurate on day two hundred.

[standard-readme](https://github.com/RichardLitt/standard-readme) is the
closest thing to a specification, so we cite it and reinvent nothing.

The 2026 marketing-shaped advice - hero images, demo GIFs, badge rows, an FAQ -
promotes the project, and it helps nobody trying to use the thing. The harness
should not generate it. A badge that reports CI status earns its place; four
badges as decoration do not.

The currency point is where the harness has something real to offer. Every
source names drift as the actual problem and then recommends discipline as the
cure. `/meow:document` is a step in the chain that runs before verification,
which makes it a mechanism that something enforces.

## Reference, and generating it

Every language in scope has a documentation-comment convention that produces
reference material from source, and the `code-comments` skill already requires
documentation on everything publicly reachable
([RES-0013-comments.md](RES-0013-comments.md) has the per-language detail). The consequence for
this skill: **reference is not hand-written where the language generates it.**
A hand-written reference page for a public API is a second source of truth that
will disagree with the first.

Go's convention is the strictest, and it transfers best as a principle. Every
exported name has a doc comment, comments are complete sentences, and a package
comment begins with "Package <name>". A paragraph beginning "Deprecated:" is a
machine-readable deprecation notice that tools warn on.

## Testable documentation

The strongest idea in this area is that documentation can be executed.

- **Doctests** (Python's `doctest`, Rust's `cargo test --doc`) run the examples
  in the documentation as tests. A stale example fails the build, so it never
  reaches a reader to mislead them. - **Docs as code** puts documentation in
  the repository, in plain-text markup, under the same review and the same CI
  as the code.

For the harness this decides everything: it is how the documentation step
becomes checkable, and without it the step is an aspiration. Where a language
pack can run doctests, the `test` verb already covers documentation examples,
and documentation drift becomes a failing check instead of a judgement call.

## What the best examples do

Stripe is cited most often, and the lesson drawn is restraint: a three-column
layout with navigation, prose and a code sample that tracks the prose, and no
ornament. The code sample is the page's centre of gravity.

Twilio is the counter-example in the useful sense: its guides are organised
around things people want to do - "send messages", "record a call" - and never
around the API's own structure. The reader is always building something. This
is Diátaxis's how-to guide done at scale, and most repositories get it wrong by
documenting their modules when a reader arrives with a task.

Both share one property, stated here as a rule: **the documentation is
organised around what the reader wants, and never around how the software is
built.** A documentation tree mirroring the source tree is a reference index
pretending to be a guide.

## Conclusions

1. Name the kind before writing. Tutorial, how-to, reference or explanation
   - and never two in one document.
2. Take the Google/Microsoft intersection as the default style, with
   Microsoft's brevity rules as the editing pass: verbs first, no "there
   is/are", cut "you can", sentence case, serial comma.
3. Reasons live in explanation. A how-to guide that justifies itself is
   mixing kinds; the reason belongs in a linked explanation or a decision
   record.
4. Do not hand-write what the language generates. Reference for a public API
   comes from doc comments.
5. Prefer executable examples wherever the language supports them, so drift
   fails a check.
6. Organise around the reader's task, not the source tree.
7. A README is an inverted pyramid with a working quick start, and no
   promotional furniture.
8. `/meow:document` reports what it did not update and why, because the
   honest answer is often "nothing needed changing" and an unreported silence
   is indistinguishable from an omission.

## Sources

- [Diátaxis](https://diataxis.fr/), read 2026-09-20 - the four kinds, the two
  axes, and the rule against mixing forms. - [Google developer documentation
  style guide highlights](https://developers.google.com/style/highlights) and
  [Microsoft Writing Style
  Guide](https://learn.microsoft.com/en-us/style-guide/welcome/), read
  2026-09-20 - the intersection taken as the default style. - [RichardLitt/stan
  dard-readme](https://github.com/RichardLitt/standard-readme), read 2026-09-20
  - the closest thing to a README specification. - [GitHub README best
    practices in
    2026](https://pushpen.dev/blog/github-readme-best-practices-2026) and [README
    best practices](https://www.tilburgsciencehub.com/topics/collaborate-share/share-your-work/content-creation/readme-best-practices/), read 2026-09-20 - the
    inverted pyramid, accuracy and scannability, and the claim that currency is
    what differentiates a good README, where structure is not. The same sources
    supply the promotional advice this document rejects. - [Go Doc
    Comments](https://tip.golang.org/doc/comment), read 2026-09-20 - every
    exported name, complete sentences, the package-comment form, and
    `Deprecated:` as a machine-readable notice. - [Python
    `doctest`](https://docs.python.org/3/library/doctest.html), read 2026-09-20 -
    documentation examples executed as tests. - [Docs as
    Code](https://www.writethedocs.org/guide/docs-as-code/) and [Documentation
    principles](https://www.writethedocs.org/guide/writing/docs-principles/),
    Write the Docs, read 2026-09-20. - [Stripe & Twilio: achieving growth through
    documentation](https://devdocs.work/post/stripe-twilio-achieving-growth-through-cutting-edge-documentation) and [Twilio
    docs](https://www.twilio.com/docs), read 2026-09-20 - the three-column
    layout, and guides organised around tasks, where the API's structure
    organises nothing.
