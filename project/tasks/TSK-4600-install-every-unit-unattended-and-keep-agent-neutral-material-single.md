---
id: TSK-4600
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2500
closes: [REQ-1486, REQ-1490, REQ-1492]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Install every unit with no person, and keep agent-neutral material written once

A provisioning script installs every unit by the platform's own commands, a
test proves it in a scratch configuration directory, and a test holds that no
unit keeps a copy of its material for a second agent, as SPC-1080 states under
"Each unit is a plugin" and SPC-1030 under "How a unit divides its material".
One task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a scratch configuration directory and this checkout's
   `.claude-plugin/marketplace.json`, when the test runs
   `claude plugin marketplace add` and `claude plugin install <unit>@meowpaw`
   for every unit with no input on standard input, then the platform lists
   each unit as enabled, and a unit left out of the install fails the test
   (REQ-1486). Closed by: a test under `tools/` naming REQ-1486, seen failing
   first.
2. Given a machine with no `claude` command on the path, when that test runs,
   then it reports itself skipped with that reason, and never passed. Closed
   by: the same test run with `PATH` stripped of the command.
3. Given `docs/README.md`, when a reader looks for an unattended install, then
   the page gives both commands as the form a provisioning script runs, with
   no prompt (REQ-1486). Closed by: judgement in the pull request's review,
   because no pattern tells an unattended form from an interactive one.
4. Given every unit under `plugins/`, when a test lists their files, then no
   directory or file is named for an agent other than Claude Code, such as
   `codex/` or `AGENTS.md`, and adding one fails the test (REQ-1490,
   REQ-1492). Closed by: a test under `tools/` naming REQ-1492.

## What to do

Write the install test so that it never touches the person's own
configuration: point the platform at a temporary directory, which the
platform's settings documentation names, and remove it afterwards. Install
from the checkout's marketplace file so the test needs no network beyond the
platform's own. Read "enabled" from the platform's own listing, never from a
file the test wrote.

The list of names that mark a second agent is my choice, recorded here: a
directory or file named `codex`, `cursor`, `gemini`, `copilot`, `aider` or
`AGENTS.md`, matched without regard to case. Keep the list in the test, with a
line saying a port adds its platform files outside `plugins/<unit>/` only by a
new decision.

Add the unattended form to `docs/README.md` beside the quick start, and add
both tests to the `test` verb in `.meowpaw/profile.toml`. `CLAUDE.md` lists the
checks that stay in `tools/`; update that list in the same change.

## Depends on

Nothing.

## Evidence

Not yet.

Criterion 3 rests on judgement, for the reason it gives.

## Left alone

A port to any other agent, which ADR-2500 leaves unsettled, so REQ-1490 holds
as a property of the layout that this task tests and doesn't exercise.
