---
id: ADR-2530
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2206, REQ-2208, REQ-2210, REQ-2212]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2530. The commit check holds the sign-off route, the trailers and the breaking mark

## Decision

`meow-scm check-message` gains three rules. The first `Signed-off-by` names
the commit's author, and each later one names someone the change passed
through, so the chain records the route and never a list of approvers
(REQ-2206). A trailer that names a person, such as `Co-authored-by`,
`Reviewed-by` or `Acked-by`, needs the person's permission, so the check fails
one the harness wrote unless the profile lists the person under
`[commits] may_name`. The trailers that record where something came from,
`Signed-off-by` by the author, `Cherry-picked-from` and `Fixes`, are exempt
(REQ-2208). A commit whose type the profile marks as breaking, or whose
subject carries `!`, must say what breaks in a `BREAKING CHANGE:` trailer
(REQ-2212).

Every commit that reaches the trunk leaves it green, because each pull
request lands as one squashed commit only after its gate passes on the
branch (REQ-2210). The `git` pack's push guard already refuses a push that
skips the trunk, and the code host's required checks hold the rest.

Once this is accepted, a message that misuses a trailer or hides a break fails
before it is used. What still doesn't work: the check reads the message and
can't know whether the person a trailer names agreed, so `[commits] may_name`
is the repository's own statement of it.

## Why

RES-0066 concluded that the sign-off chain records the route a change took and
approves nothing, that a trailer naming a person needs that person's
permission apart from the three that record provenance, that every commit on
the trunk leaves it buildable because a bisect lands on whichever one doesn't,
and that a breaking change is marked in the commit because nobody remembers
it at release time. ADR-1080 already checks a message against the convention
the repository declares, so these rules join that check.

## Alternatives

| Option                            | Better at     | Why it lost                                                     |
| --------------------------------- | ------------- | --------------------------------------------------------------- |
| Do nothing                        | No new rules  | A trailer naming a person can be written on their behalf        |
| Rules in the commit skill only    | No code       | A skill can't fail a message, and REQ-2208 must hold every time |
| Ban every trailer naming a person | Simplest rule | It blocks a co-author who did agree                             |

## What it costs

A repository that uses `Co-authored-by` for people has to list them under
`[commits] may_name`, which ADR-2370's table of profile keys must carry.

## What would reverse it

- A repository needs a trailer naming a person that the profile can't list in
  advance, such as a one-off contributor, and `may_name` blocks real work.

## Consequences

`meow-scm check-message` gains the three rules. ADR-2370's key table gains
`[commits] may_name`. The commit skill names the exempt trailers.

## How I will know it was realised

1. A message whose first `Signed-off-by` doesn't name its author fails the
   check (REQ-2206).
2. A message with a `Co-authored-by` for a person not under `may_name` fails
   (REQ-2208).
3. A subject with `!` and no `BREAKING CHANGE:` trailer fails (REQ-2212).
4. The trunk's history has no commit whose gate failed, because each landed
   through a pull request whose checks passed (REQ-2210).

## What this does not settle

- How a release reads the breaking mark, which ADR-1570 already decided.
