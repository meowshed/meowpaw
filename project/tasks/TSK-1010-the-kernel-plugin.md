---
id: TSK-1010
artifact: task
status: draft
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0932]
issue:
---

# Create `meow-core` and its marketplace entry

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-core/` with the manifest the platform reads, a version,
and an empty `output-styles/` directory for TSK-1020 to fill. Add the plugin to
`.claude-plugin/marketplace.json`, which does not exist yet and is created
here.

The constraints that bind it, verbatim from the requirements in force:

- The harness MUST be installable through the standard plugin mechanism of the
  agent it targets, with no installer of its own (REQ-1480).
- Every unit the harness ships MUST carry a version (REQ-2990).
- The harness MUST stay at major version zero until its public interface stops
  moving (REQ-2994).
- A unit's catalogue entry MUST carry the fields the platform displays before
  an install, and its description MUST state what the unit does for the reader
  and what keeping it installed costs them (REQ-3162, REQ-3164).
- The harness MUST be installable into an existing repository without modifying
  that repository's build, its dependencies or its directory layout
  (REQ-0010).

The description states the cost plainly: the kernel replaces the reader's own
output style while it is enabled.

## Depends on

No other task. It is the first task of the epic, and everything else in it ships
inside this directory.

## Evidence

The platform lists the plugin from this repository's marketplace and enables
it, recorded with the command, its output and the revision it ran at.

## Left alone

`docs/` is not written here. The kernel's documentation page belongs with the
style that gives it something to describe, and TSK-1020 carries it.
