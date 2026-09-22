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

<steps name="read what the work needs">
1. For anything longer than a sentence or two, read
   `${CLAUDE_SKILL_DIR}/voice.md`.
2. For anything longer than a short paragraph, also read
   `${CLAUDE_SKILL_DIR}/sentences.md`.
3. For a commit message, a pull request or issue body, a review comment or a
   reply, read `${CLAUDE_SKILL_DIR}/short-texts.md`.
4. For a document, read `${CLAUDE_SKILL_DIR}/documents.md` and the skeleton for
   its type in `${CLAUDE_SKILL_DIR}/types/`: `tutorial`, `how-to`,
   `reference`, `explanation`, `design-proposal`, `readme`, `release-notes`,
   `changelog`, `blog-post`, `research-notes`, `meeting-notes` or
   `daily-notes`. For a project record, read `types/record/record.md` and the
   file for its kind: `vision`, `research`, `requirement`, `decision`,
   `specification`, `epic`, `task` or `defect`.
5. For a code comment or a code example, read `${CLAUDE_SKILL_DIR}/code.md`.
6. When you edit a draft, yours or somebody else's, read
   `${CLAUDE_SKILL_DIR}/editing.md` and the pattern file for what you see in
   `${CLAUDE_SKILL_DIR}/patterns/`: `structure`, `voice` or `sentences`.
7. Before a text is published, run the checks in `editing.md`, and stop when
   every check passes.
</steps>
