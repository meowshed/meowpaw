---
id: TSK-1290
artifact: task
status: approved
revised: 2026-09-24
epic: EPC-1040
closes: [REQ-0158]
issue: 111
---

# Put the verbs in front of the model, and use them here

One task, one branch, one pull request, one review.

## What to do

Write `plugins/meow-verbs/skills/verify/SKILL.md` in the form SPC-1030 states,
with a description in the obligation form ADR-1050 gives: it MUST be used to
format, lint, type-check, test or build, in place of any command the model
would otherwise choose (REQ-0158). Its body runs `status` before the first
`run` in a session and reports each verb with the kind of result the program
gave. It names no language, tool or file extension.

Add the unit's `budget.toml`, its documentation page in `docs/` and its entry
in `.claude-plugin/marketplace.json` and `docs/README.md`.

Declare this repository's verbs in `.meowpaw/profile.toml`: `fmt` and `lint`
for the checks `mise run all` runs, and `test` for the record's own checks and
the fixtures TSK-1280 writes. Leave `typecheck` and `build` undeclared.

## Depends on

TSK-1280, because the skill calls the program and the profile is read by it.

## Evidence

The skill `meow-verbs:verify` carries its description in the obligation form
ADR-1050 gives, at 332 characters, and names no language, tool or file
extension. The unit's budget is 450, its page is `docs/meow-verbs.md`, it is in
the marketplace at 0.2.0, and this repository declares `fmt`, `lint` and
`test` in `.meowpaw/profile.toml`:

```text
$ plugins/meow-verbs/bin/meow-verbs status
fmt        resolved    mise run fmt-check   (from .meowpaw/profile.toml)
lint       resolved    mise run lint && mise run style && ...   (from .meowpaw/profile.toml)
typecheck  unresolved  undeclared: the profile doesn't name it
test       resolved    python3 -m unittest discover -s plugins/meow-verbs/tests && ...
build      unresolved  undeclared: the profile doesn't name it

$ plugins/meow-verbs/bin/meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
exit 0
```

The first run of the same three failed `fmt` and `lint` on the new page, with
the exact findings in their output, before the page was formatted: the verbs
reported a real failure as a failure.

Asked "Run the tests." on Sonnet 5 with this unit alone installed, the model
loaded `meow-verbs:verify`, ran `meow-verbs status`, then `meow-verbs run
test`, and reported "`test` passed, exit status 0", adding that `typecheck` and
`build` are unresolved and nothing ran for either. It ran no command of its
own. REQ-0158 is closed.

## Left alone

Measuring the skill's routing on both models, which waits with the other
evaluations the owner postponed.
