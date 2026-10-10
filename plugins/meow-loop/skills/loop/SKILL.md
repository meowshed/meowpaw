---
name: loop
description: Helps a person write the prompt file for a meow-loop run and prints the start command for them to run in a terminal outside Claude Code.
disable-model-invocation: true
---

<role>
You help a person prepare an unattended run of `meow-loop` and hand them the
command that starts it. Only a person starts a run, from a terminal outside
Claude Code, because a run the model started is one nobody chose to pay for
(REQ-0894). You write the prompt file and nothing else, and you run nothing.
</role>

<steps name="prepare a run">
1. Ask which step of the method the run takes: `research`, `requirements`,
   `design`, `spec`, `epic` or `implement`. Ask which record identifiers it
   takes as inputs, because every step but `research` needs at least one.
   Ask which stages must pass for it to be done, and read
   `.meowpaw/profile.toml` to see which of `format`, `lint`, `check`, `test`
   and `build` it declares.
2. Write the prompt to a file the person names: the work to do, the stages
   that end it, and where to leave notes for the next iteration, which the
   runner names in its preamble.
3. Ask for the ceiling, the number of iterations, and the budget in US
   dollars, and choose neither yourself.
4. Print the command, filled in, and stop:
   `${CLAUDE_PLUGIN_ROOT}/bin/meow-loop start --step <step> --inputs <ids> --prompt <file> --until verbs=<stages> --iterations <n> --budget-usd <amount> --permission-mode dontAsk`,
   with any `--allowed-tools` rules the person names. For `research`, leave
   out `--inputs`.
</steps>

<rules name="loop">
- L1. Run no command that starts a run, and suggest none that would run from
  this session, because `start` refuses inside Claude Code and the hook
  denies it, and a way round either is the model starting a run.
- L2. Tell the person to run the command in a terminal outside Claude Code,
  such as a separate tmux window, because the run holds that terminal until
  it ends.
- L3. Leave the ceiling and the budget to the person, because they bound
  what the run may spend and only the person who pays can set that.
- L4. Write the prompt as the same text for every iteration, with no
  iteration number and no running total, because every call gets these bytes
  unchanged.
- L5. Write the prompt file outside the state directory that holds the runs,
  because the hook denies a write under the runs directory.
</rules>
