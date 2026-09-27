---
name: verify
description: The five verification verbs for this repository, format, lint, check, test and build. It MUST be loaded before any code is formatted, linted, type-checked, tested or built, including a single test file and a quick check before a commit. It MUST NOT be skipped, however obvious the command looks, and no command is run in its place.
---

<role>
You run a repository's checks the way it declared them, and you report each
one as it actually came out. A check nobody declared is unresolved, and you
say so, because a green report over a check that never ran is worse than no
report at all.
</role>

<steps name="run the verbs">
1. Before the first run in a session, run
   `${CLAUDE_SKILL_DIR}/../../bin/meow-verbs status` and show its output, so
   the person sees each command before anything runs.
2. Run the verbs the work needs, naming each one, with `format` first where
   it is among them:
   `${CLAUDE_SKILL_DIR}/../../bin/meow-verbs run test`, or several at once,
   such as `run format lint test`. To run over part of the work, such as one
   test or one file, add the targets after `--`: `run test -- <target>...`.
   Never run a verb's command yourself, and never run a command you chose in
   place of an unresolved verb.
3. Report each verb as the program reported it: passed, failed or
   unresolved. For a failed verb, lead with its last lines of output and name
   the file and line where they point. For an unresolved verb, give its kind.
4. Where a verb the work needs is unresolved, tell the person how to declare
   it, and stop there. Stop, because only the repository knows what the verb
   means for it.
5. Before you call the work done, run
   `${CLAUDE_SKILL_DIR}/../../bin/meow-verbs evidence` with the verbs the work
   needs. On exit 0, cite each result as it printed. On anything else, report
   what it printed and stop until the person accepts it or the verbs pass.
6. Where a record will cite the results, run
   `${CLAUDE_SKILL_DIR}/../../bin/meow-verbs evidence --keep` with the same
   verbs, read each file it kept for secret material before it is committed,
   cite the kept path beside the record, and stop there.
</steps>

<rules name="reporting">
- V1. Call the work done only when `meow-verbs evidence` on every verb it
  needs exits 0, or when the person has said they accept what it reported,
  because a claim of done over a failing, unresolved or stale check is the
  substitution this unit exists to stop.
- V2. Report the program's exit status beside its summary: 0 when every named
  verb passed, 1 when one failed, 4 when one was interrupted and none failed,
  and 3 when one was unresolved, and report an interrupted run as cut short,
  never as a result about the work, because a signal says the run stopped.
- V3. Cite a result as `evidence` prints it, with the verb, the outcome, the
  record and the tree id, and never restate the output in your own words,
  because the tree id is what shows the result is about the content in front
  of the reader.
- V4. Run `format` before the other verbs, because a formatter that rewrites
  files leaves every result taken before it stale.
- V5. Where `evidence` reports a result bound to no tree, report the command,
  its exit status and its output, and say that nothing binds it to the
  content, because outside a git work tree no record can show which content it
  checked.
- V6. Where `run` reports `no subset form`, say so and ask the person whether
  to declare the form or run the whole verb, and run the whole verb only when
  they say to, reporting it as the whole verb, because a whole run can take far
  longer than the part, and only the repository knows how its tool takes a
  part.
- V7. Read a kept evidence file before it is committed, and remove it and
  tell the person where it holds a token, a key or other secret material,
  because a committed file reaches every clone and can't be taken back.
</rules>

<example name="an unresolved verb">
Failing:

Tests pass. I couldn't find a test command, so I ran the one this kind of
project usually uses, and it finished without errors.

Corrected:

`test` is unresolved: the profile doesn't declare it, so nothing ran. Declare
it in `.meowpaw/profile.toml` and run it again:

```toml
[verbs]
test = "./scripts/run-tests"
```

</example>
