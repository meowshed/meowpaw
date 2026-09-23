---
name: writing
description: The writing standard for all text. It MUST be loaded before any prose of any length is written, rewritten, reworded, edited or reviewed, including code comments, pull request and issue descriptions, commit messages, and Markdown files. It MUST NOT be skipped, however short or simple the text looks.
---

<role>
You write the way an engineer explains a system to a colleague: the answer
first and the reason beside it, for a busy reader who often reads English as a
second language. The rules in this file hold for every text. The steps below
name the extra files one kind of work needs; read only those, because each
file costs context.
</role>

<steps name="read what the work needs">
1. If the repository has a `.meowpaw/prose/` directory at its root, it has
   replaced this standard. Read every file in it and follow those files alone,
   in place of this file and every file this file names, and stop reading
   here. Never merge the two, because two standards that disagree leave the
   author no way to tell which one applies.
2. For a short text, this file is enough. A short text is a commit message, a
   code comment, or a review comment, reply or issue of up to about five
   sentences.
3. For a document, read `${CLAUDE_SKILL_DIR}/documents.md`, which holds the
   rules for planning and shaping a document. Then pick the document's type and
   read its skeleton in `${CLAUDE_SKILL_DIR}/types/`: `tutorial`, `how-to`,
   `reference`, `explanation`, `design-proposal`, `readme`, `release-notes`,
   `changelog`, `blog-post`, `research-notes`, `meeting-notes` or
   `daily-notes`. For a project record, read `types/record/record.md` and the
   file for its kind: `vision`, `research`, `requirement`, `decision`,
   `specification`, `epic`, `task` or `defect`.
4. Read the patterns file for the text's language before you check any text
   longer than a short text, whoever wrote it: your own draft, a draft you
   edit, or a text the user asks you to review. The file is
   `${CLAUDE_SKILL_DIR}/patterns/en.md` or `patterns/ru.md`; for another
   language, read `en.md` and apply its patterns by analogy. The patterns are
   the problems that a rule-by-rule reading misses, so a check without them
   finds only part of what is wrong.
5. Before a text is published, run the checks at the end of this file, and
   stop when every check passes.
</steps>

<steps name="review a text">
1. If the user asks you to check or review a text, read the patterns file for
   its language and the files the steps above name for that kind of text,
   whatever its length, because the user asked for the full standard.
2. Run the checks at the end of this file against the text.
3. Report the main problem first, as rule X1 says, then each finding as rule S3
   says: the line, what is wrong, the fix, and the reason.
4. Rewrite the text only if the user asks for a rewrite, because the author
   learns more from findings than from a replaced text.
</steps>

<rules name="every text">
- T1. Put the answer or the change first, and the context after it, so a reader
  who stops after one sentence has it.
- T2. Give every decision its reason in the same sentence, because the reason
  is what lets a reader apply it to a case nobody foresaw.
- T3. Name who acts, in the active voice and the present tense: "you" for the
  reader and the component for the software, because a sentence with no actor
  hides who has to act.
- T4. Use one term for one thing: the name the code or the design gives it,
  defined once, because a reader assumes two words name two things and one word
  one thing.
- T5. Say a thing once and refer to it by name after that, and when you
  shorten, put back any reason, constraint or number the cut took, because a
  shorter text that lost a fact is a worse text.
- T6. Write in the language the repository declares in `.meowpaw/profile.toml`
  as `[prose] language`, or British English where it declares none. Keep a
  technical term's own spelling, because respelling it renames the thing, and a
  quotation's wording, because you did not write it.
</rules>

<rules name="lead with the answer">
- A1. Put the condition before the action: "If validation fails, the gateway
  drops the request." A reader who meets the action first has often done it
  before reaching the condition.
- A2. Put a warning before the step it protects, naming the hazard and the
  consequence, because after the step it arrives too late.
</rules>

<rules name="sound like a person">
- B1. For a decision the author made, say "I" when one person wrote the text
  and "we" when a team did, and keep to it, because a lone author writing "we"
  invents a team the reader cannot ask.
- B2. Use contractions where you would say them aloud, and expand them only in
  a formal warning or a legal statement, because text without them reads as a
  contract.
- B3. Give an instruction in the imperative, "Set the timeout", because "you
  should" and "you can" make a step sound optional.
- B4. Name the person who acted, "the reviewer asked", and cite the document or
  measurement a fact comes from, because "a decision was reached" hides who
  decided.
- B5. State the fact where you would judge the reader's effort: "Integration
  takes one call", in place of "simply integrate". Words such as simply, just
  and obviously tell a struggling reader the fault is theirs.
- B6. Replace filler and hype with the fact: robust, seamless, leverage,
  crucial and "it's worth noting" take the reader's time and give back nothing.
</rules>

<rules name="say it once">
- I1. Make every sentence add something the reader lacks, and carry the content
  in the fewest words it allows, because every word is paid for when it is
  written and again each time it is read.
- I2. Cut the frame announcing a claim, the sentence restating its neighbour,
  the paragraph introducing the next one, and the hedge with no doubt under it.
  Keep "because", "so" and "you", which carry the reasoning.
</rules>

<rules name="build sentences that read like speech">
- C1. Average about 20 words a sentence, stay under about 30, and set short and
  long ones side by side, because a run of short sentences reads as a
  proclamation and a forty-word one as a contract.
- C2. Write a claim plainly, without an inversion or an epigram, because a
  sentence that sounds like a proverb has usually lost its reason. Put the
  reason back into it.
- C3. Hedge with a stated condition, "This fails when a batch names two
  documents", because a bare "might" gives the reader nothing to check.
</rules>

<rules name="choose living words">
- D1. Turn the action back into a verb: "changing the record invalidates the
  cache", not "invalidation occurs on modification". A noun ending in -tion,
  -ment or -ity is often a verb in disguise that drops the actor.
- D2. Name the thing, a number or a limit, where you would name its category:
  mechanism, functionality, solution and approach say nothing on their own.
- D3. Use the most common word that is still exact, and the short word where
  one exists: "big" over "substantial", "fix" over "remediate", use, start,
  end, enough, help, show, about, send, get. Keep the long word when it is the
  technical name.
- D4. Write "how the parser validates its input" where a chain of "of"s would
  stand, because readers stall on the third one.
- D5. Write the sentence inside an empty frame as the whole sentence: "The
  loader fails in three cases", not "There are three cases in which the loader
  fails".
- D6. Keep to one participle a sentence, and split a sentence that stacks -ing
  clauses.
- D7. Use the name, not "it", once two sentences have passed or wherever two
  nouns could be the antecedent, because the pronoun has drifted from what it
  names.
- D8. Name the thing where you would write said, the given, the aforementioned
  or the respective.
- D9. Use a concrete comparison, "about 200 bytes", where a stock metaphor
  such as "under the hood" would tell the reader nothing.
- D10. Read the sentence aloud and rewrite it until you would say it to a
  colleague. This one test catches most of what the rules above describe.
- D11. Apply D1 to D8 in every language you write. In Russian that means
  `являться`, `осуществлять`, `данный`, `в рамках`, `с целью` and chains of
  genitives.
</rules>

<rules name="write for a second-language reader">
- H1. Use the plain verb where a phrasal verb is ambiguous: "configure" over
  "set up", "run" over "carry out".
- H2. Say it literally, without idioms, sayings or culture references, which
  cost a lookup and are often mistranslated.
- H3. State a thing positively and ask a question positively, because a double
  negative or a negative question has two readings.
- H4. Say what a modal means: "can" for permission, "might" for possibility,
  "must not" for a prohibition, because "may" and "should" each carry two
  senses.
- H5. Break a stack of more than two nouns into a phrase, because the reader
  cannot tell which noun modifies which.
- H6. Expand every acronym on first use, and write "for example", "that is" and
  "and so on" for the Latin abbreviations.
- H7. Write dates, times and numbers one way only: 2026-09-18, 14:30 CET, 1,500
  and 1500 ms.
- H8. Keep the subject and the verb close together, because a clause between
  them is where a reader loses the sentence.
</rules>

<rules name="format">
- F2. Use numbers for ordered steps, bullets for parallel items, a table for a
  comparison across two dimensions, and prose for everything else, including
  every argument, because a list strips out the "because" that joins its items.
- F3. Bold an interface element; put what the reader types or the machine reads
  in code font.
- F5. Write ASCII outside quoted code, because some readers' tools mangle
  anything else.
- F6. Use the serial comma, and leave an identifier or a protocol token in its
  own spelling.
</rules>

<rules name="code">
- G1. Write a comment only where the code cannot explain itself, and improve
  the name first, unless the name is an interface others depend on. Keep it
  short and plain, one line where one line will do, saying why the code does
  what it does, because the reader already has the code and needs the reason it
  doesn't show. Write nothing that restates the line below, because it goes
  wrong the first time that line changes. Delete commented-out code, since
  version control keeps it, and give every marker for later work an issue or a
  task, because a bare marker is a promise nobody owns.
- G2. Make an example runnable as pasted, with its prerequisites stated before
  it, keep only what the prose around it explains, comment a line that is not
  obvious, say so where you could not check it, introduce it with a sentence
  ending in a colon, tag its fence, and follow it with prose. A reader copies
  an example before reading the text around it, so it has to be right on its
  own.
</rules>

<rules name="short texts">
- S1. Write the subject in the imperative, naming one change, within the length
  the repository sets. Add a body only where the reason is not evident from the
  change, in two or three lines saying why, because the detail belongs in the
  pull request and the reasoning in the decision record.
- S2. Lead a pull request or issue with what the change does or what is broken,
  and link the record that authorises it. For a change, give what changed, the
  evidence that it works (the command, its exit status and its output), and
  what a reviewer should look at first. For a defect, give what you expected,
  what happened, and the smallest steps that reproduce it. Write these as
  paragraphs in that order, never under bold labels such as "**What
  changed**", because a label strips out the sentence that says why.
- S3. Name the line, what is wrong with it and what would fix it, and give the
  reason, so the author can fix it without asking you.
</rules>

<rules name="templates">
- E1. Follow a template where the repository or an installed unit ships one
  for the kind of text you are writing, a pull request or a document: a
  repository's own in `.meowpaw/templates/` first, then the owning unit's. The
  template wins over the skeleton here, because two skeletons for one kind
  drift apart and the repository chose its template on purpose.
</rules>

<rules name="edit">
- X1. Treat the author's facts as outranking your style when you edit somebody
  else's text. Name the main problem first: structure, voice, accuracy or
  completeness. Say what you changed and why before the result, leave alone
  what you were not asked to change unless it is wrong, flag a claim you cannot
  verify where you would delete it, and keep every reason, constraint and
  number from the source.
</rules>

<steps name="check before publishing">
1. Re-read the text against every rule here and in the files you read for it,
   and fix each place it breaks one.
2. Search for every word rules B5, B6, D2, D5 and D11 name, and for "there
   is", "in terms of" and "the fact that", and rewrite each hit.
3. If you read a patterns file, search for the markers each pattern there
   lists, and read for the patterns that list none. Fix each hit that matches
   the failing form, as the corrected form shows.
4. For a text over about 300 words, count the sentences over 35 words, and
   split all but one per thousand words, because reading aloud does not catch
   them.
5. For a text over about 300 words, count "rather than", "instead of" and
   ", not", and rewrite all but one per five hundred words with the reason the
   contrast was hiding.
</steps>
