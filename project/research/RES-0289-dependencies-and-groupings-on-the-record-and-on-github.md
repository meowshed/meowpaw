---
id: RES-0289
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0022
---

# A task's dependency line can't say it doesn't block, and GitHub offers four groupings and one blocking relation

## Summary

On `main` at #622 the record writes a dependency in two places, a `TSK-`
identifier under a task's `## Depends on` and an epic entry's
`depends: TSK-NNNN`, and `paw` treats every one as an order:
`paw ready implement` and `paw status` wait on each task line, and the rule
`defect-epic-ordered` counts either as an order between a defect's tasks. So a
dependency that is only about convenience can be written down only as one that
blocks, or left out. GitHub, the one tracker the harness projects onto, offers
four ways to group an issue, a milestone, a parent issue, a project and a
label, and one dependency relation, "blocked by", with no form that doesn't
block.

This note covers how the record and `gh` 2.101.0 express a dependency and a
grouping. It doesn't cover Linear, which RES-0134 read, or how a stack of pull
requests follows the dependency order, which RES-0065 covers.

## The question

Two questions sit behind this note: how a record can say that a dependency
doesn't block, and what could group tasks other than an epic. The assumption
behind the first is that a convenience dependency is worth recording at all.
RES-0022 quotes the rule it comes from as "a dependency that is only about
convenience is not a dependency; say so and let them proceed in parallel".

The rule reads two ways. RES-0022's own conclusion 4 says "a convenience
dependency is not one", and both templates tell the author to leave it out, so
"say so" can mean saying it isn't a dependency and writing nothing on the
record. Against that reading, a recorded convenience dependency changes what
two people do. The implementer of the second task reads why the two tasks
touch, such as a fixture both write, and whoever picks up the projected issue
on GitHub reads the same reason in its body. It changes nothing for
`paw status`, which would wait on neither. So the assumption rests on what
those two readers gain, and it fails if neither of them acts on the reason.

## Method

I read `crates/meow/src/record.rs` at #622 for every reader of
`## Depends on`, and the task and epic templates in
`plugins/meow-flow/templates/`. I counted the task records whose
`## Depends on` names a `TSK-` identifier with
`awk 'FNR==1{s=0} /^## /{s=($0=="## Depends on")} s && /TSK-[0-9]{4}/{print FILENAME; nextfile}' project/tasks/TSK-*.md`,
and their statuses with `grep -h "^status:" project/tasks/TSK-*.md | sort | uniq -c`.
I searched the task, epic and defect records for a grouping field with
`grep -l -E "^(milestone|parent|sprint|iteration|project|labels?):"`, and the
60 epics for an `epic:` field with `grep -l "^epic:" project/epics/*.md`.

On GitHub I read, without writing, the issue dependency and sub-issue
endpoints for issue #625 of `meowshed/meowpaw` with `gh api`, and read the
help of `gh issue create` and `gh issue edit` in `gh` 2.101.0. I read GitHub's
pages on issue dependencies and sub-issues. Nothing was created or linked as an
experiment, so no limit here was reproduced.

## Findings

### Every dependency the record holds is read as an order

`depends_on()` in `record.rs` returns every `TSK-` identifier in a task's
`## Depends on` section, with nothing else on the line read. Three places use
it. `paw ready` reports "`<dependency>`, which `<task>` depends on, isn't
done" for each unfinished one, `paw status` names as next only a task whose
dependencies are all finished, and `defect-epic-ordered` accepts a defect's
epic only where some task has a dependency or an entry's text contains
`depends:`.

### The record has no convenience dependency to migrate

Of the 153 task records, 53 name a dependency and 100 name none, and all 153
are approved. The templates tell the author to leave a convenience dependency
out: the epic template's entry reads "depends: TSK-NNNN - and why, since a
convenience isn't a dependency", and `meow-prose`'s task type says "a
dependency that is only convenience is not one". Nothing in the record shows
which of the 53 was a convenience, so each has to keep the meaning it was
approved with, which is an order.

### Nothing in the record groups tasks except an epic and a defect

A task names its epic in `epic:` or the defect that carries it in `bug:`, and
the draft rule `one-authority` reports a draft naming neither or both. The
defect carries its own tasks under ADR-1440, so a defect is a second record a
task sits under. The first `grep` above matched no task, epic or defect carrying a
milestone, parent, sprint, iteration, project or label field, and the second
matched no epic carrying `epic:`.

### GitHub offers four ways to group an issue

`gh issue create` in 2.101.0 takes `--milestone`, `--parent`, `--project` and
`--label`, and `gh issue edit` takes the same four with their removals. A
parent groups its sub-issues, up to 100 of them and eight levels deep,
GitHub's page says. RES-0022 found that a sub-issue doesn't close by a
closing keyword, so a harness that grouped tasks under a parent issue would
close the parents and leave the children open.

### GitHub's only dependency relation blocks

`gh issue edit` takes `--add-blocked-by` and `--add-blocking`, and GitHub's
page names these two directions of one relation and no other. A blocked issue
shows a "Blocked" icon on the issues page and on project boards. So a
dependency projected as a relation always reads as blocking, and a
convenience dependency has nowhere on GitHub to go except the issue's text,
which is where `meow-github project` already writes the task's `## Depends on`
section. `gh api repos/meowshed/meowpaw/issues/625/dependencies/blocked_by`
returned `[]` with exit status 0, so the endpoint answers for this repository.

## Conclusions

1. If a convenience dependency is recorded, it has to be told apart from an
   order both under `## Depends on` and in an epic entry's `depends:`,
   because `paw` reads both as orders. A separate section works with no
   change to the readers, since `depends_on()` reads only `## Depends on`, but
   it leaves the epic entry's `depends:` reading as an order. A marker on the
   line works only if `depends_on()` and `defect-epic-ordered` learn to read
   it.
2. Whether a convenience dependency is worth recording stays untested. This
   note didn't measure whether the implementer of the second task, or whoever
   picks up the projected issue, acts on the reason, and the case for leaving
   a convenience out, as the templates say now, rests on their not acting on
   it.
3. A dependency written before the record could say so has to keep reading as
   blocking, because every approved task was written under a rule that left
   convenience dependencies out.
4. The record groups tasks under an epic, or under the defect that carries
   them, and nothing else, and a tracker's other groupings, a milestone, a
   parent issue, a project or a label, are a second grouping the record
   doesn't hold.
5. A not-blocking dependency can't reach GitHub as a dependency relation,
   because GitHub's one dependency relation blocks. This note didn't examine
   a label or a project field as a carrier for it.

## Sources

- 2026-09-28, read: `crates/meow/src/record.rs`,
  `plugins/meow-flow/templates/task.md` and
  `plugins/meow-flow/templates/epic.md` at #622 - the readers of
  `## Depends on` and the templates' wording.
- 2026-09-28, counted: `project/tasks/` at #622 with the `awk` command in
  Method - 53 tasks naming a dependency - and with the status `grep` in
  Method - 153 tasks, all `status: approved`.
- 2026-09-28, searched: `project/tasks/`, `project/epics/` and
  `project/bugs/` at #622 with the grouping `grep` in Method, and
  `project/epics/` with the `epic:` `grep` - no match for either.
- 2026-09-28, read: `plugins/meow-prose/skills/writing/types/record/task.md`
  at #622 - "a dependency that is only convenience is not one".
- 2026-09-28, read: `gh issue create --help` and `gh issue edit --help` in
  `gh` 2.101.0 - the four grouping flags and the blocked-by flags.
- 2026-09-28, run: `gh api` on `dependencies/blocked_by`, `sub_issues` and
  `parent` for issue #625 of `meowshed/meowpaw` - `[]` with exit status 0,
  `[]` with exit status 0, and "No parent issue found" (HTTP 404) with exit
  status 1.
- 2026-09-28, read: GitHub Docs,
  [Creating issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies) -
  "blocked by" and "blocking" as the only relation, and the Blocked icon.
- 2026-09-28, read: GitHub Docs,
  [Adding sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) -
  100 sub-issues per parent and eight levels.
