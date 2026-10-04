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
1. Run `meow-scm convention` to see the types the
   repository declares, what each means for a release, the subject limit and
   the trailers. Where it says the convention is undeclared, say so to the
   person, and follow only the rules below.
2. Write the message by the rules below.
3. Run the check on the exact text you will use, passed on standard input:
   `meow-scm check-message`. Fix every line it
   names and run it again.
4. Use the message only when the check exits 0. Where it exits 3 because the
   convention is undeclared, tell the person the message was checked for
   attribution alone. Never use a message the check failed. Stop once the
   message you use has passed.
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
- M7. Where the subject carries `!` or a type the convention means `major`,
  say what breaks in a `BREAKING CHANGE:` trailer, because whoever cuts the
  release won't remember it.
- M8. Write a trailer naming a person, such as `Co-authored-by` or
  `Reviewed-by`, only for someone listed under `[commits] may_name`, because
  naming a person needs their agreement and the list is where the repository
  records it. Three trailers record where something came from and are exempt:
  `Signed-off-by` naming the author, `Cherry-picked-from` and `Fixes`. The
  first `Signed-off-by` names the author, because the chain records the route
  the change took and approves nothing.
</rules>

<rules name="branches">
- B1. Give one task one branch, one pull request and one review, and land it
  on the trunk as one squashed commit, because the history then reads as a
  list of what the project gained.
- B2. Take every branch from the one trunk and keep it short-lived, and never
  keep a second long-lived branch, because two trunks drift and every change
  then lands twice.
- B3. Merge, tag, release or publish only when the person tells you to, for
  that change, because each is a public act the person answers for.
- B4. Never check out one branch in two working trees, and never force it:
  take a new branch or a detached checkout for parallel work. Working trees
  share one repository, so a branch or a tag made in one exists in all.
- B5. Lock a working tree while you use it, with the reason, in the way the
  source control tool offers, because a cleanup reclaims an unlocked tree
  with your work in it.
- B6. Split a branch that has grown past one reviewable change into several,
  rather than extending it, because review turns into approval past a size.
- B7. Say so in the pull request when you force-push over a branch someone
  reviewed, because the push removes what they reviewed.
- B8. Sign every commit, and write the sign-off as well where the repository
  asks for both: the signature says the claim wasn't forged, the sign-off
  says who makes it.
</rules>

<example name="a subject">
Failing:

fix: addressed review feedback and ran the checks again

Corrected:

fix: read a link whose target sits in angle brackets
</example>
