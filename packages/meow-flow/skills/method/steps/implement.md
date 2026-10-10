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
   implementation yet. Below the `Not yet.` that opens the task's
   `## Evidence`, name each criterion no program can check, and each with no
   `Closed by:` line, as resting on judgement with the reason.
3. Run the tests through `meow-checks`, or by the repository's own command
   where it isn't installed, and see each one fail, then commit them in a
   commit of their own, before any commit that implements the task.
4. Make the change the task describes and nothing no requirement describes,
   and see the tests pass. Where the work contradicts an approved requirement,
   stop and report it: the fix is an amendment reviewed on its own.
5. Bring the user-facing documentation the change invalidates into agreement
   with it, in the same pull request: its pages, the index they are listed in,
   and any install or usage instruction. Run every example you changed.
6. Run the repository's stages through `meow-checks`. Where `meow-checks` isn't
   installed, run each stage's command and note its exit status instead.
7. Where every stage passed, replace the `Not yet.` that opens the task's
   `## Evidence` with the tests that close each criterion, each stage's outcome
   and the pull request, mark the task `[x]` in its epic or defect in the same
   pull request, with one line of evidence, and stop there. A task naming
   `realises:` has no mark, and its Evidence closes it.
8. Where a stage didn't pass, leave `Not yet.` as the first line and the task
   unmarked, report what failed, and stop.
</steps>

<rules name="implement">
- I1. Read the task and every requirement it cites in full, not a summary of
  either, because a summary drops the clause the work turns on.
- I2. Halt when a task this one depends on has failed, and report without
  halting when a task running beside it has failed, because only the first
  leaves this one nothing to build on.
- I3. Implement no behaviour that no requirement describes, because behaviour
  nobody required is behaviour nobody reviewed.
- I4. Where the work contradicts an approved requirement, stop and write no
  code the requirement forbids; route it through an amendment stating the
  blast radius and the migration, which stops for approval as a change of its
  own, because a requirement bent in passing is one no reader sees change.
- I5. Before an amendment blames an artifact, check the check, because a
  failing check may be wrong about what it measures.
- I6. Where the work turns out to be uncovered by any requirement, stop and
  return to the requirements step, because work with no requirement closes
  nothing.
- I7. Claim the work done only with evidence: the tests that ran, each stage's
  result and the identifier of what it closes, because prose asserting
  success is not evidence.
- I8. Name in each test the requirement it proves, cover every requirement
  with a test that would fail if it were violated, check a failure path as
  precisely as its success path, and never cite coverage as evidence that a
  requirement is met, because a line run is not a behaviour checked.
- I9. Report outcomes faithfully, partial completion, skipped steps and checks
  that couldn't run included, because a report that leaves them out reads as
  a pass.
- I10. Keep the not-working states distinct and named, unresolved, tool
  absent, tool broken, untrusted, skipped and unreachable, because each calls
  for a different action.
- I11. Work from the parts the task touches and the dependencies it may use,
  as the specification states them, not from structure inferred from the file
  tree, because the tree shows what exists and not what is allowed.
- I12. Where the task's criteria predict a measurable outcome, check the result
  against the number they state and never restate the prediction, because a
  prediction written after the result fits it, and an approved task holds it
  frozen.
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
- I18. Name under the task's `## Evidence`, below its `Not yet.` and before
  the implementation starts, each criterion no program can check and each
  with no `Closed by:` line, as resting on judgement with the reason, because
  an unchecked criterion left unnamed reads as covered, and Evidence is the
  section an approved task may still change.
- I19. Keep no run output in the repository, in a file or in the task,
  because the first commit shows the tests failing and the gate shows them
  passing.
- I20. Mark the task done only in a change whose stages all passed, because a
  done mark without the gate closes its requirements on nothing.
- I21. Keep `Not yet.` as the first line of the task's Evidence until every
  stage has passed, because the program reads an Evidence that opens with
  anything else as a finished task, and a task naming `realises:` has no
  other mark.
- I22. Don't report the task finished while documentation it invalidated is
  still published, and record under the task's Evidence the reason wherever
  a page is left un-updated, because an unreported silence reads as an
  omission.
- I23. Edit only pages written for the project's users, and change the record
  only by the task's Evidence and its mark, because every other section of an
  approved task is frozen and every other record changes through its own
  step.
- I24. Write to the documentation style `[docs] style` declares in
  `.meowpaw/profile.toml`, never a default of your own, and where it declares
  none, say so and write to the writing standard in force, because the style
  is the repository's decision.
- I25. Name a page's kind before you write it, introduction, tutorial, how-to,
  reference, explanation or troubleshooting, and keep each page to one kind,
  because the kind decides the page's shape.
- I26. Give a how-to guide no justification, and link the explanation or the
  decision instead, because a reader following steps needs the next step, not
  the argument for it.
- I27. Organise pages around what the reader is trying to do, never around the
  shape of the source tree, because the reader arrives with a task and not
  with a map of the code.
- I28. Open the repository's introduction with what the project is, followed
  by a quick start that works, and no promotional material, because a reader
  deciding whether to use the project needs those two things first.
- I29. Take reference for a public interface from the stage that generates it,
  and where no stage does, report the reference as written by hand and
  unchecked against the interface, because hand-written reference drifts from
  the interface it describes.
- I30. Check documentation through the repository's stages, report the stage
  that checked it or report it unchecked where none does, and never run a
  check of your own, because a check the repository didn't declare is a
  command you guessed.
- I31. Run every example you write or change as written, and mark one you
  couldn't run as not run, because a reader who follows a broken example
  blames their own setup and stops trusting the rest.
</rules>
