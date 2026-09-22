---
id: SPC-1010
artifact: spec
status: live
revised: 2026-09-22
checked-at:
states:
  [
    REQ-0990,
    REQ-0991,
    REQ-0992,
    REQ-0993,
    REQ-0994,
    REQ-0995,
    REQ-0996,
    REQ-0997,
    REQ-0998,
    REQ-0999,
    REQ-1000,
    REQ-1002,
    REQ-1671,
    REQ-1674,
    REQ-1676,
    REQ-3182,
    REQ-3184,
    REQ-3186,
    REQ-3188,
    REQ-1012,
    REQ-1013,
    REQ-1014,
    REQ-1024,
    REQ-1026,
  ]
---

# The writing standard

## Scope

Two units are what this covers. `meow-prose` carries the skill stating the
writing standard and the reviewer that reads a finished text; `meow-prose-gate`
carries the hook that blocks a publish. It also covers the way a repository
replaces the standard, and what each unit costs in context.

It leaves licence headers to REQ-1008 and REQ-1016 to REQ-1022, which ask
whether a header of a declared form is present, and it leaves the shape of a
reply to SPC-1000.

The harness does not implement this yet. ADR-1010 authorises it, ADR-1020 and
ADR-1030 amend it, EPC-1010 and EPC-1020 realise them, and `checked-at` stays
empty until both epics close.

## Boundary

Two units ship, and either installs without the other (REQ-0012, REQ-0076).

| Surface                                    | What it is                                                         |
| ------------------------------------------ | ------------------------------------------------------------------ |
| `plugins/meow-prose/skills/writing/`       | The standard, loaded before anything is written                    |
| `plugins/meow-prose/agents/prose.md`       | The deep reviewer, dispatched on request and at the review step    |
| `plugins/meow-prose/hooks/hooks.json`      | A `SessionStart` command hook naming the skill and when to load it |
| `plugins/meow-prose-gate/hooks/hooks.json` | A `PreToolUse` prompt hook that blocks a publish                   |
| `.meowpaw/prose/`                          | A repository's replacement standard, which is total                |

Installing either unit adds no task to a repository's runner, writes nothing
into its tree and changes no build.

## Behaviour

### The standard

The harness holds one writing standard over everything it produces, including
artifacts, code comments, commit messages and replies (REQ-0990). The skill
carrying it loads before anything is written (REQ-0992), because a standard
applied afterwards is a rewrite and gets skipped when time is short.

It is British English (REQ-0995), one language per repository and declarable
there (REQ-0996), and a technical term keeps the spelling its own domain uses
(REQ-0997). Every rule it states carries its reason (REQ-0994). A draft
declares the reader it is written for (REQ-0993), and a sentence names the
actor and uses the verb (REQ-0991).

The standard covers the shape of a document as well as its sentences: which
sections a document type carries, and in what order (REQ-0998).

Prose carries its content in the fewest tokens the content allows, and loses no
content to get shorter (REQ-3188). What goes is the frame announcing a claim,
the sentence restating its neighbour, the paragraph introducing the next one,
and the hedge with nothing under it.

### The deep reviewer

An agent in `meow-prose` reads a text line by line when somebody asks and at
the review step (REQ-3184). It reports and never edits: a finding names the
line, the rule and what the text would say instead, and the author decides. A
reviewer editing silently leaves that author unable to tell a correction from a
preference.

It never blocks. A long reading varies between runs, and a gate that varies is
a gate people route around.

Quotations are read and never judged, so the wording and the spelling their
author used survive (REQ-0999).

### The gate, installed separately

`meow-prose-gate` is a unit of its own, so a repository takes the standard
without the gate, the gate without the standard, or both (REQ-0012). It
requires neither the skill nor the agent, which REQ-0076 forbids a separately
installable unit from doing, so it carries its own criteria in its own prompt.

Its `PreToolUse` hook of type `prompt` reads a text before it is published, and
publishing covers a commit, an issue, a pull request body, a review comment and
a release note (REQ-3182). The hook names Haiku in its `model` field and blocks
by answering `ok: false` with a reason that names the rule. It sets
`continueOnBlock: true`, so the reason reaches the model as the tool error and
the model corrects the text and publishes again.

It judges only what a reader names without weighing taste: an idiom, an
unexplained acronym, an American spelling outside a technical term, a bold
fragment standing in for a heading. Narrow criteria are what make a model
verdict fit to block on, and they stay inside what a small model settles
reliably.

The hook reads the call's input and opens no file, so it denies a publish that
hides its text behind a path: `git commit -F`, `--body-file`, or a substitution
such as `$(cat notes.md)`, which the hook sees before the shell expands it. The
denial names the form to use instead. A text the gate cannot read is not
published.

### Loading the standard

The skill has to be in context before a text is written, and the model's own
choice loaded it in one run of nine. `meow-prose` therefore ships a
`SessionStart` command hook that returns one line of `additionalContext`,
naming the skill and the work it governs, on every new, resumed, cleared and
compacted session (REQ-1140). The line costs under 300 characters, and the hook
reads nothing and writes nothing.

How often the skill is in context when a writing request arrives is measured on
both models, with the hook and without it.

### Comments in code

A comment is prose, so the standard holds it (REQ-0990) and the reviewer reads
it. Finding a comment with a pattern would mean knowing the language's grammar,
which nothing carrying this method names (REQ-0016), and a model recognises one
without that grammar.

A comment exists only where the code cannot explain itself (REQ-1012), and the
name is improved before a comment is added (REQ-1013). A comment is short and
plain, one line where one line will do, and says why the code does what it
does. A comment never restates
what the code says (REQ-1014). Commented-out code does not survive a change
(REQ-1024), and a marker for later work carries an issue or a task (REQ-1026).

On a source file the reviewer reads the whole file to find a few lines of
comment, so it runs on the files a change touched.

### Why no pattern holds it

No pattern over the text enforces the standard (REQ-3186). A pattern reads
words, and the defects that reach a branch are shape. A bold fragment stands in
for a heading. An opener announces how many items follow. A claim reads as a
proverb with its reason missing.

`prettier` and a Markdown linter stay. They read syntax, which settles nothing
the standard is about.

### Replacing the standard

A repository writes its own standard in `.meowpaw/prose/`, and the replacement
is total (REQ-1000, REQ-1002). The two are never merged, because two standards
disagreeing in one repository leave an author no way to tell which applies.

### What the unit owes itself

The unit's own material is the first text its reviewer reads. The skill, the
reviewer's own prompt and the documentation page are held to the standard they
carry (REQ-1674, REQ-1676), and a finding in them counts as readily
as a finding anywhere else.

### How the prompts are written

Every prompt either unit ships follows SPC-1030: its form, its content, how it
is divided and loaded, and what it costs.

### Changing any of it

A change to this standard, or to any prompt the harness ships, is measured
against what it replaces. SPC-1020 states how: the case set, the two arms, the
thresholds, the judge, and what counts as a regression.

## Failure paths

| Condition                                        | What happens                                                                                       |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| The reviewer is unavailable                      | The harness reports the review as unrun, and a person decides whether to publish                   |
| The hook exceeds its timeout                     | It stops blocking, so the unit states the timeout it set and a long text is reviewed by hand       |
| The hook blocks on taste                         | The criteria are the defect, and they are narrowed rather than the text being rewritten            |
| The reviewer's finding is disputed               | The author decides, because the reviewer reports and never edits                                   |
| The reviewer reports a preference                | The reviewer's own prompt is the defect, and the text it flagged is not rewritten to satisfy it    |
| A repository declares a replacement standard     | The shipped standard is not loaded, and the replacement's own reviewer runs                        |
| A unit exceeds its stated budget                 | The overrun is reported as a defect, and the unit is not left over budget                          |
| A text is published with no review               | The omission is reported, because a silent skip is the substitution this harness exists to prevent |
| The reviewer passes a text a reader later faults | The finding goes against the reviewer's own prompt, which is the thing that changes                |
