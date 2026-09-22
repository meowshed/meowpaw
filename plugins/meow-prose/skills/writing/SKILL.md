---
name: writing
description: Always load this skill before you write anything a person will read - a commit message, a pull request or issue body, a review comment, a code comment, a document, release notes, or a reply - even a one-line commit message, and even when nobody mentions style. It holds the writing standard all of those follow - the answer first, a reason for every rule, one term for one thing, plain English for a reader who learned it as a second language - and the patterns to rewrite before a text leaves your hands.
---

# The writing standard

Write the way an engineer explains a system to a colleague at a shared screen:
the answer first and the reason beside it. Your reader is busy, often reads
English as a second language, and reads at the speed of the hardest word in the
sentence.

Every rule below carries its reason. When a case comes up that no rule foresaw,
ask whether the reason applies, and follow the reason, because a rule applied
without it goes wrong on exactly those cases.

The rules are numbered so a review can cite them. Beside this file sit
`patterns.md`, the shapes to rewrite with a failing and a corrected example of
each; `document-types.md`, the skeleton of each kind of document; and
`self-review.md`, the checks to run before publishing.

## Before you write

Decide who reads it, and state the level at the top of a draft, because the
same fact is written differently for each and a reviewer can only check the
level if it is written down. A reader who is learning is new to the concept:
expand every acronym, link the prerequisites, and explain why before how. A
reader who is integrating knows the platform: explain only what is specific to
this system. A reader who is evaluating is deciding whether to adopt or
approve: lead with the decision, the trade-offs and the limits. If the request
names no reader, ask one question before you draft.

Pick the document type next, because the type fixes the skeleton before you
write a word. `document-types.md` gives each skeleton, and a document missing a
part its type requires is incomplete however good its sentences are.

Write in the language the repository declares in `.meowpaw/profile.toml`, as
`[prose] language`, and in British English where it declares none. One
repository in one language spares the reader a second vocabulary for the same
things. A technical term keeps the spelling its own domain uses, because
respelling a term of art renames the thing. A quotation keeps its author's
wording and spelling, because what you quote is not what you wrote.

Name the two or three rules this type of text breaks most often, and re-read
each paragraph against them before writing the next, because a sentence comes
out shaped like whatever you were last reading.

## Lead with the answer

A1. The first sentence answers the question the heading asks, and the context
follows, because a reader who stops after one sentence should still leave with
the answer.

A2. Every decision carries its reason. A rewrite that drops a "because", a
constraint or a motivation is wrong even when it is shorter, since the reason
is what lets a reader apply the decision to a case its author never saw.

A3. Put the condition before the action: "If validation fails, the gateway
drops the request." A reader who meets the action first has often done it
before reaching the condition.

A4. A warning names the hazard and the consequence, and comes before the step
it protects, because a warning after the step arrives too late.

## Sound like a person

B1. Say "you" for what the reader does and name the component for what the
software does. For a decision the author made, say "I" when one person wrote
the text and "we" when a team did, and keep to it throughout, because a text
with no author reads as law handed down by nobody, and a lone author writing
"we" invents a team the reader cannot ask.

B2. Use contractions where you would say them aloud, and expand them only in a
formal warning or a legal statement. Contractions are how people talk, and text
without them reads as a contract.

B3. Write in the present tense and the active voice, with the actor named. Use
the passive only when the actor is unknown or beside the point, because a
sentence with no actor hides who has to do the thing.

B4. Give instructions in the imperative, without "you should" or "you can",
which make a step sound optional.

B5. A person acts where a person acted, and a fact comes from the document or
the measurement that holds it. "A decision was reached" hides who decided, and
putting words in someone's mouth misreports them.

B6. Drop words that judge the reader's effort: simply, just, easily,
obviously. They tell a struggling reader the fault is theirs.

B7. Drop filler and hype: robust, seamless, leverage, crucial, "it's worth
noting". They take a reader's time and give back no fact.

## Build sentences that read like speech

C1. Average about 20 words a sentence and stay under about 30, with short and
long ones side by side. A run of short sentences reads as a proclamation and a
forty-word sentence reads as a contract.

C2. Join cause and effect inside the sentence with because, so, which means or
when, since a reason in the next sentence reads as a separate claim.

C3. State a claim plainly, without inversion, a contrast bolted on the end, or
an epigram. A sentence that sounds like a proverb has usually lost its reason,
so put the reason back.

C4. One idea per paragraph, topic sentence first, three to five sentences, so a
reader who skims only first sentences still gets the argument.

C5. Give a worked example once and refer to it by name elsewhere, because two
copies drift apart.

C6. Hedge only with a stated condition: "This fails when a batch names two
documents." A bare "might" tells the reader nothing they can check.

## Choose living words

D1. One term, one meaning. Use the name the code or the design gives a thing,
define it once, and never swap in a synonym, because a reader assumes two words
name two things.

D2. Turn the action back into a verb: "changing the record invalidates the
cache", not "invalidation occurs on modification". A noun ending in -tion,
-ment or -ity is often a verb in disguise, and it drops the actor.

D3. Name the thing, not its category. Mechanism, functionality, solution,
process and approach say nothing on their own; a number, a name or a limit
does.

D4. Use the short word where one exists: use, start, end, enough, help, show,
about, send, get, because. Keep the long word when it is the technical name.

D5. Break a chain of "of"s: "how the parser validates its input", not "the
validation of the input of the parser". Readers stall on the third one.

D6. Delete the empty frame: there is, it is X that, the fact that, in terms
of, in the context of. The sentence inside the frame is the whole sentence.

D7. One participle per sentence. A sentence stacking -ing clauses belongs in a
policy manual, so split it.

D8. Use a name rather than a pronoun once two sentences have passed, because
"it" has drifted from its antecedent by then.

D9. Drop demonstrative padding: said, the given, the aforementioned, the
respective. Name the thing.

D10. Prefer a concrete comparison to a stock metaphor. "About 200 bytes" tells
the reader something; "under the hood" tells them nothing.

D11. Read the sentence aloud, and rewrite it until you would say it to a
colleague. This one test catches most of what the rules above describe.

D12. Apply D2 to D9 in every language you write. In Russian that means
`являться`, `осуществлять`, `данный`, `в рамках`, `с целью` and chains of
genitives.

## Say it once

I1. Every sentence adds something the reader lacks. Prose carries its content
in the fewest words the content allows, because every word is paid for when it
is written and again each time it is read.

I2. Cut the frame announcing a claim, the sentence restating its neighbour, the
paragraph introducing the next one, and the hedge with no doubt under it. Keep
"because", "so" and "you", which carry the reasoning.

I3. Say a thing once and refer to it by name after that.

I4. Never shorten by dropping content. After a cut, read the paragraph again,
and if a reason, a constraint or a number went with it, put it back: a shorter
text that lost a fact is a worse text.

## Shape the document

E1. Define a term before you use it, and gloss it in the same sentence where a
forward reference cannot be avoided, because a reader meeting an unknown name
stops reading.

E2. Open with the reader's problem in the reader's words. Your own vocabulary
starts once the problem is on the table.

E3. Open each section with two to four sentences on what it covers, so a reader
who stops after any section has a coherent picture.

E4. Make the headings tell the story on their own, three levels at most,
because a skimmer reads only the headings.

E5. One question per section. A section answering two questions is two
sections, and two sections answering one question are one.

E6. Give sibling sections the same shape, so the reader learns the pattern
once.

E7. Keep the main path for what a first-time reader needs, and move numbers,
edge cases, long tables and derivations to a detail section they can skip.

E8. On the main path, refer back and never forward. "Section 9 explains why"
means the sections are in the wrong order.

E9. Refer to another section in a full sentence, never in a bare "Section 8."
fragment.

E10, E12, E13. Add a glossary near the top when a document introduces more
than five terms; write an executive summary as five to eight sentences of
prose (problem, what was done, its cost, what was not measured, next step); and
add a note on how to read the document only past about 3,000 words.

E11. Put a table or a figure beside the paragraph that uses it, and say what
the reader should take from it.

E14. Test the order with a cold read: wherever a reader who has only the
earlier sections meets a name they cannot place, the structure has failed.

## Format for scanning

F1. Headings in sentence case with no end punctuation and no question mark. A
task heading starts with a verb and a concept heading is a noun phrase.

F2. Numbers for ordered steps, bullets for parallel items, a table for a
comparison across two or more dimensions, and prose for everything else,
including every argument, because a list strips out the "because" that joins
the items.

F3. Bold for interface elements, code font for what the reader types or the
machine reads.

F4. Bold at most one phrase per section, and never open two paragraphs running
in bold. A page of bold openers reads as orders nobody argued for.

F5. ASCII outside quoted code, because some readers' tools mangle anything
else.

F6. Serial comma, ISO dates (2026-09-18), and the declared spelling, while a
name keeps its own: an identifier or a protocol token is never respelled.

## Write for a second-language reader

H1. Use the most common word that is still exact: "big" over "substantial",
"fix" over "remediate".

H2. Give one word one meaning within a document, and avoid a word whose
everyday sense differs from its technical one in the same text.

H3. Prefer the plain verb to an ambiguous phrasal verb: "configure" over "set
up", "run" over "carry out".

H4. No idioms, sayings, sports or culture references, which cost a lookup and
are often mistranslated.

H5. No double negatives and no negative questions, since each has two readings.

H6. Say what a modal means: "can" for permission, "might" for possibility, and
"must not" for a prohibition. "May" and "should" each carry two senses.

H7. Break up a stack of more than two nouns, because the reader cannot tell
which noun modifies which.

H8. Expand every acronym on first use, and write "for example", "that is" and
"and so on" in place of their Latin abbreviations.

H9. Write dates, times and numbers one way only: 2026-09-18, 14:30 CET, 1,500
and 1500 ms.

H10. Keep the subject and the verb close together, because a clause between
them is where a reader loses the sentence.

H11. Repeat the noun wherever two nouns could be the antecedent of a pronoun.

## Show code that runs

G1 to G5. Make every example runnable as pasted, with its prerequisites stated
before it; keep only what the prose around it explains; comment a line that is
not obvious and leave an obvious one alone; say so in the text where you could
not check it; and introduce it with a sentence ending in a colon, tag its fence,
and follow it with prose. A reader copies an example before reading the text
around it, so the example has to be right on its own.

## Comments in code

A comment is prose and follows the same standard. Write one only where the code
cannot be made to explain itself, and improve the name first, unless the name
is an interface others depend on. Keep a comment short and plain: one line
where one line will do, saying why the code does what it does and not what it
does, because the reader already has the code and needs the reason it doesn't
show. Never restate the line below, because the comment goes wrong the first
time that line changes. Delete commented-out code, since version control keeps
it. Give every marker for later work an issue or a task, because a bare marker
is a promise nobody owns.

## Rewrite these patterns

Each hides the author, the reader or the reason; `patterns.md` shows each
failing and corrected: a bold verdict opening a paragraph; a long sentence with
a short punchline; a counted opener; a judgement of worth; a chain of X-is-Y definitions; a contrastive tail; "rather
than" past once in five hundred words; the document as author; an abstract
"one" as subject; a pointer fragment; a summary as bold theses; absence as the
subject; "that" pointing at a whole sentence; "X matters"; a paragraph
narrating itself; draft archaeology; "a person" where the reader is you; a pet
abstraction; drama in place of an argument; a restatement or a preview; and a
bold fragment standing in for a heading.

## Replies

A reply is a short text for a reader who asked a question, and the standard
holds at that scale. Answer in the first sentence, with nothing before it. Reply in the language of the question. Keep the actor in
every sentence: "I changed the parser because", not "the parser was changed".
Format only where it carries information, so a short answer is a paragraph and
not a list with one sentence per bullet. Ask at most one question, at the end,
and only when the answer depends on it. When you disagree, say so once with the
reason, then do what was asked or propose the alternative. When you changed
something, say what and why, then stop.

## Editing somebody else's text

The author's facts outrank your style. Name the main problem first: structure,
voice, accuracy or completeness. Say what you changed and why before showing
the result. Leave alone what you were not asked to change, unless it is wrong.
Flag a claim you cannot verify rather than deleting it. Keep every reason,
constraint and number from the source, because a rewrite that cannot fit one is
too short.

## Before it is published

Run `self-review.md` before a text leaves your hands, because a defect caught
there costs one edit and the same defect caught after the merge costs an issue
and a second change.
