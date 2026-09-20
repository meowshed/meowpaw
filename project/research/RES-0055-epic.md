---
id: RES-0055
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:epic`

## Summary

Decomposition is where a plan silently stops matching the decision it came
from. Tasks are cut by vertical slice, because a task with no observable
behaviour is a bad cut; dependencies are stated with reasons and what is
genuinely parallel is marked; a coverage check is named; and each task is sized
for one review, with a bad cut recut rather than split. The command stops for
approval and files issues only afterwards.

Decomposes an approved design into tasks with dependencies, then stops for
approval. Files the tasks as issues once approved.

## Who has an equivalent

| Harness        | Command           | Output                                                     |
| -------------- | ----------------- | ---------------------------------------------------------- |
| spec-kit       | `speckit-tasks`   | `tasks.md`, phase-ordered, with parallelism markers        |
| cc-sdd         | `kiro-spec-tasks` | `tasks.md` with `_Boundary:_` and `_Depends:_` annotations |
| meowhub        | `spec-tasks`      | `tasks.md`                                                 |
| meowctl        | `/plan`           | **GitHub issues**, after approval                          |
| harness4claude | `validate-plan`   | A gate on a plan, not a producer                           |
| vlie           | `/plan`           | Issues                                                     |

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

## Task line format

spec-kit's is the best in the survey and costs nothing to adopt:

```text
- [ ] [T001] [P] [US1] Description with file path
```

Four facts in one line: a sequential identifier, a **parallelism marker**
meaning different files and no blocking dependency, the story or requirement it
serves, and a **required file path**. All machine-readable.

cc-sdd annotates differently - `_Boundary:_` for what the task may touch and
`_Depends:_` for order - which carries the same information less compactly but
makes the boundary explicit, and that is the more useful half for delegation.

Ours needs both: identity, parallelism, the requirements closed, the path, the
boundary, and the evidence once done.

## Phases, or a dependency graph

spec-kit organises into phases - setup, foundational, then one phase per user
story in priority order, then polish - with each story independently testable.
cc-sdd and meowctl use explicit per-task dependencies instead.

Phases are easier to read and impose an order that is often false. A dependency
graph is exact and harder to skim. The resolution: **dependencies are the
truth, phases are a view**, and the plan states dependencies while the report
groups them.

The rule this method takes from meowctl: "a dependency that is only about
convenience is not a dependency; say so and let them proceed in parallel". Most
over-sequenced plans are over-sequenced for convenience.

## Coverage

meowctl's execution plan carries a coverage check - every requirement lands in
exactly one issue or is explicitly deferred with a reason. spec-kit's `analyze`
checks the same thing after the fact.

Doing it _in_ the plan is better: a decomposition that silently drops a
requirement is easier to fix before the issues exist. A decomposition now carries
it as a named check.

## Sizing

meowctl's `/plan` asks for small, medium or large "to review in one sitting",
and splits anything larger - with the rule that "if splitting it produces a
piece with no observable behaviour, the cut is in the wrong place, so recut".

That second sentence is the useful one. It is a test for _where_ to cut, not
just how small.

## Issues after approval, never before

meowctl is explicit: present the plan for approval **before creating anything
on GitHub**. Issues created from an unapproved plan make the tracker the record
of something nobody agreed to, and deleting them afterwards is worse than not
having filed them.

## Conclusions

1. Cut by vertical slice; a task with no observable behaviour is a bad cut.
2. State dependencies with reasons; mark what is genuinely parallel.
3. Carry a named coverage check.
4. Size each task for one review, and recut rather than split badly.
5. Stop for approval, then file issues.

## Sources

All read 2026-09-20.

- [github/spec-kit `tasks.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/tasks.md)
  - the `- [ ] [T001] [P] [US1] Description with file path` line format, the
    phase organisation, and the independent-testability rule per story.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - `_Boundary:_` and
  `_Depends:_` annotations, and implementation notes fed forward.
- `~/workspace/meowctl/.claude/commands/plan.md` - vertical slices, dependencies
  with reasons, the convenience-dependency rule, sizing for one review, the
  recut test, and issues only after approval.
- `~/workspace/meowctl/docs/design/0.2.0-execution-plan.md` - the decomposition
  with a coverage check.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
  `validate-plan` as a gate on a plan rather than a producer.
