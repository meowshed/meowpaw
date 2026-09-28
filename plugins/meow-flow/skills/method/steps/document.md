<role>
The document step. It reads an epic whose tasks are all done, named by its
identifier, and writes from `paw template spec`. Its artifact lands in each
user-facing page it changed. The step that picks it up is verify.
</role>

<steps name="document">
1. Read `[docs] style` in `.meowpaw/profile.toml`: a path to the repository's
   style guide, or the name of an installed unit that ships one. Where it
   declares none, say so and write to the writing standard in force.
2. For each page the epic's change invalidated or needs, name its kind first:
   introduction, tutorial, how-to, reference, explanation or troubleshooting.
3. Bring the user-facing documentation into agreement with what the epic
   changed: pages, the index they are listed in, and any install or usage
   instruction the change invalidated.
4. Run every example you wrote or changed, as written, and run the
   repository's verbs. Report which verb checked the documentation, or that
   none did.
5. Report what you changed and what you deliberately left alone, with the
   reason, because an unreported silence reads as an omission.
</steps>

<rules name="document">
- O1. Bring the user-facing documentation into agreement with what the epic
  changed.
- O2. Report what you changed and what you deliberately left alone, and record
  the reason wherever documentation is left un-updated, because an unreported
  silence reads as an omission.
- O3. Don't report an epic finished while documentation its tasks invalidated
  is still published.
- O4. Name a page's kind before you write it, because the kind decides the
  page's shape, and choosing it afterwards means rewriting the page.
- O5. Keep each page to one kind, because a reference that editorialises fails
  the reader looking something up, and a tutorial that explains the design
  fails the reader learning a first task.
- O6. Give a how-to guide no justification, and link the explanation or the
  decision instead, because a reader following steps needs the next step, not
  the argument for it.
- O7. Organise pages around what the reader is trying to do, never around the
  shape of the source tree, because the reader arrives with a task and not
  with a map of the code.
- O8. Open the repository's introduction with what the project is, followed
  by a quick start that works, and no promotional material, because a reader
  deciding whether to use the project needs those two things first.
- O9. Take reference for a public interface from the verb that generates it
  from the interface's own documentation, and where no verb does, report the
  reference as written by hand and unchecked against the interface, because
  hand-written reference drifts from the interface it describes.
- O10. Write to the documentation style the repository declares, never a
  default of your own, because the style is the repository's decision.
- O11. Edit only documentation written for the project's users, never the
  epic, its tasks or any other record, because the record changes through its
  own steps.
- O12. Check documentation through the repository's verbs, report the verb
  that checked it or report it unchecked where none does, and never run a
  check of your own, because a check the repository didn't declare is a
  command you guessed.
- O13. Run every example you write or change as written, and mark one you
  couldn't run as not run, because a reader who follows a broken example
  blames their own setup and stops trusting the rest.
</rules>
