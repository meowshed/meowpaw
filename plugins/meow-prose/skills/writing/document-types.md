# Document types

Pick the type before you write, because each type has a fixed skeleton, and a
document missing a part its type requires is incomplete however good its
sentences are. The first four types sort documentation by what the reader is
trying to do: learn, finish a task, look something up, or understand.

## Tutorial

A guaranteed path from nothing to a working result, for a reader who is
learning. State the prerequisites and the expected outcome first. Every step
produces something the reader can see. Offer no options and no digressions,
because a learner cannot yet judge which option to take.

## How-to guide

Starts from a goal the reader already has. Prerequisites, then numbered steps
in the order the reader performs them, then the expected result. Cover the
failure paths a reader actually hits. Put a screenshot beside the step it
supports and say what the reader should see in it.

## Reference

The same structure for every item and no narrative, so the reader learns the
layout once and finds any item. For an interface: its name or path, a
one-sentence description, authentication, a parameter table with type, whether
it is required, and its constraint ("ISO 8601 timestamp, at most 90 days ago"),
a realistic request and response, and each error with its exact text.

## Explanation

Why the system is the way it is: the alternatives considered, the trade-offs,
and the history where it changes the answer. This is where the author's "I",
or a team's "we", fits best, because the reader wants to know who chose and
why.

## Decision record

Title, status and date. Context: the forces at play. The decision, in one
paragraph, stated as a fact. Consequences, good and bad, each with a concrete
effect. The alternatives considered, with the reason each lost. What would
reverse the decision, stated as something observable.

## Design proposal

A summary that stands alone in five sentences: problem, proposal, cost, risk
and ask. Then goals and non-goals, the design, alternatives, rollout and open
questions. Every risk carries an impact and a mitigation, and every mitigation
a cost and a way to tell it worked. State what is unmeasured as plainly as what
is measured.

## README

The name, one line on what it is, and a quick start that reaches a working
state in five steps or fewer and works when somebody tries it. Then
installation, usage with code, configuration, how to contribute, and the
licence.

## Release notes

The version and the date, and one sentence of summary. Breaking changes first,
each with its migration path. Then features, improvements and fixes, each
starting with a verb and naming the specific thing: "Fixed a race in token
refresh when two requests arrived within 50 ms."

## Changelog

Grouped as Added, Changed, Deprecated, Removed, Fixed and Security. A date as
YYYY-MM-DD, one sentence per entry, and no marketing language.

## Engineering blog post

Open with a concrete pain in the first line. Then the problem, the approach,
the implementation with code, the edge cases, and what to do next. One thesis,
600 to 1,500 words, and at most three second-level headings. Write "I" for
your own story and "we" for a team's.

## Research notes

Material for a decision nobody has made yet, written so somebody else can
argue with it. Open with the question and the answer so far, in five to eight
plain sentences, so a reader who stops there knows where you stand and how sure
you are. Then, for each finding: what you checked, where, what you found, and
what it changes. Mark each position as a position, with what would reverse it.
Give the unmeasured and the unverified their own section, with the same weight
as the measured. Close with open questions, each with an owner or a next step.
Leave out the history of how the notes evolved.

## Meeting notes

The date and who was there, then decisions, open questions and actions. A
decision names who made it and why, in one sentence. An action names an owner
and a date. Record discussion only where it explains a decision, because
nobody rereads the back-and-forth.

## Daily notes

What you did, what you learned and what is blocked, in that order, one line
each. Fragments are fine, but each line still names the thing and the reason:
"Reverted the retry change, because the two events it merged meant different
things", not "reverted retry change". A note you cannot act on a week later was
not worth writing.

## Commit message

A subject in the imperative that names one change, within the length the
repository sets. A body only where the reason is not evident from the change,
in two or three lines, saying why. The detail belongs in the pull request, and
the reasoning in the decision record.

## Pull request and issue

Lead with what the change does or what is broken, and link the record that
authorises it. For a change: what changed, the evidence that it works (the
command, its exit status and its output), and what a reviewer should look at
first. For a defect: what you expected, what happened, and the smallest steps
that reproduce it.
