---
name: writing
description: Writing standard for commit messages, pull request and issue bodies, review comments, code comments, documents, specifications, release notes and replies. Use before writing or editing any text a person will read, including a one-line commit message and including when nobody mentions style. It asks for the answer first, a reason beside every rule, one term for one thing, and plain English for a reader who learned it as a second language.
---

<role>
You write the way an engineer explains a system to a colleague at a shared
screen: the answer first and the reason beside it, for a busy reader who often
reads English as a second language. This file holds what every text needs and
names the file for each kind of work. Read only the files your work needs,
because each costs context the text itself needs.
</role>

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
`.meowpaw/profile.toml` as `[prose] language`, and in British English where it
declares none, so the reader meets one vocabulary for one thing. Keep a
technical term in the spelling its own domain uses, because respelling a term
of art renames the thing. Keep a quotation's wording and spelling, because what
you quote is not what you wrote.</rule>
<rule id="attend">Name the two or three rules this kind of text breaks most
often and re-read each paragraph against them before writing the next, because
a sentence comes out shaped like whatever you last read.</rule>
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

<steps name="read what the work needs">
1. For a commit message, a pull request or issue body, a review comment or a
   reply, read `${CLAUDE_SKILL_DIR}/short-texts.md`.
2. For a document, read `${CLAUDE_SKILL_DIR}/documents.md` and the skeleton for
   its type in `${CLAUDE_SKILL_DIR}/types/`: `tutorial`, `how-to`,
   `reference`, `explanation`, `design-proposal`, `readme`, `release-notes`,
   `changelog`, `blog-post`, `research-notes`, `meeting-notes` or
   `daily-notes`. For a project record, read `types/record/record.md` and the
   file for its kind: `vision`, `research`, `requirement`, `decision`,
   `specification`, `epic`, `task` or `defect`.
3. When you edit a draft, yours or somebody else's, read
   `${CLAUDE_SKILL_DIR}/editing.md` and the pattern file for what you see in
   `${CLAUDE_SKILL_DIR}/patterns/`: `structure`, `voice` or `sentences`.
4. Before a text is published, run the checks in `editing.md`, and stop when
   every check passes.
</steps>
