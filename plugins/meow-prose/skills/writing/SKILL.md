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

<steps name="read what the work needs">
1. For anything longer than a short paragraph, read
   `${CLAUDE_SKILL_DIR}/sentences.md`.
2. For a commit message, a pull request or issue body, a review comment or a
   reply, read `${CLAUDE_SKILL_DIR}/short-texts.md`.
3. For a document, read `${CLAUDE_SKILL_DIR}/documents.md` and the skeleton for
   its type in `${CLAUDE_SKILL_DIR}/types/`: `tutorial`, `how-to`,
   `reference`, `explanation`, `design-proposal`, `readme`, `release-notes`,
   `changelog`, `blog-post`, `research-notes`, `meeting-notes` or
   `daily-notes`. For a project record, read `types/record/record.md` and the
   file for its kind: `vision`, `research`, `requirement`, `decision`,
   `specification`, `epic`, `task` or `defect`.
4. For a code comment or a code example, read `${CLAUDE_SKILL_DIR}/code.md`.
5. When you edit a draft, yours or somebody else's, read
   `${CLAUDE_SKILL_DIR}/editing.md` and the pattern file for what you see in
   `${CLAUDE_SKILL_DIR}/patterns/`: `structure`, `voice` or `sentences`.
6. Before a text is published, run the checks in `editing.md`, and stop when
   every check passes.
</steps>
