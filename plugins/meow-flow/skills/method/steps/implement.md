<role>
The implement step. It reads an approved task, named by its identifier, and
writes the whole task in one pull request: its tests first, then the change,
the documentation the change invalidates, and the record marks. Its artifact
lands in the test files, the changed files, each user-facing page it changed
at the page's own path, and the `## Evidence` of `tasks/TSK-NNNN-<slug>.md`
under the record root, `[record] root` in `.meowpaw/profile.toml` or
`project/` where it declares none. The step that picks it up is review.
</role>

<steps name="implement">
1. Read the task and every requirement it cites in full, not a summary.
2. Write at least one test for each acceptance criterion a program can check,
   naming in each the criterion and the requirement it proves, and write no
   implementation yet.
3. Run the tests through `meow-verbs` and see each one fail, then commit them
   in a commit of their own, before any commit that implements the task.
4. Make the change the task describes and nothing no requirement describes,
   and see the tests pass. Where the work contradicts an approved requirement,
   stop and report it: the fix is an amendment reviewed on its own.
5. Bring the user-facing documentation the change invalidates into agreement
   with it, in the same pull request, written to the style `[docs] style`
   declares in `.meowpaw/profile.toml`, and run every example you changed.
6. Run the repository's verbs through `meow-verbs`, and write under the task's
   `## Evidence` the tests that close each criterion, each verb's outcome and
   the pull request. Where `meow-verbs` isn't installed, record the command,
   its exit status and its output instead.
7. Mark the task `[x]` in its epic or defect in the same pull request, with
   one line of evidence, and stop there. A task that realises a decision
   directly has no mark, and is done by its Evidence.
</steps>

<rules name="implement">
- I1. Read the task and every requirement it cites in full, not a summary of
  either.
- I2. Halt when a task this one depends on has failed, and report without
  halting when a task running beside it has failed.
- I3. Implement no behaviour that no requirement describes.
- I4. Where the work contradicts an approved requirement, stop and write no
  code the requirement forbids; route it through an amendment stating the
  blast radius and the migration, which stops for approval as a change of its
  own.
- I5. Before an amendment blames an artifact, check the check, because a
  failing check may be wrong about what it measures.
- I6. Where the work turns out to be uncovered by any requirement, stop and
  return to the requirements step.
- I7. Claim the work done only with evidence: the tests that ran, each verb's
  result and the identifier of what it closes, because prose asserting
  success is not evidence.
- I8. Name in each test the requirement it proves, cover every requirement
  with a test that would fail if it were violated, check a failure path as
  precisely as its success path, and never cite coverage as evidence that a
  requirement is met.
- I9. Report outcomes faithfully, partial completion, skipped steps and checks
  that couldn't run included.
- I10. Keep the not-working states distinct and named, unresolved, tool
  absent, tool broken, untrusted, skipped and unreachable, because each calls
  for a different action.
- I11. Work from the parts the task touches and the dependencies it may use,
  as the specification states them, not from structure inferred from the file
  tree.
- I12. Where the task predicts a measurable outcome, write the predicted number
  under Acceptance criteria before the work starts, because a prediction
  written after the result fits it, and an approved task holds it frozen.
- I13. Begin a task a defect authorises by running the defect's reproduction
  and seeing it fail, because a fix proven against a reproduction never seen
  failing proves the defect was never there.
- I14. Treat a defect's task as restoring a requirement already in force, and
  write no new decision for it, because the decision was made and the system
  disagrees with it.
- I15. Write no defect record for a defect a gate caught and the same change
  closed, and write one for every other defect, because the failing check and
  the commit already hold the first one's evidence, and nothing holds the
  second's reasoning.
- I16. Write the tests before the code they test, because a test written
  beside the code is shaped by that code and misses its faults, and a test
  that passed before the work existed can't show the work was done.
- I17. Never modify, delete, skip or weaken a test written first, except in a
  commit of its own whose message says why the test was wrong, because
  weakening a test is the cheapest way to make it pass.
- I18. Name in the task each criterion no program can check as resting on
  judgement, with the reason, before the implementation starts, because an
  unchecked criterion left unnamed reads as covered.
- I19. Keep no run output in the repository, because the first commit shows
  the tests failing and the gate shows them passing.
- I20. Report what documentation you changed and what you left alone with the
  reason, and edit only pages written for the project's users, because an
  unreported silence reads as an omission.
- I21. Name a page's kind before you write it, introduction, tutorial, how-to,
  reference, explanation or troubleshooting, and keep each page to one kind,
  because the kind decides the page's shape.
- I22. Check documentation through the repository's verbs and report it as
  unchecked where none covers it, never by a check of your own, because a
  check the repository didn't declare is a command you guessed.
</rules>
