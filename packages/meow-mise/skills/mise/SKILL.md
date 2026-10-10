---
name: mise
description: The tasks mise resolves in this repository and what each can safely do. It MUST be loaded before running, listing or binding a mise task or a stage to one in a repository with a mise.toml or a mise task directory. It MUST NOT be used to trust a configuration.
---

<role>
You read what mise resolves in a repository through the pack's program, and
you report what it printed. mise guards a repository's configuration with a
trust boundary, and a harness reading somebody else's repository is what that
boundary exists to stop, so trusting a configuration is the person's decision
and never yours.
</role>

<steps name="read the tasks">
1. Run `meow-mise status` and show its output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop. For `untrusted`, give the person the command it names and let them
   run it after reading the configuration.
3. Otherwise report each task you are about to use with its origin and every
   line under it: a task from `outside` or `work tree only`, a replaced task,
   and a blocked task each say why a result from it proves less.
</steps>

<steps name="bind the stages">
1. Run `meow-mise bind` and show the table it
   prints, each unbound stage's reason included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and write
   the profile yourself only when they ask, because the profile is the
   repository's declaration.
3. After a profile's stages change, run
   `meow-mise check` and report every finding it
   prints, with its exit status.
</steps>

<rules name="tasks">
- K1. Never run `mise trust`, never pass `--yes` or set `MISE_YES`, and never
  add a path to `MISE_TRUSTED_CONFIG_PATHS`, because each authorises code
  that came with the repository to run in the person's environment.
- K2. Never write `mise.local.toml`, because it is the person's own file and
  isn't committed.
- K3. Report an untrusted configuration as untrusted, never as a repository
  with no tasks, because the two look alike and mean opposite things.
- K4. Run no task marked `asks for a person` without a person present, and
  none marked `needs` without the arguments it names, because its author
  asked for both.
- K5. Report a task marked `can skip as fresh` that passed without `--force`
  as possibly skipped, because mise exits 0 on a task it didn't run.
</rules>
