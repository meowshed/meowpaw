---
name: change
description: The rules for every change to code in this repository. It MUST be loaded before any code is edited, written, refactored or deleted, including a one-line change, and before any test or other check is written. It MUST NOT be skipped, however small or obvious the change looks.
---

<role>
You change code the way a careful reviewer would want to read the change: the
smallest one that is correct, made with the most precise edit available, and
proven by a check that could have failed. A change that is larger, noisier or
proven by a check that couldn't fail costs every reader after you.
</role>

<steps name="change code">
1. Read each file before you write to it, and batch the reads that don't
   depend on each other.
2. For a question about a symbol, ask the language server where the session
   offers one; otherwise search the text and say what the search can't cover.
3. Make the smallest change that is correct, with the most precise edit the
   session offers: semantic for a symbol, structural for a mechanical rewrite,
   textual only for a literal.
4. After each edit, read the file's diagnostics before you claim anything
   about it.
5. Prove the change with a check that fails without it, take the evidence
   from the repository's verification verbs, and stop when they pass.
</steps>

<rules name="changing code">
- E1. Make the smallest change that is correct, because every line beyond it
  is one a reviewer has to read and rule out.
- E2. Read a file before you write to it, because an edit made from memory of
  a file overwrites what changed since.
- E3. Ask a language server about a symbol where the session offers one, and
  where an answer comes from a text search, say what the search can't cover,
  such as a name built at run time, because a search reports matches and not
  uses.
- E4. Prefer a semantic edit for a symbol, a structural edit for a mechanical
  rewrite and a textual edit only for a literal, and make a change one
  structural edit can express as that one edit, because a textual edit to a
  symbol misses the uses that don't match its text.
- E5. Batch reads and edits that don't depend on each other, because each
  round trip costs time and context for nothing.
- E6. Read a file's diagnostics after editing it and before claiming anything
  about it, and take evidence from the verification verbs, never from the
  diagnostics, because diagnostics say a file parses, not that the work is
  done.
- E7. Never reformat while changing behaviour, because in the diff a
  reformatted line and a changed one look the same.
- E8. Document every declaration another module or a user can reach, and
  prefer an example the language runs as a check where it runs them, because
  a documented example that runs is the only comment a check can fail.
</rules>

<rules name="writing a check">
- C1. Check an obligation statically where you can, behaviourally where you
  can't, and by evaluation only where neither is possible, because each step
  down costs determinism.
- C2. See a check fail before the work that makes it pass, where the language
  and the pack support it, because a check never seen failing may not be able
  to.
- C3. Report a weak or tautological assertion as a defect in the check, such
  as one that compares a value with itself, because it passes whatever the
  code does.
- C4. Rewrite a check that wouldn't fail if its requirement were violated, and
  never add a second check beside it, because the first goes on passing for
  the wrong reason.
- C5. Where the ecosystem provides mutation testing, run the tool the
  repository or a pack names when asked whether the checks would catch a
  change, and report each surviving mutant; where nothing names a tool, say
  how to declare one and run nothing in its place, because a guessed tool's
  silence reads as a pass.
</rules>
