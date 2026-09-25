---
name: verify
description: The five verification verbs for this repository, fmt, lint, typecheck, test and build. It MUST be loaded before any code is formatted, linted, type-checked, tested or built, including a single test file and a quick check before a commit. It MUST NOT be skipped, however obvious the command looks, and no command is run in its place.
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
2. Run the verbs the work needs, naming each one:
   `${CLAUDE_SKILL_DIR}/../../bin/meow-verbs run test`, or several at once,
   such as `run fmt lint test`. Never run a verb's command yourself, and never
   run a command you chose in place of an unresolved verb.
3. Report each verb as the program reported it: passed, failed or
   unresolved. For a failed verb, lead with its last lines of output and name
   the file and line where they point. For an unresolved verb, give its kind.
4. Where a verb the work needs is unresolved, tell the person how to declare
   it, and stop there. Stop, because only the repository knows what the verb
   means for it.
</steps>

<rules name="reporting">
- V1. Call the work done only when every verb it needs passed, or when the
  person has said they accept a verb that failed or stayed unresolved, because
  a claim of done over a failing check is the substitution this unit exists to
  stop.
- V2. Report the program's exit status beside its summary: 0 when every named
  verb passed, 1 when one failed and 3 when one was unresolved.
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
