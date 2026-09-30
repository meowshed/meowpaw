---
id: BUG-1380
artifact: bug
status: approved
severity: minor
violates: REQ-3656
enters: implement
found: 2026-09-30
revised: 2026-09-30
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The method skill names nobody to open the one pull request

On the one-pull-request path the method skill tells a session to stop at the
pull request and never says who opens it. A session that stops with the
records on a branch and no pull request has stopped at nothing a person can
merge.

## Reproduction

`meow-flow` 0.46.0 at the commit of #768 on `main`, on 2026-09-30. Read
`plugins/meow-flow/skills/method/SKILL.md`, steps 7 and 8 and rules M20 and
M21, and search them for who opens the pull request:

```bash
grep -n -i "open" plugins/meow-flow/skills/method/SKILL.md
```

## What the system does

M20 says to "stop once, at that pull request", and step 8 says "the gate is
the pull request". Neither says the session opens it, and neither says what
to do in a repository with no code host. The search prints no line about a
pull request.

## What it should do, and why

The skill says the session opens the pull request and names it in its report,
and that where the repository declares no code host it names the branch in
its place, because REQ-3656 puts the one stop at the pull request, and a
stop before one exists leaves the person a branch to find and a request to
open by hand.

## Triage

It enters at implement, because the requirement is right and the prompt
leaves its last act unstated. Minor, because a person who sees no pull
request asks for one.

## Closed by

Not closed.

## Tasks

- [ ] T-001 TSK-4010 say who opens the pull request, in
      `plugins/meow-flow/skills/method/SKILL.md`
