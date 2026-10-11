---
name: governance
description: Why a change to how a repository is governed is asked and never made unasked. It MUST be loaded before branch protection, a ruleset, a repository setting, an Actions permission, a secret, a variable, a webhook, a collaborator or a workflow file is changed. It MUST NOT be skipped, however small the setting looks.
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
- G2. Where a change is asked for, run its `gh` command and let the unit's
  guard ask the person through the platform, and never answer for the person,
  because the answer is the approval and the model can't give it.
- G3. Write no workflow that changes governance, because a run no person
  starts changes the rules with nobody looking, and `mise run test-tools`
  fails a workflow that does.
- G4. Say which command the guard asked about, by its method and endpoint and
  never its text, because a command can carry a token.
</rules>
