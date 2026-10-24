---
id: TSK-5683
artifact: task
status: approved
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-4620, REQ-3196, REQ-4622]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Generate each unit's launcher and Pi extension and hold its copies to each other

A unit's launcher and Pi extension come from one template written by the unit's own program, and a check holds a unit's description and its package's page to their copies. This is the Pi tree generated from the Claude tree, which the owner chose on 2026-10-13.

## Acceptance criteria

1. Given a unit's declared facts (its name, its binary and its commands), when its own program writes the launcher and the Pi extension, then the committed files equal what it writes, and a check fails naming each unit whose committed launcher or extension differs (REQ-4620). Closed by: a test that writes into a scratch copy, compares, and fails against an edited launcher.
2. Given a unit, when a check reads its plugin manifest, its plugin page, its package manifest and its package page, then it fails naming each copy of the description that differs from the others (REQ-3196). Closed by: a test naming REQ-3196, seen failing against one edited copy.
3. Given a unit's page and its package's page, when the same check compares them, then it fails naming a package page that lacks a section of its unit's page, apart from the sections the unit page marks as host-specific (REQ-4622). Closed by: a test naming REQ-4622, seen failing against a package page with a section removed.
4. Given the launchers and Pi extensions this task regenerates, when `mise run all` runs, then it exits 0, and no unit's behaviour changes: every existing launcher and extension test passes unchanged (REQ-4620). Closed by: the gate of the pull request that carries this task.

## What to do

Decide where the generator lives, inside the constraints that `check_standalone` and the kernel check hold: a unit's file runs no path outside its own directory, and the kernel names no unit outside it. Generate the launcher first and prove it equal to today's before touching the extension. Where a package page differs from its unit's page by more than marked sections, write the missing sections into the package page from the unit page with the host's substitutions, and mark a section host-specific only where the host truly differs. Keep the Claude tree and the Pi tree in step, as the constitution requires.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by `tools/test_generate_launchers.py`, which writes the
generated files into a scratch copy and sees `differing` name an edited
launcher, an edited extension and a deleted launcher, and by
`tools/generate_launchers.py --check`, which the `test-tools` task runs against
the tree. The generator lives in `tools/`, outside every unit, so neither
`check_standalone` nor the kernel check applies to it. It writes the Claude and
Pi launcher of every unit from `tools/launchers.toml` and the Pi extension
`bin.ts` of the 17 units that only put their launcher on `PATH`. It was proven
byte-equal to the committed launchers before the cache was added, with one
exception: the Pi launcher of `meow-prose-gate` now ends on a newline. The
seven bespoke Pi extensions (`kernel.ts`, `flow.ts`, `git.ts`, `github.ts`,
`loop.ts`, `prose.ts`, `gate.ts`) carry a host's hook and command adapters, so
they stay hand-written.

Criteria 2 and 3 are closed by `tools/test_check_unit_copies.py`, whose tests
name REQ-3196 and REQ-4622 and fail against one edited copy and against a
package page with a section removed. The description is the plugin manifest's,
held verbatim as `description` in the plugin page's front matter, and with
Claude Code said as Pi plus the sentence "Distributed as a Pi package." in the
package manifest and the first paragraph of the package page. The check found
four drifted package descriptions (`meow-github`, `meow-loop`, `meow-markdown`,
`meow-git`), now corrected. A section is host-specific where the unit page puts
`<!-- host-specific: claude -->` under its heading. I marked 60 sections by a
text rule (they name a hook, `requires.toml`, `.claude`, the `claude` command
or a plugin manifest), and that marking rests on judgement. The 136 other
missing sections were copied into the package pages with the substitutions.

Criterion 4 rests on the gate of the pull request that carries this task.

Every stage passed in pull request #PR.

## Left alone

A unit's behaviour, and the content of any host-specific section.
