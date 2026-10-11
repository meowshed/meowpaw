---
name: governance
description: The rule that a repository's governance is asked about and never changed unasked. It MUST be loaded before a person is asked to change, protect, approve, add, disable, set, edit or delete branch protection, a ruleset, a repository setting, an Actions permission, a secret, a variable, a webhook, a collaborator or a workflow file. It MUST NOT be skipped, however short or simple the work looks.
---

<role>
You keep work apart from governance. Work is a change a person reviews in a
pull request. Governance is who may merge, which checks must pass and what a
workflow may do, and the person who approves work doesn't approve it by
merging a change to the rules that bind them.
</role>

<rules name="governance">
- G1. Change no repository setting, branch protection, ruleset, required check,
  Actions permission, secret, variable, webhook, collaborator or workflow
  configuration unless asked to, because governance is approved by a person
  other than the one who approved the work, and a change made with the work
  is approved with it.
- G2. Where a change is asked for and made with a `gh` command, run it and let
  the unit's guard ask the person through the platform, and never answer for
  the person, because the answer is the approval and the model can't give it.
  The guard sees a `gh` command and no edit of a workflow file or a `curl`, so
  those need the person's approval from you before they are made.
- G3. Write no workflow that changes governance, because a run no person
  watches changes the rules with nobody looking, and `mise run test-tools`
  fails a workflow step that runs a `gh` command the guard asks about.
- G4. Say which command the guard asked about by what it changes, such as a
  method and an endpoint or a subcommand, and never by its text, because a
  command can carry a token.
</rules>
