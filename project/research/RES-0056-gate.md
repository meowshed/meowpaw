---
id: RES-0056
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:gate`

## Summary

Nobody in the survey has this command. Every harness verifies by asking the
model to run the project's tests in prose, so the model decides which command
counts as running them. This one runs a verb and records the result as
evidence. It has three outcomes rather than two - pass, fail and unresolved -
with environment failure separate from all three, and it never guesses a
command.

Runs a verification verb and records the result as evidence.

## Who has an equivalent

Nobody. This is the gap finding 2 names, seen as a missing command.

Every surveyed harness verifies by asking the model to run the project's tests
in prose. spec-kit's `implement` runs "Setup -> Tests -> Core -> Integration ->
Polish" and reports task completion; harness4claude demands "concrete proof -
test files, code diffs, logs"; superpowers runs the tests through the
implementer subagent. In all of them, _which command_ constitutes running the
tests is left to the model.

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

## The surface

```text
/meow:gate <verb> [scope] [filter]
```

- `verb` - one of the five, and nothing else.
- `scope` - a path, for a repository with several. Defaults to the
  whole tree, or to the scope containing the changed files.
- `filter` - one test, one file, where the tool supports it.

`disable-model-invocation` is **false** here: the model must be able to run a
gate on its own, because everything else in the harness depends on evidence and
evidence comes from this command.

`allowed-tools` cannot be used to pre-approve, because the command it runs is
resolved at runtime from the profile or a pack. That is a genuine friction and
the honest answer is that a repository pre-approves its own gate commands in
its permission settings, which `init` can propose.

## Three outcomes, not two

| Outcome        | Exit | Means                                      |
| -------------- | ---- | ------------------------------------------ |
| Pass           | 0    | The command ran and succeeded              |
| Fail           | 1    | The command ran and failed                 |
| **Unresolved** | 3    | No command could be resolved for this verb |

The third is the whole point. It is distinct from failure because
the responses differ: a failure means fix the code, an unresolved verb means
fix the profile or install a pack. Collapsing them into "not passing" tells the
user nothing about which.

A fourth case exists and must not be collapsed either: **the command resolved
but its tool is absent** - `cargo` not installed, `dotnet` missing. That is
neither a code failure nor an unresolved verb; it is an environment problem, and
`doctor` is where it is diagnosed.

## What it records

The command as executed, the exit status, the output, and the tree revision at
the time. That record is the only thing anything else may
cite as having run a check.

Output handling matters more than it looks. A failing test suite produces
thousands of lines, and putting all of it into context to prove one failure is
the most expensive thing the harness can do. The record keeps everything; what
enters context is the failing portion.

## Conclusions

1. Five verbs, no sixth.
2. Resolve from the profile, then a pack, then stop.
3. Never guess a command.
4. Three outcomes with distinct exit codes, and environment failure separate
   from all three.
5. Record command, status, output and revision.
6. Put the failing portion in context, keep the whole in the record.

## Sources

All read 2026-09-20.

- [github/spec-kit `implement.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/implement.md)
  - phase-ordered execution, and verification left to the model.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) - evidence
  as test files, diffs and logs, with the command that produces them unspecified.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) and
  [Configure permissions](https://code.claude.com/docs/en/permissions) -
  `allowed-tools`, and why a runtime-resolved command cannot be pre-approved by
  a static rule.
- `~/workspace/hephaestus/.claude/settings.json` - an allow list of task-runner
  invocations as a repository's real interface to its own checks.
