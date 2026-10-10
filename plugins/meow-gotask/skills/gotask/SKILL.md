---
name: gotask
description: The tasks Task (go-task) resolves in this repository and what each can safely do. It MUST be loaded before running, listing or binding a Task task, or a stage to one, in a repository with a Taskfile. It MUST NOT be used to trust a remote Taskfile.
---

<role>
You read what Task resolves in a repository through the pack's program, and
you report what it printed. A remote Taskfile runs a third party's code, and
trusting one is the person's decision and never yours.
</role>

<steps name="read the tasks">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-gotask status` and show its output.
2. If it exits 3, report the line starting `unresolved:` as it stands, with
   each remote include it named, and stop.
3. Otherwise report each task you are about to use with its origin and every
   line under it, because a blocked task and a task that can skip each prove
   less than a pass suggests.
</steps>

<rules name="tasks">
- G1. Never run `task --list` or `task --list-all` yourself, because Task
  writes a checksum when it lists, and the next run then skips a task that
  never ran; the program lists with its temporary directory moved away.
- G2. Never pass `--yes`, `--trusted-hosts`, `--download` or `--insecure`,
  because each answers a prompt meant for a person or lets a third party's
  code into the person's environment.
- G3. Never write an include whose `taskfile` names a URL or a `git::`
  source, because the project would then depend on a third party whenever a
  stage runs.
- G4. Treat a variable marked `secret: true` as unprotected, because Task
  masks it only in the command it echoes, and a command's own output still
  prints it.
- G5. Report a task that ignores errors, or runs only under `if` or
  `platforms`, as unable to show a failure, because it exits 0 whatever
  happened.
</rules>

<steps name="bind the stages">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-gotask bind` and show the table it
   prints, each unbound stage's reason included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and write
   the profile yourself only when they ask, because the profile is the
   repository's declaration.
3. After a profile's stages change, run
   `${CLAUDE_SKILL_DIR}/../../bin/meow-gotask check` and report every finding
   it prints, with its exit status.
</steps>
