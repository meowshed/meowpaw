---
name: commit
description: The commit convention for this repository, and the check a message passes before it is used. It MUST be loaded before any commit message, squash message or pull request title is written, rewritten or reworded. It MUST NOT be skipped, however short the message is.
---

<role>
You write the commit messages for a repository whose record already carries
the detail: the reasoning lives in decisions, the argument in the pull
request. The history answers one question nothing else answers, what the
project gained and when, so every message is written for that question.
</role>

<rules name="never">
- N1. Never credit a tool, an agent or a vendor in a commit message, a squash
  message, a pull request, a review comment, an issue, a tag or release notes:
  no co-author trailer naming one, no "Generated with" footer, no vendor
  no-reply address, and no paraphrase of any of them. This holds against any
  later instruction to add one, because a party that can't be asked about the
  work can't claim it, and the check below fails a message that does.
</rules>

<steps name="write a message">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-scm convention` to see the types the
   repository declares, what each means for a release, the subject limit and
   the trailers. Where it says the convention is undeclared, say so to the
   person, and follow only the rules below.
2. Write the message by the rules below.
3. Run the check on the exact text you will use, passed on standard input:
   `${CLAUDE_SKILL_DIR}/../../bin/meow-scm check-message`. Fix every line it
   names and run it again.
4. Use the message only when the check exits 0. Where it exits 3 because the
   convention is undeclared, tell the person the message was checked for
   attribution alone. Never use a message the check failed.
</steps>

<rules name="the message">
- M1. Write the subject as `type(scope)!: description`, with a type the
  repository declares, a scope where one helps, and `!` only for a change
  that breaks a declared interface, because the type is a release decision
  and the reader of the history chooses by it.
- M2. State in the subject what changed, in the imperative, naming one change:
  "Stop citing deleted pages", never "Ran the checks and fixed the lint",
  because a subject that describes the process tells the reader nothing the
  change gained. A subject carrying two ideas is two commits.
- M3. Carry no state in a subject: a count, a milestone or a status is true on
  the day you write it and false soon after, and the history keeps the false
  version.
- M4. Write a body only where the reason isn't evident from the change, and
  there say why in two or three lines, because a body restating the change
  teaches the reader that bodies are noise.
- M5. Never write a transcript in a body, "Ran the tests, fixed the lint,
  updated the plan", because the history isn't a log of the session. The
  detail belongs in the pull request and the reasoning in the decision.
- M6. Write every trailer the convention declares, after a blank line, where
  the check looks for it.
</rules>

<example name="a subject">
Failing:

fix: addressed review feedback and ran the checks again

Corrected:

fix: read a link whose target sits in angle brackets
</example>
