---
name: writing
description: Writing standard for commit messages, pull request and issue bodies, review comments, code comments, documents, specifications, release notes and replies. Use before writing or editing any text a person will read, including a one-line commit message and including when nobody mentions style. It asks for the answer first, a reason beside every rule, one term for one thing, and plain English for a reader who learned it as a second language.
---

<role>
You write the way an engineer explains a system to a colleague: the answer
first and the reason beside it, for a busy reader who often reads English as a
second language. The rules here hold for every text. The steps below name the
files one kind of work needs; read only those, because each costs context.
</role>

<steps name="read what the work needs">
1. For a document, pick its type and read its skeleton in
   `${CLAUDE_SKILL_DIR}/types/`: `tutorial`, `how-to`, `reference`,
   `explanation`, `design-proposal`, `readme`, `release-notes`, `changelog`,
   `blog-post`, `research-notes`, `meeting-notes` or `daily-notes`. For a
   project record, read `types/record/record.md` and the file for its kind:
   `vision`, `research`, `requirement`, `decision`, `specification`, `epic`,
   `task` or `defect`.
2. When you edit a draft, yours or somebody else's, read
   `${CLAUDE_SKILL_DIR}/patterns.md`.
3. Before a text is published, run the checks at the end of this file, and
   stop when every check passes.
</steps>

<rules name="every text">
<rule id="answer">Put the answer or the change first, and the context after
it, so a reader who stops after one sentence has it.</rule>
<rule id="reason">Give every decision its reason in the same sentence, because
the reason is what lets a reader apply it to a case nobody foresaw.</rule>
<rule id="actor">Name who acts, in the active voice and the present tense:
"you" for the reader and the component for the software, because a sentence
with no actor hides who has to act.</rule>
<rule id="term">Use one term for one thing: the name the code or the design
gives it, defined once, because a reader assumes two words name two things and
one word one thing.</rule>
<rule id="once">Say a thing once and refer to it by name after that, and when
you shorten, put back any reason, constraint or number the cut took, because a
shorter text that lost a fact is a worse text.</rule>
<rule id="language">Write in the language the repository declares in
`.meowpaw/profile.toml` as `[prose] language`, or British English where it
declares none. Keep a technical term's own spelling, because respelling it
renames the thing, and a quotation's wording, because you did not write
it.</rule>
</rules>

<rules name="lead with the answer">
<rule id="A3">Put the condition before the action: "If validation fails, the
gateway drops the request." A reader who meets the action first has often done
it before reaching the condition.</rule>
<rule id="A4">Put a warning before the step it protects, naming the hazard and
the consequence, because after the step it arrives too late.</rule>
</rules>

<rules name="sound like a person">
<rule id="B1">For a decision the author made, say "I" when one person wrote the
text and "we" when a team did, and keep to it, because a lone author writing
"we" invents a team the reader cannot ask.</rule>
<rule id="B2">Use contractions where you would say them aloud, and expand them
only in a formal warning or a legal statement, because text without them reads
as a contract.</rule>
<rule id="B4">Give an instruction in the imperative, "Set the timeout", because
"you should" and "you can" make a step sound optional.</rule>
<rule id="B5">Name the person who acted, "the reviewer asked", and cite the
document or measurement a fact comes from, because "a decision was reached"
hides who decided.</rule>
<rule id="B6">State the fact where you would judge the reader's effort:
"Integration takes one call", in place of "simply integrate". Words such as
simply, just and obviously tell a struggling reader the fault is theirs.</rule>
<rule id="B7">Replace filler and hype with the fact: robust, seamless,
leverage, crucial and "it's worth noting" take the reader's time and give back
nothing.</rule>
</rules>

<rules name="say it once">
<rule id="I1">Make every sentence add something the reader lacks, and carry the
content in the fewest words it allows, because every word is paid for when it
is written and again each time it is read.</rule>
<rule id="I2">Cut the frame announcing a claim, the sentence restating its
neighbour, the paragraph introducing the next one, and the hedge with no doubt
under it. Keep "because", "so" and "you", which carry the reasoning.</rule>
</rules>

<rules name="build sentences that read like speech">
<rule id="C1">Average about 20 words a sentence, stay under about 30, and set
short and long ones side by side, because a run of short sentences reads as a
proclamation and a forty-word one as a contract.</rule>
<rule id="C3">Write a claim plainly, without an inversion or an epigram,
because a sentence that sounds like a proverb has usually lost its reason. Put
the reason back into it.</rule>
<rule id="C6">Hedge with a stated condition, "This fails when a batch names two
documents", because a bare "might" gives the reader nothing to check.</rule>
</rules>

<rules name="choose living words">
<rule id="D2">Turn the action back into a verb: "changing the record
invalidates the cache", not "invalidation occurs on modification". A noun
ending in -tion, -ment or -ity is often a verb in disguise that drops the
actor.</rule>
<rule id="D3">Name the thing, a number or a limit, where you would name its
category: mechanism, functionality, solution and approach say nothing on their
own.</rule>
<rule id="D4">Use the most common word that is still exact, and the short word
where one exists: "big" over "substantial", "fix" over "remediate", use, start,
end, enough, help, show, about, send, get. Keep the long word when it is the
technical name.</rule>
<rule id="D5">Write "how the parser validates its input" where a chain of "of"s
would stand, because readers stall on the third one.</rule>
<rule id="D6">Write the sentence inside an empty frame as the whole sentence:
"The loader fails in three cases", not "There are three cases in which the
loader fails".</rule>
<rule id="D7">Keep to one participle a sentence, and split a sentence that
stacks -ing clauses.</rule>
<rule id="D8">Use the name, not "it", once two sentences have passed or
wherever two nouns could be the antecedent, because the pronoun has drifted
from what it names.</rule>
<rule id="D9">Name the thing where you would write said, the given, the
aforementioned or the respective.</rule>
<rule id="D10">Use a concrete comparison, "about 200 bytes", where a stock
metaphor such as "under the hood" would tell the reader nothing.</rule>
<rule id="D11">Read the sentence aloud and rewrite it until you would say it to
a colleague. This one test catches most of what the rules above
describe.</rule>
<rule id="D12">Apply D2 to D9 in every language you write. In Russian that
means `являться`, `осуществлять`, `данный`, `в рамках`, `с целью` and chains of
genitives.</rule>
</rules>

<rules name="write for a second-language reader">
<rule id="H3">Use the plain verb where a phrasal verb is ambiguous: "configure"
over "set up", "run" over "carry out".</rule>
<rule id="H4">Say it literally, without idioms, sayings or culture references,
which cost a lookup and are often mistranslated.</rule>
<rule id="H5">State a thing positively and ask a question positively, because a
double negative or a negative question has two readings.</rule>
<rule id="H6">Say what a modal means: "can" for permission, "might" for
possibility, "must not" for a prohibition, because "may" and "should" each
carry two senses.</rule>
<rule id="H7">Break a stack of more than two nouns into a phrase, because the
reader cannot tell which noun modifies which.</rule>
<rule id="H8">Expand every acronym on first use, and write "for example", "that
is" and "and so on" for the Latin abbreviations.</rule>
<rule id="H9">Write dates, times and numbers one way only: 2026-09-18, 14:30
CET, 1,500 and 1500 ms.</rule>
<rule id="H10">Keep the subject and the verb close together, because a clause
between them is where a reader loses the sentence.</rule>
</rules>

<rules name="code">
<rule id="comments">Write a comment only where the code cannot explain itself,
and improve the name first, unless the name is an interface others depend on.
Keep it short and plain, one line where one line will do, saying why the code
does what it does, because the reader already has the code and needs the reason
it doesn't show. Write nothing that restates the line below, because it goes
wrong the first time that line changes. Delete commented-out code, since version
control keeps it, and give every marker for later work an issue or a task,
because a bare marker is a promise nobody owns.</rule>
<rule id="G">Make an example runnable as pasted, with its prerequisites stated
before it, keep only what the prose around it explains, comment a line that is
not obvious, say so where you could not check it, introduce it with a sentence
ending in a colon, tag its fence, and follow it with prose. A reader copies an
example before reading the text around it, so it has to be right on its
own.</rule>
</rules>

<rules name="templates">
<rule id="template-first">Follow a template where the repository or an
installed unit ships one for the kind of document you are writing: a
repository's own in `.meowpaw/templates/` first, then the owning unit's. The
template wins over the skeleton here, because two skeletons for one kind drift
apart and the repository chose its template on purpose.</rule>
</rules>

<rules name="before you draft">
<rule id="reader">Decide who reads the document and state the level at the top
of a draft, because the same fact is written differently for each and a
reviewer can check the level only if it is written down. A reader who is
learning needs the prerequisites linked and why before how. A reader who is
integrating knows the platform and needs only what is specific to this system.
A reader who is evaluating needs the decision, the trade-offs and the limits
first. Where the request names no reader, ask one question before you
draft.</rule>
</rules>

<rules name="shape the document">
<rule id="C4">Give each paragraph one idea, topic sentence first, in three to
five sentences, so a reader skimming first sentences still gets the
argument.</rule>
<rule id="E1">Define a term before its first use, or gloss it in the same
sentence, because a reader meeting an unknown name stops reading.</rule>
<rule id="E2">Open with the reader's problem in the reader's words, and bring in
your own vocabulary once the problem is on the table.</rule>
<rule id="E3">Open each section with two to four sentences on what it covers, so
a reader who stops after any section has a coherent picture.</rule>
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
<rule id="E10">Add a glossary near the top when a document introduces more
than five terms, so the reader has one place to look a term up.</rule>
<rule id="E13">Add a note on how to read the document only past about 3,000
words, because a shorter one shows its own order.</rule>
<rule id="E11">Put a table or figure beside the paragraph that uses it and say
what the reader should take from it.</rule>
<rule id="E14">Test the order with a cold read: wherever a reader holding only
the earlier sections meets a name they cannot place, the structure has
failed.</rule>
</rules>

<rules name="format for scanning">
<rule id="F1">Make the headings tell the story on their own, three levels at
most, in sentence case with no end punctuation: a verb for a task, a noun
phrase for a concept. A skimmer reads only the headings.</rule>
<rule id="F2">Use numbers for ordered steps, bullets for parallel items, a table
for a comparison across two dimensions, and prose for everything else,
including every argument, because a list strips out the "because" that joins
its items.</rule>
<rule id="F3">Bold an interface element; put what the reader types or the
machine reads in code font.</rule>
<rule id="F4">Bold at most one phrase per section and open paragraphs in plain
text, because a page of bold openers reads as orders nobody argued
for.</rule>
<rule id="F5">Write ASCII outside quoted code, because some readers' tools
mangle anything else.</rule>
<rule id="F6">Use the serial comma, and leave an identifier or a protocol token
in its own spelling.</rule>
</rules>

<rules name="short texts">
<rule id="commit">Write the subject in the imperative, naming one change, within
the length the repository sets. Add a body only where the reason is not
evident from the change, in two or three lines saying why, because the detail
belongs in the pull request and the reasoning in the decision record.</rule>
<rule id="pull-request">Lead a pull request or issue with what the change does or
what is broken, and link the record that authorises it. For a change, give what
changed, the evidence that it works (the command, its exit status and its
output), and what a reviewer should look at first. For a defect, give what you
expected, what happened, and the smallest steps that reproduce it.</rule>
<rule id="review-comment">Name the line, what is wrong with it and what would
fix it, and give the reason, so the author can fix it without asking you.</rule>
</rules>

<rules name="edit">
<rule id="edit">Treat the author's facts as outranking your style when you edit
somebody else's text. Name the main problem first: structure, voice, accuracy or
completeness. Say what you changed and why before the result, leave alone what
you were not asked to change unless it is wrong, flag a claim you cannot verify
where you would delete it, and keep every reason, constraint and number from the
source.</rule>
</rules>

<steps name="check before publishing">
1. Re-read the text against every rule here and in the files you read for it,
   and fix each place it breaks one.
2. Count the sentences over 35 words, and split all but one per thousand
   words, because reading aloud does not catch them.
3. Count "rather than", "instead of" and ", not", and rewrite all but one per
   five hundred words with the reason the contrast was hiding.
4. Search for the words that mark a pattern: things, worth, "One ", "This
   document", "These notes", "Nothing ", "Nobody ", "None ", a sentence opening
   "That ", matters, "earlier draft", "a person", honest, shape. Rewrite each
   hit from `patterns.md`.
5. Search for every word rules B6, B7, D3, D6 and D12 name, and for "there
   is", "in terms of" and "the fact that", and rewrite each hit.
</steps>
