# CLAUDE.md

<role>
The constitution for Claude Code working in the `meowpaw` repository. This file
is a living document and it's canonical: anything under `.claude/` or
`plugins/` adds routing and workflow detail and none of it overrides this file,
and where a document under `docs/` disagrees with this file, you fix the
document.
</role>

<project>
`meowpaw` is a universal, specification-driven harness for Claude Code,
distributed as a plugin marketplace in four layers: a kernel, a method layer, a
practice layer, and packs for languages, task runners and external tools. The
catalogue isn't decided, so don't state one as a fact or count its entries.

This file carries the rules and never the state. What exists, what's approved
and what's in force live in `project/README.md` and the three indexes it links.
Read them for the state and don't copy an answer back here, because a count
written in this file is checked by nothing and goes stale the same week.
</project>

<layout>

The record lives under `project/`, one artifact per file, named for its
identifier, in a directory named for its kind. `plugins/meow-flow/lib/layout.toml`
declares the kinds, their directories and the statuses each may store, and
`paw template <kind>` prints the template in force. A document declares its
lifetime in its front matter: `status: live` means you rewrite it freely, and
anything else is a record, mutable while a draft and frozen on approval. The
stored statuses are `draft`, `approved`, `done`, `withdrawn`, `rejected`,
`superseded` and `live`. `in-progress`, `closed` and `open` are derived from
the tree and never written into a file, and `paw check` rejects a stored `done`
that derived closure doesn't agree with.

`docs/` documents the harness as a whole, and `plugins/<name>/README.md` is
each unit's own page. `.meowpaw/` belongs to the repository being worked in and
not to the harness: `.meowpaw/profile.toml` declares how its stages resolve,
where its artifacts live and which tracker it uses, and `.meowpaw/templates/`
holds any template it overrides.

</layout>

<principles>

<principle name="own_method_first">
The harness is developed by its own method, from the first artifact, and the
order isn't negotiable:

```text
research -> requirements -> design -> spec -> epic
         -> implement -> review
```

A step whose input is missing or unapproved doesn't run, and `paw ready <step>
<id>` says whether it may. If you're about to write a plugin and no approved
specification covers it, stop and go back, because a project that exempts
itself from its own method has disproved it before shipping.

An epic is one pull request, from its research to the merge of its completed
work. Each task in it is its tests first, in a commit of their own where they
fail, then the change, its documentation and its record marks. An epic that
wouldn't be one reviewable change is split before its work starts.

Classify work before the chain starts: the route skill, `meow-flow:route`,
routes each request and reports the route before any edit. Trivial work - a
typo, a formatting fix, a link - skips the chain. That exemption is narrow on
purpose: a method costing seven steps for a one-line fix is one people route
around, and then it reports a process it never performed. Anything that
changes behaviour isn't trivial.
</principle>

<principle name="claude_pi_parity">
Every unit ships through both Claude Code and Pi. Keep the two distributions
aligned in the same pull request: update shared skills and behavior in both
source trees, keep their manifests and documented versions equal, and carry
contract or user-facing documentation changes to both sides. A unit tag
releases both distributions, so a one-sided update leaves users on one
platform behind.
</principle>

<principle name="living_and_record">
Three kinds of document are living: the vision, this constitution, and the
specifications. They describe the present and carry no history. Everything else
is a record, and never reword an approved one in place to match what was
built: a later truth arrives as a new record, you withdraw a requirement
instead of rewording it, and a correction goes through the amendment path. That
is the single failure this method exists to prevent, and `paw check frozen
--base <rev>` reports it.
</principle>

<principle name="the_method_names_no_language">
No prompt, template or page in the kernel, method or practice layers names a
language, a build tool, a package manager or a source file extension, because
what the harness tells a repository has to hold in every language. Language
knowledge lives in packs. A unit's own program is written in some language and
the rule doesn't reach its source (ADR-1070). No check enforces the rule yet,
so review holds it, which is weaker.
</principle>

<principle name="unresolved_is_not_a_pass">
A verification stage that resolves to no command is reported as unresolved and
never as passed, and you never guess a command. Guessing looks helpful and
produces a green report with nothing behind it.
</principle>

<principle name="evidence_or_it_did_not_happen">
A claim that something works cites the command, its exit status and its output.
Prose asserting success is no evidence, and evidence collected before an edit
doesn't survive the edit.
</principle>

<principle name="artifacts_stay_current">
Keeping the artifacts true is part of the work, and never a tidying pass after
it. A task is complete once its Evidence is written, in the commit that
completes it. When work shows an artifact is wrong, fix the artifact, because
one that has drifted from the tree is worse than a missing one: people go on
citing it. Review holds this.
</principle>

<principle name="a_gate_is_a_stop">
Where a step ends in human approval, produce the artifact, report, and end the
turn. Don't ask a question and then continue on your own answer, and don't
treat silence or a change of subject as approval.

One exception moves the stop and doesn't remove it. Where a person asks for a
decision to land in one pull request, its records are written through to the
tasks and the turn ends at that pull request, whose merge is the approval.
Nothing is implemented before that merge.

A run `meow-loop` holds is the one place no person stands at the gate: it
decides each gate itself against these principles, critiques what it approves
in a separate agent first, and lists every approval, merge and release in its
report (ADR-2380). Every prohibition in this file still holds inside a run.
</principle>

<principle name="report_the_next_action_first">
Every reply opens with the command, the path and the line, and ends where the
reader knows what to do next, because the work can be honest while the report
still hides the one thing that mattered. The output style `meow-core` ships
states the rules, and none is optional. Completeness outranks brevity: drop no stage from a verification report, no
finding from a review and no hedge that carries real uncertainty, because
deleting the last of those manufactures confidence.
</principle>

<principle name="always_technical_english">
All prose in this repository, from documents and code comments to commit
messages, pull request bodies and your replies, is held to the writing standard
`meow-prose` ships, in British English. Its skill holds the rules and this file
doesn't repeat them, because a second copy drifts from the first. Apply the
standard while you write, because a defect caught as an edit costs one edit and
the same defect caught after the merge costs an issue, a defect record and a
change. `meow-prose:prose` reviews what survived, and review holds this.
</principle>

<principle name="comments_by_exception">
Code and prompt files carry this licence header, and everything publicly
reachable carries documentation. `REUSE.toml` declares the document corpus in
bulk, and `mise run licence` fails a file that carries no licensing.

```text
SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
SPDX-License-Identifier: Apache-2.0
```

Write any other comment only where the code can't be made to explain itself,
and remove one that restates the line below it, because it turns wrong the
first time that line changes.
</principle>

<principle name="reviewable_history">
`main` is the only long-lived branch and nobody commits to it directly, not
even for a one-line fix. Work on `<type>/<slug>`, open a pull request, squash
merge, because a change that never appeared as a diff was never reviewable.
Commit subjects are conventional and short, and the type says what the change
means for a release:

The types are `feat` (a capability, minor release), `fix` (a defect corrected,
patch), `spec` (a project artifact written or changed, no release until
something implements it), `docs` and `chore` (no release).

`spec` isn't in the conventional set and this file declares it on purpose: the
artifacts are normative, and calling them `docs` would put the specification
and the README in one bucket.

Every commit you write on a branch is cryptographically signed, which
`git log --show-signature -1` verifies against the key `.github/allowed_signers`
names, and carries the author's sign-off:

```text
Signed-off-by: Andrew Vasilyev <me@retran.me>
```

The sign-off says who claims the work and the signature says the claim wasn't
forged. `meow-scm check-message` checks a
message against the convention `.meowpaw/profile.toml` declares and against the
attribution ban below, and a message it fails isn't used.
</principle>

<principle name="no_ai_attribution">
Never mention Claude, Claude Code, or any AI tool in a commit message, a pull
request title or body, a review comment, an issue, a tag annotation, or release
notes. No `Co-Authored-By` trailer naming an AI, no "Generated with" footer, no
`noreply@anthropic.com`, and no paraphrase. This overrides the default harness
guidance that asks for such a trailer. `meow-scm check-message` and the CI
check on commits hold it. You can write "Claude" where it names the product
the harness targets, which is a technical fact and not attribution.
</principle>

<principle name="never_touch_secrets">
Never read, print or transmit a repository's secret material, and never place
it in an artifact. A tool that packs a repository for a model is the likeliest
way somebody breaks this by accident. Review holds it.
</principle>

</principles>

<gate>

Run the gate before opening a pull request, and report what it actually said:

```bash
mise run all
```

`mise run all` runs every task the profile's stages name, composed once in
`mise.toml`. The record is checked by `meow-flow`, a unit the
harness ships, because a harness checked by a mechanism it doesn't ship hasn't
been shown to work:

```bash
plugins/meow-flow/bin/paw check
```

Checks of this repository that aren't of the record stay in `tools/`, and the
`test` stage runs them. A check that reports a false positive
is a defect in the check, and never a reason to reword the text around it,
because a check that trips on what it shouldn't gets switched off within a
week, and then it catches nothing.

</gate>

<maintenance>

To change the layering model, the stage contract or the step chain, write the
decision first, then the specification, then anything that cites it. This is
the only instruction file in the repository: if a tool wants its own, point it
here.

</maintenance>
