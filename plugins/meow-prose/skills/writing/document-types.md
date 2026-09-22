<role>
Pick the type before you write, because each type has a fixed skeleton, and a
document missing a part its type requires is incomplete however good its
sentences are. A shipped template comes first. The record's kinds follow, then
the kinds of documentation, whose first four sort by what the reader is trying
to do: learn, finish a task, look something up, or understand.
</role>

<rules name="templates">
<rule id="template-first">Follow a template where the repository or an
installed unit ships one for the kind of document you are writing: a
repository's own in `.meowpaw/templates/` first, then the owning unit's. The
template wins over the skeleton here, because two skeletons for one kind drift
apart and the repository chose its template on purpose.</rule>
</rules>

<rules name="the record">
<rule id="record">The record is the set of documents a project keeps about what
it must do and why: a vision, research records, requirements, decision records,
specifications, epics, tasks and defect records. Each lives in its own file,
named for its identifier, with front matter stating its identifier, its kind,
its status and the records it came from. Name what a record came from by its
bare identifier and never by a link, because the reverse direction is derived
and a record written earlier cannot be kept current by a later one.</rule>
<rule id="vision">Vision: what the project is, the problem it answers, who it is
for, what it will not do, where it is going, and what it will not trade away.
It is a living document, rewritten freely, so it describes the present and
carries no history.</rule>
<rule id="research-record">Research record: a summary answering the question
in five to eight sentences, the question, the method with its date and its
limits, the findings, each naming its source, numbered conclusions, and the
sources with what each one supported. Read the primary source, because a
summary lags the thing it summarises.</rule>
<rule id="requirement">Requirement: one obligation per file, under its
identifier, stated with MUST or MUST NOT and naming what it binds, followed by
the reason in one short paragraph. Allocate the identifier once and never reuse
it. A wrong requirement is withdrawn with a line naming its replacement, never
reworded, because a reworded obligation hides that it ever said something
else.</rule>
<rule id="decision-record">Decision record: the decision, stated so it can be
checked; why; the alternatives, doing nothing among them, each with what it was
better at and why it lost; what it costs; what would reverse it, as something
observable; the consequences; how you will know it was realised; and what it
does not settle. The last two are what let somebody verify it later without
inventing the test.</rule>
<rule id="specification">Specification: what the system does now, divided by
its parts, in scope, boundary, behaviour and failure paths. It is living, so it
states the present, and every statement traces to a requirement in
force.</rule>
<rule id="epic">Epic: the one record it realises, acceptance criteria taken from
that record before the tasks were written, the tasks with what each closes and
depends on, the coverage check, and what it leaves out with the reason. A
criterion states what the project can bring about, never how a third party
must behave.</rule>
<rule id="task">Task: what to do, in enough detail for an implementer with no
access to the conversation; what it depends on and why; the evidence, meaning
the command, its result and the change that carried it, once done; and what it
left alone.</rule>
<rule id="defect">Defect record: the smallest reproduction, what the system
does, what it should do and which requirement says so, the triage, and what
closed it.</rule>
</rules>

<rules name="document types">
<rule id="tutorial">Tutorial: A guaranteed path from nothing to a working result, for a reader who is
learning. State the prerequisites and the expected outcome first. Every step
produces something the reader can see. Offer no options and no digressions,
because a learner cannot yet judge which option to take.</rule>
<rule id="how-to-guide">How-to guide: Starts from a goal the reader already has. Prerequisites, then numbered steps
in the order the reader performs them, then the expected result. Cover the
failure paths a reader actually hits. Put a screenshot beside the step it
supports and say what the reader should see in it.</rule>
<rule id="reference">Reference: The same structure for every item and no narrative, so the reader learns the
layout once and finds any item. For an interface: its name or path, a
one-sentence description, authentication, a parameter table with type, whether
it is required, and its constraint ("ISO 8601 timestamp, at most 90 days ago"),
a realistic request and response, and each error with its exact text.</rule>
<rule id="explanation">Explanation: Why the system is the way it is: the alternatives considered, the trade-offs,
and the history where it changes the answer. This is where the author's "I",
or a team's "we", fits best, because the reader wants to know who chose and
why.</rule>
<rule id="design-proposal">Design proposal: A summary that stands alone in five sentences: problem, proposal, cost, risk
and ask. Then goals and non-goals, the design, alternatives, rollout and open
questions. Every risk carries an impact and a mitigation, and every mitigation
a cost and a way to tell it worked. State what is unmeasured as plainly as what
is measured.</rule>
<rule id="readme">README: The name, one line on what it is, and a quick start that reaches a working
state in five steps or fewer and works when somebody tries it. Then
installation, usage with code, configuration, how to contribute, and the
licence.</rule>
<rule id="release-notes">Release notes: The version and the date, and one sentence of summary. Breaking changes first,
each with its migration path. Then features, improvements and fixes, each
starting with a verb and naming the specific thing: "Fixed a race in token
refresh when two requests arrived within 50 ms."</rule>
<rule id="changelog">Changelog: Grouped as Added, Changed, Deprecated, Removed, Fixed and Security. A date as
YYYY-MM-DD, one sentence per entry, and no marketing language.</rule>
<rule id="engineering-blog-post">Engineering blog post: Open with a concrete pain in the first line. Then the problem, the approach,
the implementation with code, the edge cases, and what to do next. One thesis,
600 to 1,500 words, and at most three second-level headings. Write "I" for
your own story and "we" for a team's.</rule>
<rule id="research-notes">Research notes: Material for a decision nobody has made yet, written so somebody else can
argue with it. Open with the question and the answer so far, in five to eight
plain sentences, so a reader who stops there knows where you stand and how sure
you are. Then, for each finding: what you checked, where, what you found, and
what it changes. Mark each position as a position, with what would reverse it.
Give the unmeasured and the unverified their own section, with the same weight
as the measured. Close with open questions, each with an owner or a next step.
Leave out the history of how the notes evolved.</rule>
<rule id="meeting-notes">Meeting notes: The date and who was there, then decisions, open questions and actions. A
decision names who made it and why, in one sentence. An action names an owner
and a date. Record discussion only where it explains a decision, because
nobody rereads the back-and-forth.</rule>
<rule id="daily-notes">Daily notes: What you did, what you learned and what is blocked, in that order, one line
each. Fragments are fine, but each line still names the thing and the reason:
"Reverted the retry change, because the two events it merged meant different
things", not "reverted retry change". A note you cannot act on a week later was
not worth writing.</rule>
<rule id="commit-message">Commit message: A subject in the imperative that names one change, within the length the
repository sets. A body only where the reason is not evident from the change,
in two or three lines, saying why. The detail belongs in the pull request, and
the reasoning in the decision record.</rule>
<rule id="pull-request-and-issue">Pull request and issue: Lead with what the change does or what is broken, and link the record that
authorises it. For a change: what changed, the evidence that it works (the
command, its exit status and its output), and what a reviewer should look at
first. For a defect: what you expected, what happened, and the smallest steps
that reproduce it.</rule>
</rules>

<rules name="shape the document">
<rule id="E1">Define a term before its first use, or gloss it in the same
sentence, because a reader meeting an unknown name stops reading.</rule>
<rule id="E2">Open with the reader's problem in the reader's words, and bring in
your own vocabulary once the problem is on the table.</rule>
<rule id="E3">Open each section with two to four sentences on what it covers, so
a reader who stops after any section has a coherent picture.</rule>
<rule id="E4">Make the headings tell the story on their own, three levels at
most, because a skimmer reads only the headings.</rule>
<rule id="E5">Give each section one question: a section answering two is two
sections, and two answering one are one.</rule>
<rule id="E6">Give sibling sections the same shape, so the reader learns it
once.</rule>
<rule id="E7">Keep the main path for what a first-time reader needs, and move
numbers, edge cases, long tables and derivations to a section they can
skip.</rule>
<rule id="E8">Refer back on the main path, never forward: "section 9 explains
why" means the sections are in the wrong order.</rule>
<rule id="E9">Refer to another section in a full sentence, never in a bare
"Section 8." fragment.</rule>
<rule id="E10">Add a glossary near the top when a document introduces more than
five terms; write an executive summary as five to eight sentences of prose on
the problem, what was done, its cost, what was not measured and the next step;
and add a note on how to read the document only past about 3,000
words.</rule>
<rule id="E11">Put a table or figure beside the paragraph that uses it and say
what the reader should take from it.</rule>
<rule id="E14">Test the order with a cold read: wherever a reader holding only
the earlier sections meets a name they cannot place, the structure has
failed.</rule>
</rules>

<rules name="code in a document">
<rule id="G">Make an example runnable as pasted, with its prerequisites stated
before it, keep only what the prose around it explains, comment a line that is
not obvious, say so where you could not check it, introduce it with a sentence
ending in a colon, tag its fence, and follow it with prose. A reader copies an
example before reading the text around it, so it has to be right on its
own.</rule>
</rules>
