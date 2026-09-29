---
name: write
description: How a skill, agent definition, output style, command or hook prompt for Claude Code is written in this repository. It MUST be loaded before any of them is created, edited or reviewed, including a one-line change to a skill's description. It MUST NOT be skipped, however small the change looks.
---

<role>
You write material Claude Code loads: skills, agent definitions, output
styles, commands and the prompts inside hooks. The model that reads it follows
what it says literally, so every rule states its reason and every procedure
states where it stops.
</role>

<steps name="write material">
1. Decide what the material is: knowledge the model loads, an action a person
   invokes, or a long read that ends in a short answer.
2. Write its front matter: what it is for and when to load it, and the
   invocation, paths and context its kind needs. For an agent, write the six
   fields D3 to D8 name.
3. Write the body in the five tags, `<role>`, `<rules>`, `<steps>`,
   `<example>` and `<input>`, with every obligation a numbered list item under
   `<rules>` and every file it relies on named in the core.
4. Where the material adds to what loads on every turn, run
   `${CLAUDE_SKILL_DIR}/../../bin/meow-author cost`, and before cutting or
   keeping a unit, read its use in `/skill-doctor`.
5. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-author check` on the directory you
   wrote in, fix each line it names, and stop when it passes.
</steps>

<rules name="what a unit declares">
- A1. Give every skill and agent a description of what it is for and when to
  load it, because the model chooses what to load from that line alone.
- A2. Write a command as a skill only a person invokes, with
  `disable-model-invocation: true`, and ship no `commands/` directory,
  because two kinds of loadable unit give the next author two places to look.
- A3. Let only a person invoke material with side effects, and only the model
  load material that is knowledge, because the model must not act unasked and
  a person gains nothing by invoking a rule.
- A4. Declare `paths` for material that applies to one language or one
  directory, because loading it everywhere costs every other session.
- A5. Run material whose work is a long read ending in a short answer in a
  forked context, so the reading stays out of the context that continues.
- A6. Keep anything injected when the material loads cheap and certain, never
  running a verification verb, and never let the material depend on it,
  because a failing injection fails every load.
- A7. Rely on the platform's namespacing of a plugin's skills for every
  command, and claim no bare name, because a bare name lasts only until
  something else claims it.
- A8. Propose the permissions the material needs on its page, and leave the
  repository to declare them, because permissions are the repository's
  decision.
</rules>

<rules name="how the body is written">
- B1. Use only the five tags, none inside another and each closed, with no
  Markdown heading, because a heading or a new tag is structure the next
  author reinvents differently.
- B2. Use tags where the material mixes kinds of content, and not as
  decoration around a single instruction, because a tag tells the model which
  kind of content it is reading.
- B3. Put every obligation in a numbered item under `<rules>`, led by an
  identifier, because an obligation elsewhere can't be extracted, checked or
  cited.
- B4. End every procedure at a named stopping point, because a model with no
  stopping point keeps going.
- B5. Show the failing case beside the corrected one wherever the material
  teaches a judgement, because a judgement shown only right is learnt as a
  rule of thumb.
- B6. Name every supporting file in the core with when to read it, and reach
  it through `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`, because a file
  nothing names is never loaded and a fixed path breaks wherever the unit is
  installed.
- B7. Say whether a script is run or read, and never summarise in prose a
  script that is run, because a summary drifts from the script it describes.
- B8. Write instructions in the words of the work they govern, because the
  model retrieves an instruction by the words a request uses.
- B9. Keep the form uniform with every other unit's, so one check audits all
  of them.
</rules>

<rules name="when material loads">
- C1. Load material needed only once a capability is chosen at that point, and
  not before, because material loaded early costs every turn that never
  chooses it.
- C2. Load material for an unusual case only in that case, and never carry it
  in material that is always loaded, because the common case pays for it
  otherwise.
- C3. Express one capability as one skill, not several overlapping ones,
  because invoking an overlapping set loads every body in it.
- C4. Keep each skill to one discipline, and split one that spans two,
  because a skill spanning two is loaded whole for either.
- C5. Give a rule its reason beside it where the rule is counter-intuitive or
  the model's default is wrong, and otherwise keep the reason in material
  loaded on demand, because an always-loaded reason is paid on every turn.
- C6. Measure a change that moves explanation out of always-loaded material,
  with and without it, before shipping it, because a shorter prompt that
  changes behaviour is a regression and no saving.
- C7. Carry instruction that applies only to certain files in a path-scoped
  rule, not in always-loaded material, because a path-scoped rule loads only
  when those files are touched.
- C8. Count splitting always-loaded material into imported files as no
  saving, because the platform expands imports at launch.
- C9. Load nothing because it might be relevant, because a nearly relevant
  unit distracts the model and costs its context.
- C10. Put no obligation in a file the model reads at its own discretion,
  because an obligation it may skip is one it will skip.
- C11. Put mutually exclusive branches of an instruction in separate files,
  because a file holding both loads both whenever either is needed.
</rules>

<rules name="agents and delegation">
- D1. Ship knowledge, such as a lens or a language's idioms, as a skill loaded
  into the working context and never as an agent, because knowledge needs no
  isolation and an agent pays for a fresh context and a summary on every
  dispatch.
- D2. Never describe a delegated agent as a boundary that contains what it
  does, because it runs in the parent's process and under the parent's
  sandbox configuration.
- D3. Declare `maxTurns` as a positive integer, because it is the ceiling the
  runner enforces, and an agent without one runs until the work or the
  session ends.
- D4. Write `tools` out as a list, `tools: []` included, and in an agent a
  unit ships list no `*`, `Agent` or `Task`, alone or restricted such as
  `Agent(worker)`, because a missing list and `*` both grant every tool, the
  delegation tool among them, and the platform still takes `Task` as the
  earlier name of `Agent`.
- D5. Name `model` as `sonnet`, `opus`, `haiku`, `fable` or a full identifier
  containing `claude-`, never `inherit`, because `inherit` leaves the model,
  and so the cost, to whichever session dispatches the agent.
- D6. Name `effort` as `low`, `medium`, `high`, `xhigh` or `max`, because a
  missing one runs at the session's level, a cost nobody chose, and those
  five are the levels the platform documents.
- D7. Write `omitClaudeMd` out, `false` where the agent judges against the
  repository's rules and `true` where it judges against a standard it
  preloads, because the platform honours only `true`, so a missing key loads
  the project's instructions exactly as `false` does and only a written value
  shows somebody decided.
- D8. List in `skills` the skills the agent preloads, and write `skills: []`
  where it needs none, because the list decides what the agent loads at
  startup and grants nothing, so an empty one states that nothing is needed.
- D9. Where you dispatch an agent, read an output marked partial, stopped at
  its ceiling, as unfinished work, and read any output of a run that reached
  its ceiling the same way until a run has shown the marking, because a
  partial list of findings reads as a complete one.
</rules>
