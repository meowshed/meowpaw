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

The agent and its labelled set shipped in #92. The set holds 52 cases: 42 from
the failing and corrected pairs in `patterns/en.md` and ten written for it,
each tagged `defect` or `clean`. `tools/loop.py --mode classifier`, three runs
per case, judged by Opus 5.5, so every judged score is a smoke check
(REQ-3028).

The first runs measured the eval's sandbox and not the reviewer. It refused
the reviewer's reads of its own `patterns/en.md` and `documents.md`, so the
reviewer reported every review as unrun, as its setup step says. `tools/loop.py`
now grants each unit `Read` on its own directory (#98). The next run read the
files and showed three faults in the set, which were corrected before any
candidate was judged:

- Three clean texts I wrote broke the standard: an acronym never expanded
  (H6), times with no time zone (H7), "I" switching to "us" (B1), two words for
  one action (T4) and a sum of minutes that didn't add up. The reviewer named
  each of them.
- The corrected example "deterministic, sandboxed and bounded" broke F6 as it
  then read. F6 asked for the serial comma, and nothing else the standard
  ships used it, so the owner changed F6 to leave it out, as British English
  does.
- The 42 pattern cases are excerpts, and reviewed as whole texts they have
  references the surrounding document would define. Each now says it is an
  excerpt.

On the corrected set, Sonnet 5:

| Candidate | Change                                                           | Defects named | Clean passed | Verdict             |
| --------- | ---------------------------------------------------------------- | ------------- | ------------ | ------------------- |
| first run | the set before its faults were fixed                             | 0.99 (n=84)   | 0.64 (n=72)  | superseded          |
| baseline  | the draft from ADR-1010's appendix, in the tag vocabulary        | 0.99 (n=81)   | 0.88 (n=68)  | baseline            |
| V4        | fix only where the line breaks a rule and the reader loses by it | 0.98 (n=84)   | 0.92 (n=72)  | landed by the owner |

On the three hand-written clean texts alone, after their last correction, the
baseline passed two runs of nine and V4 six. V4 missed one more defect in 84
runs and costs two more lines, so the landing rule left it to the owner, who
landed it.

V4 on Opus 5.5 named defects in 1.00 of runs (n=76) and passed 0.97 of clean
texts (n=66). Fourteen runs timed out at 300 seconds and count as failures.
Its only misses on the named quotation case were a real ambiguity in my text,
whether "five retries two seconds apart" counts a wait before the first retry;
it never judged the quotation (REQ-0999).

The three named cases, each first seen failing against an agent with the same
name and description and no instructions (REQ-2072). That agent failed all
nine runs, eight of them by running out of turns while it searched for a
standard it had not been given:

| Case                          | Kind   | V4 on Sonnet 5 | The empty agent |
| ----------------------------- | ------ | -------------- | --------------- |
| bold-count-long               | defect | 2 of 3         | 0 of 3          |
| clean-with-american-quotation | clean  | 3 of 3         | 0 of 3          |
| comment-restates-the-line     | defect | 3 of 3         | 0 of 3          |

In the run that fell short on `bold-count-long`, the reviewer named two of its
three defects. REQ-3184, REQ-0999, REQ-1012, REQ-1013, REQ-1014, REQ-1024 and
REQ-1026 are closed.

## Left alone

The gate, which blocks and is a separate unit. This reviewer is the deep half
and blocks nothing.
