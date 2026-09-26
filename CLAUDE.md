# CLAUDE.md

<role>
The constitution for Claude Code working in the `meowpaw` repository. This file
is a living document and it's canonical. Anything under `.claude/` or
`plugins/` adds routing and workflow detail, and none of it overrides this
file. Where a document under `docs/` disagrees with this file, this file wins
and you fix the document.
</role>

<project>
`meowpaw` is a universal, specification-driven harness for Claude Code,
distributed as a plugin marketplace in four layers: a kernel, a method layer, a
practice layer, and packs for languages, task runners and external tools. The
catalogue isn't decided, so don't state one as a fact or count its entries.

This file carries the rules and never the state. What exists, what's approved,
what's in force and how many of each there are live in `project/README.md` and
the three indexes it links. They sit beside the artifacts they describe, and
the change that moves the work updates them. Read them for the state and don't
copy an answer back here, because a count written in this file is checked by
nothing and goes stale the same week.

The approved research is frozen, so a later finding becomes a new document
instead of an edit to an existing one. Earlier decision records and earlier
specification drafts were deleted rather than amended, and what gets written
next is derived from the requirements in force.
</project>

<layout>

Each document declares its lifetime in its front matter, so you can move a file
without changing what it is. `status: live` means you rewrite the document
freely. Everything else is a record: mutable while it's a draft, frozen on
approval.

One vocabulary, shared by every kind that has these statuses, so one act is
named by one word wherever it's recorded:

| Decided, and stored | Means                                                               |
| ------------------- | ------------------------------------------------------------------- |
| `draft`             | Being written. Editable                                             |
| `approved`          | Someone agreed. The record freezes                                  |
| `withdrawn`         | Retired, naming the decision that withdrew it                       |
| `rejected`          | Considered and not taken                                            |
| `superseded`        | Replaced by a named later record                                    |
| `live`              | A living document. The value never changes, and that's what it says |

| Observed, and derived | Means                                           |
| --------------------- | ----------------------------------------------- |
| `implemented`         | Every task realising it is closed with evidence |
| `verified`            | Its checks pass at the current revision         |
| `in-progress`         | Some of its work has landed and some hasn't     |
| `done`                | Implemented and verified                        |

The harness computes an observed status from the tree and never writes one into
a file. A decision record is `approved` when someone accepted it and
`implemented` when its epic closes, and only the first of those is stored.

| Path                                      | Holds                                                                                                              |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `CLAUDE.md`                               | This constitution. At the root because the platform loads it only from there                                       |
| `project/vision.md`                       | What this is, who it's for, what it won't do. Living                                                               |
| `project/specs/SPC-NNNN-<topic>.md`       | What the system must do now. One per part, plus the cross-cutting contracts. Living                                |
| `project/research/RES-NNNN-<topic>.md`    | What was read, with its sources                                                                                    |
| `project/requirements/REQ-NNNN-<slug>.md` | One obligation per file                                                                                            |
| `project/adrs/ADR-NNNN-<slug>.md`         | What was chosen, and what lost                                                                                     |
| `project/epics/EPC-NNNN-<slug>.md`        | One authorising record decomposed into tasks                                                                       |
| `project/tasks/TSK-NNNN-<slug>.md`        | One task, one branch, one pull request                                                                             |
| `project/bugs/BUG-NNNN-<slug>.md`         | Evidence that a requirement isn't met                                                                              |
| `docs/`                                   | Documentation for someone using the harness. A separate hierarchy                                                  |
| `plugins/<name>/`                         | One directory per plugin                                                                                           |
| `.claude-plugin/marketplace.json`         | The marketplace index                                                                                              |
| `mise.toml`                               | The gate, as tasks                                                                                                 |
| `.github/`                                | CI                                                                                                                 |
| `.meowpaw/profile.toml`                   | What this repository declares about itself: how its verbs resolve, where its artifacts live, which tracker it uses |
| `.meowpaw/templates/`                     | Any template this repository overrides. Empty or absent means the plugin's own                                     |

`.meowpaw/` belongs to the repository being worked in, and not to the harness.
The five verbs resolve from the profile, so it can't live in `.github/`: a
repository on `jj` with no forge still has to declare how you test it.

Configuration the harness owns is TOML, because a person reads the profile as
often as a program does and TOML has one way to write a table. Front matter
stays YAML, because the platform decided that and we didn't.

Templates ship inside the plugin that owns them and are read from
`${CLAUDE_PLUGIN_ROOT}`, so a repository gets them from the installed harness
and never from a copy that drifts. A repository that wants one changed puts its
own in `.meowpaw/templates/`, which overrides. The record's templates ship with
`meow-method`, and `meow-method template <kind>` prints the one in force.

One artifact per file, named for its identifier, in a directory named for its
kind. A directory appears when its first artifact does. A record is found by
what it says and by the identifiers it cites, never by the week somebody wrote
it, so nothing in a path or a field records when work happened.

</layout>

<principles>

<principle name="own_method_first">
The harness is developed by its own method, from the first artifact, and the
order isn't negotiable:

```text
research -> requirements -> design -> spec -> epic
         -> implement -> document -> verify -> review
```

A step whose input is missing or unapproved doesn't run. If you're about to
write a plugin and no approved specification covers it, stop and go back. The
whole claim of this project is that this order is cheaper, so a project that
exempts itself from its own method has disproved it before shipping.

Classify work before the chain starts. Trivial work - a typo, a formatting fix,
a link - skips it. That exemption is narrow on purpose: a method costing nine
steps for a one-line fix is one people route around, and then it reports a
process it never performed. Anything that changes behaviour isn't trivial.
</principle>

<principle name="living_and_record">
Three kinds of document are living: the vision, this constitution, and the
specifications. They describe the present, carry no history, and you rewrite
them freely.

Everything else is a record. You may edit a record while it's a draft, and it
freezes when someone approves it. After that, a later truth arrives as a new
record, you withdraw a requirement instead of rewording it, and a correction
goes through the amendment path with a tombstone naming the replacement. Never
reword an approved artifact in place to match what was built. That's the single
failure this method exists to prevent, and it stays invisible unless the
tombstone turns it into a diff.
</principle>

<principle name="grow_it_in_working_increments">
The design is a series of decisions ordered so the system works after each one.
The first decides the smallest thing that's a working harness, and every one
after it adds a layer without breaking what's already there.

A decision that needs a later decision to be usable is half a decision, so the
two belong in one record. A decision that adds a capability leaves the system
working when that capability is absent, which is what lets you remove the
increment again with the step that added it.

Each decision says what works once you accept it and what still doesn't.
Without that line, a reader can't tell an increment from a promise.
</principle>

<principle name="two_records_authorise_work">
Either somebody decided something, or something is broken. Every task traces to
a decision or to a defect, and if nothing authorises the work, write the
authorising record first. The method keeps no taxonomy of work types, because
the harness can derive the type and a list somebody maintains is a boundary
argument that never ends.
</principle>

<principle name="research_is_evidence">
A claim in a requirement or a specification points at where it was recorded in
`project/research/`. "Most harnesses do X" is a claim, so it needs a source.
Adding a finding to the research after the fact is correct and expected;
asserting one without adding it isn't.
</principle>

<principle name="relations_are_authored_upward">
A document names what it came from, as a bare identifier in its front matter
and never as a Markdown link. Tooling derives the reverse direction. Research
cites no requirement, and a requirement lists none of the tasks that close it,
because a record written earlier can't be kept current by a record written
later.
</principle>

<principle name="requirements_are_identified">
Every obligation carries `REQ-NNNN`, allocated once, never reused and never
renumbered. Identifiers are allocated in blocks per topic, with gaps, so a
statement written later joins its neighbours and doesn't land at the end.
</principle>

<principle name="the_method_names_no_language">
No prompt, template or page in the kernel, method or practice layers names a
language, a build tool, a package manager or a source file extension, because
what the harness tells a repository has to hold in every language. Language
knowledge lives in packs. A unit's own program is written in some language and
the rule doesn't reach its source: it governs what the harness says, not what
it is built with (ADR-1070). No check enforces the rule yet, so review holds
it, which is weaker, and this sentence says so instead of leaving you to
assume otherwise.
</principle>

<principle name="unresolved_is_not_a_pass">
A verification verb that resolves to no command is reported as unresolved and
never as passed, and you never guess a command. Implementation violates this
one more often than any other requirement, because guessing looks helpful. It
isn't: it produces a green report with nothing behind it.
</principle>

<principle name="evidence_or_it_did_not_happen">
A claim that something works cites the command, its exit status and its output.
Prose asserting success is no evidence. Evidence collected before an edit
doesn't survive the edit.
</principle>

<principle name="artifacts_stay_current">
Keeping the artifacts true is part of the work, and never a tidying pass after
it.

- Mark a task complete in the commit that completes it, with the evidence and
  the requirement identifiers it closed. Never in a later pass.
- Move a requirement's status in the change that moves the requirement, and
  name the checks that cover it once it's implemented.
- When work shows an artifact is wrong, fix the artifact. Fixing only the code
  leaves the work incomplete.
- Keep a dropped task with the reason you dropped it, and mark a task added
  after approval as added, with why nobody foresaw it. Deleting the entry loses
  the only record that anyone considered the question.

An artifact that has drifted from the tree is worse than a missing one, because
people go on citing it.
</principle>

<principle name="a_gate_is_a_stop">
Where a step ends in human approval, produce the artifact, report, and end the
turn. Don't ask a question and then continue on your own answer. Don't treat
silence or a change of subject as approval.
</principle>

<principle name="report_the_next_action_first">
The shape of a report is a mechanism and not a preference: the work can be
honest while the report still hides the one thing that mattered.

This applies to every reply, unconditionally. It's not a mode, you don't opt
into it, and no plugin, skill or step is exempt, because a rule that only some
replies follow shapes nothing.

- Lead with the command, the path and the line. Prose after, if at all.
- Compute progress from the artifacts instead of recalling it: which step of
  how many, what's pending, what's unresolved.
- Report a failure as cause, location and fix, with no drama in front of it.
- Where a step stops, name the command that resumes it.
- No preamble announcing what you're about to do, no recap of what you just
  did, no closing offer of further help.

**Completeness outranks brevity.** Brevity is the default and it's
presentation. Drop no verb from a verification report, no finding from a
review, no question from a gap list, and no hedge that carries real
uncertainty, because deleting the last of those manufactures confidence. Where
a rule of shape would delete part of an answer, the answer wins and the shape
yields.

Check before sending: reading only the first line and the last line, does the
reader know what to do next and what just happened?
</principle>

<principle name="always_technical_english">
All prose in this repository is held to the writing standard `meow-prose`
ships, installed from this marketplace, and in its default language, British
English. The rules and their reasons live in its skill, and this file doesn't
repeat them, because a second copy drifts from the first. This governs
documents, specifications, code comments, commit messages, pull request bodies
and your replies. A commit message is prose and a reply is prose.

Apply the standard while you write, not afterwards. Before a document, name
the two or three rules its type breaks most often, and re-read each paragraph
before you write the next one. A sentence comes out shaped like whatever you
have been reading, so a day spent in specifications produces specifications,
and the rules only join in when you stop to look.

The review before publishing, by `meow-prose:prose`, catches what survived
that. It is not where the work happens, and a review finding six defects in
five short texts is your work handed to the next step.

Check the text before it leaves your hands, not after somebody reads it.
Every document, every commit message, every issue you file and every pull
request body goes through the standard while it is still an edit. A defect caught here costs one edit. The same
defect caught after the merge costs an issue, a defect record and a change to
correct it, and this repository has paid that several times.

The test: a rule whose reason is stated survives contact with a case its author
never foresaw, because the reader can tell whether the reason applies. A rule
without one gets applied literally and wrongly.
</principle>

<principle name="comments_by_exception">
Code and prompt files carry the licence header below, and everything publicly
reachable carries documentation.

```text
SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
SPDX-License-Identifier: Apache-2.0
```

`REUSE.toml` declares the document corpus in bulk. A requirement is fifteen
lines, so a per-file header would take a seventh of the document and meet the
reader first in every one of a thousand of them. Write any other comment only
where the code can't be made to explain itself. Remove a comment that restates
the line below it, because it turns wrong the first time that line changes.
</principle>

<principle name="reviewable_history">
`main` is the only long-lived branch, and nobody commits to it directly, not
even for a one-line fix. Work on `<type>/<slug>`, open a pull request, squash
merge. Conventional commit subjects, kept short.

The type says what the change means for a release:

| Type    | Means                                                                                                                         | Release                            |
| ------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `feat`  | The harness gained a capability                                                                                               | minor                              |
| `fix`   | A defect was corrected, in code or in an artifact                                                                             | patch                              |
| `spec`  | A project artifact was written or changed: research, requirements, decisions, the vision, the constitution, the specification | none until something implements it |
| `docs`  | Documentation for people using the harness                                                                                    | none                               |
| `chore` | Tooling, gates and repository plumbing                                                                                        | none                               |

`spec` isn't in the conventional set, and this file declares it on purpose:
this repository's artifacts are normative, and calling them `docs` would put
the specification and the README in one bucket.

Every commit you write on a branch is cryptographically signed, and
`.github/allowed_signers` names the key that verifies it:

```bash
git log --show-signature -1     # the signature verifies against the named key
```

GitHub rebuilds the commit when it squashes a pull request, so the one that
lands on `main` carries GitHub's own key and not yours. That's accepted: the
branch commits it was built from verify against the named key, and they're what
review read.

Before a message is used, `meow-scm check-message` checks it against the
convention `.meowpaw/profile.toml` declares and against the attribution ban
below, and a message it fails isn't used.

Every commit also carries the author's sign-off:

```text
Signed-off-by: Andrew Vasilyev <me@retran.me>
```

A sign-off says who claims the work and a signature says the claim wasn't
forged, so the two are different obligations and not one stated twice. The
sign-off is also the opposite of the attribution ban below: that ban stops the
harness naming itself, the agent or the vendor.

The reason for all of this is review: a change that never appeared as a diff
was never reviewable, and an agent's change least of all. Squashing keeps one
commit per unit of work, so the history reads as decisions and not as a
transcript of how the work went.
</principle>

<principle name="no_ai_attribution">
Never mention Claude, Claude Code, or any AI tool in a commit message, a pull
request title or body, a review comment, an issue, a tag annotation, or release
notes. No `Co-Authored-By` trailer naming an AI, no "Generated with" footer, no
`noreply@anthropic.com`, and no paraphrase. This overrides the default harness
guidance that asks for such a trailer.

Check your own message before committing. Match the attribution patterns and
not the bare word, so a path such as `plugins/meow-core/` doesn't trip it:

```bash
git log -1 --format=%B |
  grep -iE 'co-authored-by.*(claude|anthropic|copilot)|generated with|noreply@anthropic'
```

You can write "Claude" where it names the product the harness targets. That's a
technical fact about the system and not attribution.
</principle>

<principle name="never_touch_secrets">
Never read, print or transmit a repository's secret material, and never place
it in an artifact. A tool that packs a repository for a model is the likeliest
way somebody breaks this by accident.
</principle>

</principles>

<gate>

Run the gate before opening a pull request, and report what it actually said:

```bash
mise run all          # fmt-check, lint, style, prompts, kernel and budget
```

| Check       | Fails when                                                      |
| ----------- | --------------------------------------------------------------- |
| `fmt-check` | Markdown isn't in canonical form                                |
| `lint`      | Markdown breaks a rule in `.markdownlint-cli2.yaml`             |
| `style`     | An output style breaks the shape SPC-1000 states                |
| `prompts`   | A shipped prompt uses a heading or a tag outside the vocabulary |
| `kernel`    | A file in the kernel names a unit outside it                    |
| `budget`    | A unit loads more on every turn than its `budget.toml` states   |

The record is checked by `meow-method`, a unit the harness ships, because a
harness checked by a mechanism it doesn't ship hasn't been shown to work. It
checks front matter, identifiers, relations, each kind's index, coverage and
shape, where `.meowpaw/profile.toml` declares the record:

```bash
plugins/meow-method/bin/meow-method check
```

Three checks stay in `tools/` as Python scripts, because they read this
repository and not the record: the documentation index, links, and the shape a
subordinate agent carries. The `test` verb runs all four, and so does
`meow-verbs run test`.

A check that reports a false positive is a defect in the check, and never a
reason to reword the text around it. A check that trips on what it shouldn't
gets switched off within a week, and then it catches nothing.

</gate>

<maintenance>

Keep this file and the documentation saying what's true. When you change:

- **a requirement** - allocate a new identifier, tombstone the old one, and
  check the specification that cites it
- **the layering model, the verb contract or the step chain** - write the
  decision first, then the specification, then anything that cites it
- **the plugin list** - update the specification that states it, and name the
  plugins in one place so that nothing has to be counted twice
- **a research finding** - add it to the right file under `project/research/`,
  index it in `RES-0001-synthesis.md`, and cite it from whatever now depends on
  it

This is the only instruction file in the repository. If a tool wants its own,
point it here instead of adding a second source of truth.

</maintenance>
