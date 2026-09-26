<role>
The implement step. It reads an approved task, named by its identifier, and writes from `meow-method template task`. The step that picks
it up is document.
</role>

<steps name="implement">
1. Read the task and every requirement it cites in full, not a summary.
2. Make the change the task describes and nothing no requirement describes.
   Where the work contradicts an approved requirement, stop and report it:
   the fix is an amendment reviewed on its own.
3. Write a check for each requirement the task closes, seen failing first
   against a version that doesn't do the work, so the check can fail.
4. Run the repository's verbs through `meow-verbs`, and record the command,
   its exit status and its output under `## Evidence`.
5. Mark the task `[x]` in its epic in the same change, with one line of
   evidence.
</steps>
