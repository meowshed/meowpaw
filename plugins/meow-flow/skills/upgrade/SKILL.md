---
name: upgrade
description: Moves a repository's record from epics and tasks to the form where a decision or a defect is one issue and one pull request, in a pull request of its own, and retires the archived tasks' issues once that pull request has merged.
disable-model-invocation: true
---

<role>
You move a repository's record to the form the method now reads, and then its
issues, in two separate stops, because an issue that points at a plan not yet
on the trunk is a dead end. The commands make every change, and you show what
each will do and report what it did.
</role>

<steps name="upgrade the record">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/paw upgrade`, which only previews, and
   show its whole output. Where it reports nothing to upgrade and the
   trunk holds an archive of tasks, go to step 6. Where it reports that and no
   archive exists, say so and stop.
2. Stop until the person agrees to the preview.
3. Take a branch from the trunk. Run `${CLAUDE_SKILL_DIR}/../../bin/paw count`,
   `${CLAUDE_SKILL_DIR}/../../bin/paw upgrade --write`, and
   `${CLAUDE_SKILL_DIR}/../../bin/paw count` again, then
   `${CLAUDE_SKILL_DIR}/../../bin/paw check`. Where the check reports a finding,
   report it with the two counts and stop. The first count holds no task or
   epic, because the old directories aren't kinds any more, so the totals the
   preview printed stand for them.
4. Report each task folded and the record now carrying it, each orphan as
   "needs a decision", and each template under `.meowpaw/templates/` to remove.
5. Commit the result and open one pull request holding both `paw count`
   outputs. Name it, say that the issues change only after it merges, and stop.
   Where the repository declares no code host, name the branch in its place.
</steps>

<steps name="retire the issues">
6. Confirm that the record's upgrade is on the trunk, and stop where it isn't.
   Where the `meow-github` command doesn't exist, or `[tracker] kind` is not
   declared, report this stage as not run and stop.
7. Where `meow-github` exists, run `meow-github upgrade --check` and show its whole output, with each open
   pull request it lists and each task that needs a decision.
8. Stop until the person agrees to that output.
9. Where `meow-github` exists, run `meow-github upgrade`, report each line it printed, and commit the
   `issue:` and `projected:` it wrote on each record in a pull request of its
   own, because a mapping lost here opens a second issue. Name that pull
   request and stop.
</steps>

<rules name="upgrade">
- U1. Change nothing before the person agrees to the preview, and take neither
  agreement from the other stop, because the first changes the tree and the
  second writes to issues other people read.
- U2. Run `paw upgrade --write` on a branch and never on the trunk, because the
  record change has to land in a pull request a person can read.
- U3. Where `meow-github` exists, run `meow-github upgrade` only after that pull request has merged, and
  never in the same stop as `paw upgrade --write`, because a closed issue naming
  a plan that was never merged is a dead end.
- U4. Where `meow-github` exists, list each open pull request `meow-github upgrade --check` names and change
  none of them, because those branches are somebody's work: they rebase, and
  move their plan to the record by hand.
- U5. Leave an orphan in the archive and report it as "needs a decision", and
  write no decision for it here, because no live record authorises its work and
  that choice is a person's.
- U6. Report a template under `.meowpaw/templates/` for a retired kind and leave
  it in place, because it is the repository's own file.
- U7. Edit no archived file and no plan step by hand during the upgrade, because
  the two `paw count` outputs prove nothing about a tree edited beside the
  program. A decision the preview reports as needing a plan is the exception:
  write its plan in that pull request, because the check refuses it without one.
</rules>
