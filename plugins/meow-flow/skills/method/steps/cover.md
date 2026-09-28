<role>
The cover step. It reads an approved task, named by its identifier, and writes
the task's checks before any of its implementation. Its artifact lands in the
check files, the kept failing run, and the task file's `## Cover`. The step
that picks it up is implement.
</role>

<steps name="cover">
1. Run `paw ready cover <task>`, and stop where it refuses the task.
2. Read the task and every requirement it cites in full, not a summary.
3. Write a check for each acceptance criterion a program can settle, naming
   in each check the criterion and the requirement it proves, and write no
   implementation code.
4. Run the checks through `meow-verbs` and see each one fail, because a check
   that passes before the work exists can't show the work was done.
5. Keep that failing run with `meow-verbs evidence --keep`, and cite the kept
   path.
6. Land the checks in a change of their own, before any of the
   implementation.
7. Fill the task's `## Cover` section in its four lines, replacing `Not yet.`,
   and stop there:

```text
- Checks: <the path of each check file, or none>
- Failing run: <the path of the kept run in which they failed, or none>
- Landed in: <the pull request, or the commit where nothing squashes, that carried the checks, or none>
- Judgement: <for each criterion no program can check, its number, a colon and the reason, separated by semicolons; or none>
```

</steps>

<rules name="cover">
- C1. Write checks and never implementation code, because a check written
  beside the code it tests is shaped by that code and misses its faults.
- C2. Name under `Judgement` each criterion no program can check, with the
  reason, because an unchecked criterion left off the list reads as covered.
- C3. Leave `Failing run` and `Landed in` as none only where `Checks` is none
  and `Judgement` names every criterion, because then nothing ran and nothing
  landed.
</rules>
