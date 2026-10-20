---
name: go
description: The stages a Go repository binds, what its modules and linter configuration say, and what a reviewer of Go checks. It MUST be loaded before binding a stage in, reporting the tools of, or reviewing Go in a repository that tracks a go.mod. It MUST NOT be used to write the profile, a module file or a tool's configuration.
---

<role>
You read what a repository's modules and linter configuration call for through
the pack's program, and you report what it printed. The program binds each stage
from the files the repository commits, and its binding runs none of the tools it
names, so its table is a proposal the person accepts, never a result. The pack
was observed against Go 1.26 and golangci-lint v2, so where the installed
toolchain is newer, an observation may be stale.
</role>

<steps name="read the configuration">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-go status` and show its output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report each module's language version, the toolchain it pins, the
   declared tools, the linter configuration and whether the race detector is
   on, and stop.
</steps>

<steps name="bind the stages">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-go bind` and show the table it
   prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="check before reporting a pass">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-go check` and
   `${CLAUDE_SKILL_DIR}/../../bin/meow-go toolchain`, and show both.
2. Report each finding as the line, what is wrong and what would fix it. If
   `toolchain` exits 3, report its `unresolved:` line and say the stages ran
   under an unknown toolchain, and stop.
</steps>

<steps name="review Go">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-go status` for the module and the
   linter configuration.
2. Read `${CLAUDE_SKILL_DIR}/reviewing.md` before you review Go, and hold the
   code to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- M1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M2. Write the profile only when the person asks, because the profile is the
  repository's declaration.
- M3. Read whether `-race` was in the `test` command before you report a pass,
  because a run without it is evidence about everything except the defect Go
  programs most often have.
- M4. Ask `golangci-lint linters` for the linters this configuration enables,
  and take no list from memory, because the documentation publishes no default
  set and the answer is per repository.
- M5. Say a new module's `go` line sitting one release behind the toolchain is
  the tool's own default, because `go mod init` writes it deliberately and
  nobody neglected it.
</rules>

<rules name="what must never happen">
- M6. Never write a v1-shaped golangci-lint configuration. A v2 file declares
  `version: "2"`, puts `gci`, `gofmt`, `gofumpt` and `goimports` under
  `formatters`, and names neither `stylecheck`, `gosimple`, `disable-all` nor
  `enable-all`, because a v1 file names real tools and configures a formatter
  as a linter, so it does less than it says while passing.
- M7. Never run `go fix` in place during a check, and never report one of its
  suggestions as a defect, because it modernises code that already works and
  edits files silently.
- M8. Never treat a vulnerability scan without reachability as `govulncheck`,
  because a finding about a dependency nothing calls and one about code the
  program reaches are different claims, and a gate treating them alike is
  disabled within a week.
</rules>
