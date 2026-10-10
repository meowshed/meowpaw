---
id: SPC-1010
artifact: spec
status: live
revised: 2026-10-03
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
    REQ-3183,
    REQ-3184,
    REQ-3740,
    REQ-3742,
    REQ-3744,
    REQ-3746,
    REQ-3748,
    REQ-3750,
    REQ-3752,
    REQ-3188,
    REQ-1012,
    REQ-1013,
    REQ-1014,
    REQ-1024,
    REQ-1026,
    REQ-1426,
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

The harness does not implement this yet. ADR-1010 authorises it, ADR-1020,
ADR-1030, ADR-1050, ADR-1600 and ADR-2390 amend it, EPC-1010 and EPC-1020 realise them.
ADR-2700 names the gate's judge as the one hook call that reaches the network
and waits on a model, and ADR-2710 decides that a missing binary denies the
publish.

## Boundary

Two units ship, and either installs without the other (REQ-0012, REQ-0076).

| Surface                                    | What it is                                                      |
| ------------------------------------------ | --------------------------------------------------------------- |
| `plugins/meow-prose/skills/writing/`       | The standard, loaded before anything is written                 |
| `plugins/meow-prose/agents/prose.md`       | The deep reviewer, dispatched on request and at the review step |
| `plugins/meow-prose-gate/hooks/hooks.json` | A `PreToolUse` command hook that blocks a publish               |
| `.meowpaw/prose/`                          | A repository's replacement standard, which is total             |

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
actor and uses the stage (REQ-0991).

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
installable unit from doing, so it carries its own criteria in its own
program.

Its `PreToolUse` hook of type `command` runs `meow-prose-gate check` before a
text is published, and publishing covers a commit, an issue, a pull request
body, a review comment and a release note (REQ-3182). The program reads the
shell command from the hook's input. It finds
each `git commit` and each `gh` command in the command, including one with a
global option before its subcommand, such as `git -C dir commit` or
`gh -R owner/repo pr create`, and the hook routes both, as it does
`git -c`. It takes the text
from the arguments of `-m`, `--message`, `--title`, `--body` and `--notes`,
their short forms for that tool, and each heredoc.

It checks three rules, each of which names its defect exactly, so a program
settles it the same way every time, and no model is called for them
(REQ-3740):

- P1, a phrase from a closed list of fifteen idioms, matched
  case-insensitively as whole words with any spaces, line breaks or hyphens
  between its words.
- P2, a line holding only bold text, such as `**Why.**`, with an optional
  colon or full stop after it.
- P3, a text hidden behind a path the hook can't read: the value of `-F`,
  `--file`, `--body-file` or `--notes-file` other than `-`, `/dev/stdin` or
  `/dev/fd/0`, which each name standard input, or a substitution
  such as `$(cat notes.md)` or `$(< notes.md)`, which the hook sees before the
  shell expands it. `-F -` with a heredoc and `$(cat <<'EOF' ... EOF)` are
  readable and pass.

P1 and P2 skip fenced code, code spans and URLs. On a finding the program
exits 2 and prints one line per finding to standard error as
`P1 | "span" | fix`, where the span is the text it matched, verbatim from the
command (REQ-3183), and the fix names what to write instead. Claude Code hands
the lines to the model as the reason, and the model corrects the text and
publishes again. On no finding it exits 0 and prints nothing.

Where the unit carries no binary for the machine, its launcher denies the
publish with exit 2, and its reason names `meow-prose-gate`, the machine's
target and the command that installs the unit again, as SPC-1240 states for
every hook (REQ-1426).

With no finding on P1, P2 or P3, the program asks a judge twice, in two calls
started side by side, whether the text breaks a judged rule. The judged rules
are a closed list, and a rule joins or leaves it only by a decision of its own
(REQ-3742):

- J1, an idiom, saying or culture reference that P1's list doesn't spell,
  outside code font, URLs and identifiers.
- J2, an acronym used before it is expanded, or never expanded, outside code
  font, URLs, identifiers and a commit subject's type and scope.
- J3, a paragraph or list item opening with a bold phrase that goes on in the
  same line, outside code font and fenced code.

A judgement is one run of `claude -p` in safe mode with no tool, no session
saved, one turn, the `sonnet` model and a JSON schema whose `rule` field
allows only `J1`, `J2` and `J3`, so the judge loads no hook, plugin, skill,
MCP server or project instruction (REQ-3750). The text reaches the judge as
data inside a tag. Where `MEOW_PROSE_GATE_JUDGE` is set, the program runs that
command in its place, which only the unit's fixtures do.

The program keeps a judged finding only where its span is a slice of the text
it read from the command, and occurs there at least once outside the code,
URLs and identifiers P1 skips (REQ-3746, REQ-3183). It blocks only on a finding
whose rule and span both judgements report (REQ-3744). It prints those as
`J1 | "span" | fix`, as it prints the exact rules' findings.

Where either judgement can't be made, because `claude` isn't on the path, a
call exits non-zero, a call runs past 45 seconds or a reply is outside the
schema, the program exits 0 and prints
`{"systemMessage": "meow-prose-gate: the judged rules were not checked: <cause>"}`,
so the person sees that only the exact rules ran (REQ-3748). A call that
exits non-zero adds the last line the judge wrote on standard error to the
cause. The 45 seconds bound the whole call, writing the prompt included, and
at the limit the program kills the judge's process group, so a child the judge
left running can't hold the gate. Each hook's timeout is 120 seconds, so the
judge's limit fires first.

The judge is the one call any hook the harness ships makes to the network,
and the one wait longer than a hook's small fixed work. SPC-1240 names it as
the exception to REQ-2727 and REQ-2716, and `meow-author check` accepts it by
unit and subcommand only (ADR-2700).

Before a release ships a judged rule, a run by hand shows BUG-1230's four texts
passing and one text per judged rule blocked, each in three runs of three, and
no workflow runs it (REQ-3752). An American spelling, and every rule of the
standard outside P1 to P3 and J1 to J3, stay with the skill and the reviewer.

### Loading the standard

The skill has to be in context before a text is written, and its description
is what loads it. The description states the obligation in the form SPC-1030
gives, and names the stages a writing request uses, so Sonnet 5 loads the skill
on a one-line commit message as well as on a document. `meow-prose` ships no
hook for loading, because a `SessionStart` line naming the skill did not
change what the model did.

How often the skill is in context when a writing request arrives is measured on
both models, beside near misses that should not load it (REQ-1150).

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

No pattern that guesses at meaning enforces the standard (REQ-3740). A pattern
reads words, and the defects that reach a branch are shape. A paragraph opens
with a bold verdict. An opener announces how many items follow. A claim reads as a
proverb with its reason missing. The gate's three exact rules are the
exception, because each names its defect exactly and asks for no guess, and
its judged rules are held by a model whose finding a program confirms.

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

| Condition                                        | What happens                                                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| The reviewer is unavailable                      | The harness reports the review as unrun, and a person decides whether to publish                              |
| The gate's binary is missing for the machine     | The launcher reports nothing checked and lets the publish through, and the reviewer still runs                |
| The gate blocks a text that carries no defect    | The program's reading is the defect, and it is fixed with a fixture rather than the text rewritten            |
| The gate's judge can't run or answer             | The gate checks only P1 to P3, lets the publish through and tells the person the judged rules weren't checked |
| Both judgements agree on a finding that is wrong | The judge's prompt is the defect, and a defect record names the text and the finding                          |
| The reviewer's finding is disputed               | The author decides, because the reviewer reports and never edits                                              |
| The reviewer reports a preference                | The reviewer's own prompt is the defect, and the text it flagged is not rewritten to satisfy it               |
| A repository declares a replacement standard     | The shipped standard is not loaded, and the replacement's own reviewer runs                                   |
| A unit exceeds its stated budget                 | The overrun is reported as a defect, and the unit is not left over budget                                     |
| A text is published with no review               | The omission is reported, because a silent skip is the substitution this harness exists to prevent            |
| The reviewer passes a text a reader later faults | The finding goes against the reviewer's own prompt, which is the thing that changes                           |
