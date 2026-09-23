---
id: TSK-1120
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3184, REQ-0999, REQ-1012, REQ-1013, REQ-1014, REQ-1024, REQ-1026]
issue: 49
---

# Review a text line by line, and report

One task, one branch, one pull request, one review.

## What to do

Write the agent definition `plugins/meow-prose/agents/prose.md`. It reads a
text line by line against the standard the skill states, when somebody asks
and at the review step, and it runs before the text is published (REQ-3184).
Start from the fourth text in the appendix of ADR-1010, the reviewer's draft.

The reviewer reports and never edits. A finding names the line, the rule, and
what the text would say instead, and the author decides. A reviewer that edits
silently leaves the author unable to tell a correction from a preference.

The reviewer never blocks. A long reading varies between runs, and a gate that
varies is a gate people route around.

A quotation is read and never judged, so its wording and its spelling survive
(REQ-0999). That covers a block quotation and a quoted string alike.

The reviewer reads comments in code as prose and holds them to five rules:

- A comment exists only where the code cannot explain itself (REQ-1012).
- Where a name can carry the meaning, the finding asks for a better name and
  not a comment (REQ-1013).
- A comment never restates what the code says (REQ-1014).
- Commented-out code does not survive a change (REQ-1024).
- A marker for later work carries an issue or a task (REQ-1026).

It recognises a comment without a language's grammar, which is why it reads
comments at all, since nothing in this layer names a language (REQ-0016). It
reads only the files a change touched, because on a source file it reads the
whole file to find a few lines of comment.

Measure the reviewer as a classifier, on a labelled set under
`plugins/meow-prose/evals/`: texts carrying named defects, which it must name
with their lines, and clean texts, which it must pass. Draw the defects from
the criteria table TSK-1110 publishes, with at least one case for every rule
and pattern a reader can see in a text, so the set tests the standard the
skill states and not a sample of it. Start the set from the examples the standard as it stands already carries,
in the appendix of ADR-1010: each rule's failing and corrected sentence, and
each pattern's failing and corrected text. A failing example is a labelled
defect and its correction is a labelled clean text, so every pair is two cases
somebody already argued for. Put quotations, code
comments and texts a reader would call a matter of taste among the clean ones,
because a finding on taste is how a reviewer loses the trust ADR-1010 says
would reverse the decision. Publish two rates: defects missed, and findings on
clean text.

Then improve the reviewer's prompt with the runner TSK-1170 builds, starting
from the appendix draft as the baseline. Each candidate changes one thing, and
a candidate lands when neither rate rises and the token cost does not rise. Publish
every candidate, including the ones that lost.

If the reviewer cannot run, the harness reports the review as unrun. A silent
skip is the substitution this harness exists to prevent.

## Depends on

TSK-1110, because the reviewer reads against the standard the skill states.
Carrying a second copy inside the agent is the drift ADR-1010 ends.

TSK-1170, because the reviewer's prompt is improved with the runner that task
builds.

## Evidence

In progress. The agent and its labelled set ship in the pull request for #49:
`plugins/meow-prose/agents/prose.md`, which preloads the writing skill and
carries no copy of the standard, and 52 cases under `plugins/meow-prose/evals/`.
Of those, 42 come from the failing and corrected pairs in `patterns/en.md`, 21
of each kind, and ten are written for this set, including the three below. The
runs wait for the measurement pass. The task closes on three runs of the
reviewer, each shown with its output:

- On a text carrying a bold fragment where a heading belongs, a counted opener
  and an over-long sentence, it names all three with their lines.
- On a text the standard is happy with, including a quotation in American
  spelling, it names nothing.
- On a source file carrying a comment that restates the line below it, it names
  that comment.

Each case is seen failing first against an empty agent (REQ-2072). The
labelled set's two rates follow for the baseline and for every candidate, with
the run count and the judge named.

## Left alone

The gate, which blocks and is a separate unit. This reviewer is the deep half
and blocks nothing.
