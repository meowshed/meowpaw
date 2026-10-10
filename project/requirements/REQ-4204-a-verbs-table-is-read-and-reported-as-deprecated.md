---
id: REQ-4204
artifact: requirement
topic: stage-term
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0344
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4204

A profile that declares the five under a `[verbs]` table MUST still resolve
them, with a report that names `[stages]` as the table to use, until the second
release after the one that adds `[stages]`.

A repository's profile is a file the harness doesn't own, so a release that
stopped reading `[verbs]` would leave every unresolved stage reported as
unresolved on a repository that changed nothing (the repository's two-release deprecation rule).
