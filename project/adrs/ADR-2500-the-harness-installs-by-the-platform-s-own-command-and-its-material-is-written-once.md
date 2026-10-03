---
id: ADR-2500
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1486, REQ-1490, REQ-1492]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2500. The harness installs by the platform's own command, and its material is written once

## Decision

A machine-provisioning system installs and configures the harness by running
the platform's own commands, `claude plugin marketplace add` and
`claude plugin install`, with no prompt and no person (REQ-1486). The
installation page under `docs/` gives those commands as the unattended form,
and a test runs them in a clean configuration directory and checks that each
unit is enabled.

Material that holds for any agent, such as the writing standard, the method's
steps and the templates, is written once, as Markdown, and no unit keeps a
copy per agent (REQ-1492). What is specific to Claude Code, such as hook
declarations, agent front matter and the plugin manifest, stays in the files
the platform reads. A port to another agent with equivalent primitives then
rewrites those files and reuses the rest (REQ-1490).

Once this is accepted, a dotfiles or provisioning script can install the
harness on a new machine. What still doesn't work: no port to another agent
exists, so REQ-1490 is a property of the layout and has not been
demonstrated.

## Why

RES-0002 describes the six private harnesses the harness replaces, one of
them inside a dotfiles and environment manager, so the machines it runs on
are set up by provisioning, and a step that needs a person is one a new
machine skips. The platform's plugin commands take their arguments on the
command line, which a provisioning script can pass. Writing agent-neutral material once keeps a port to rewriting the
platform files only.

## Alternatives

| Option                       | Better at                     | Why it lost                                                     |
| ---------------------------- | ----------------------------- | --------------------------------------------------------------- |
| Do nothing                   | No test to keep               | Nobody knows whether an unattended install works until it fails |
| An install script of our own | One command for everything    | REQ-1480 rules out an installer of the harness's own            |
| Material per agent           | Each agent gets tuned wording | Two copies drift, and the drift is found by a user              |

## What it costs

The test needs the platform's command-line tool in the gate, and a change to
the plugin commands' flags breaks it.

## What would reverse it

- The platform's plugin commands start to prompt or to need a session, so an
  unattended install can't use them.

## Consequences

The installation page states the unattended form. The gate gains a test that
installs into a scratch configuration directory.

## How I will know it was realised

1. A test installs every unit into a scratch configuration directory with no
   input and finds each one enabled (REQ-1486).
2. No file under `plugins/` repeats another unit's material for a second
   agent (REQ-1492).

## What this does not settle

- Which other agent, if any, the harness is ported to.
