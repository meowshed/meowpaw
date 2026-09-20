---
id: RES-0061
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:review`

## Summary

Review reads the diff against a recorded base and returns findings
worst-first with two verdicts rather than one. It reads the verification report
first and never reports what a gate verb already fixes; a finding names the
input that makes the code wrong, or is asked as a question instead; and each
finding is attacked before it is reported. A clean result is stated plainly as
clean.

Findings worst-first, two verdicts, and the step the work returns to.

## Who has an equivalent

| Harness        | Shape                                                                                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| superpowers    | A reviewer per task on the diff against a recorded base, two verdicts for conformance and quality, a fix loop capped at five rounds, and a final whole-branch review on the most capable model |
| harness4claude | Several review dimensions in parallel, then adversarial adjudication attempting to refute the findings                                                                                         |
| cc-sdd         | An independent reviewer per task; two rejections trigger auto-debug in a clean context                                                                                                         |
| vlie           | `/self-review` before push: diff, spec, boundaries, language skill, source-control skill, scoped checks, blockers first                                                                        |
| meowctl        | `/review` against the spec with a fixed order of checks                                                                                                                                        |
| meowhub        | `spec-review` verifies implementation against the spec                                                                                                                                         |

The full design discussion is in [RES-0030-review.md](RES-0030-review.md).
What follows is the command surface.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## Target selection

`/meow:review [target]` - a pull request, a branch, a path, or nothing, which
means the current branch against the protected one.

The subject is **the diff against a recorded base**, not the working tree
(superpowers). Reviewing the tree conflates this change with everything else
present.

## What it reads first

The verify report. A review that has not seen the checks spends its
attention on what a check would have found, which is the commonest waste in
model review.

Then the requirements the task cites, then the diff. vlie's order - diff, spec,
boundaries, language conventions, source-control conventions, scoped checks - is
the same idea with the project's own conventions made explicit.

## Two verdicts and a return step

Conformance and quality, separately: a faithful implementation of
the wrong thing is still wrong, and one verdict cannot say so.

Then one overall verdict from a fixed set, and anything other than "finished"
names the step the work returns to - implement, design, or as far
back as requirements when what review found is that the requirement was wrong.

## Posting

A review that stays in the terminal helps one person once. Posting findings as
inline comments on the pull request puts them where the work is.

But posting is outward-facing and irreversible enough to need confirmation, so it is a flag rather than a default, and the flag is not carried
over to the next review.

## Conclusions

1. Review the diff against a recorded base.
2. Read the verify report first.
3. Never report what a gate verb already fixes.
4. Name the input that makes the code wrong, or ask a question instead.
5. Attempt to refute each finding before reporting it.
6. Two verdicts, then one, naming the return step.
7. Say plainly when the work is clean.
8. Post only when asked.

## Sources

All read 2026-09-20.

- [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
  - the diff against a recorded base, two verdicts, and the bounded fix loop.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) - parallel
  review dimensions and adversarial adjudication.
- `~/workspace/vlie/.claude/commands/self-review.md` - the order: diff, spec,
  boundaries, language conventions, source-control conventions, scoped checks,
  blockers first.
- `~/workspace/meowctl/.claude/commands/review.md` - the check order and the
  named-input rule.
- [The standard of code review](https://google.github.io/eng-practices/review/reviewer/standard.html),
  Google engineering practices.
