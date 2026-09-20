---
id: RES-0125
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0005
---

# make

## Summary

make has no concept of a task, so every resolution is an inference and the pack
resolves narrowly or not at all. The finding that changes behaviour rather than
reporting: enumerating make targets executes code. The manual states that make
updates the makefiles it reads, and that neither dry run nor question mode
prevents it. Running it here confirmed the recipe fires, writes to standard
error and creates a file. Reading a make project is an action rather than an
inspection.

Research for one supported tool. make is everywhere, so a pack supports it, and
it is the runner a pack can promise least about. make has no concept of a task:
a target is a file rule, and everything a runner pack wants to know has to be
inferred.

It covers what marks a make project, why enumeration is an approximation, the
verified finding that enumerating can execute code, what a pack may resolve,
what it authors, and what the skill has to contain.

It does not cover the class of task runners, which is
[RES-0121-task-runners.md](RES-0121-task-runners.md).

## The question

The other three runners answer _what does this project call its test_ directly.
make does not have the question. The pack's job is to decide how much inference
is honest, and the answer is: very little, and reading the file is itself an
action with consequences.

## Method

The manual was fetched and read on 2026-09-20, specifically the section on
how makefiles are remade, which is where the statement that dry run and
question mode do not prevent updating came from.

That behaviour was then reproduced locally rather than taken on trust. We wrote
a makefile that includes a generated makefile, plus a rule whose recipe wrote
to standard error and created that file. We read it with the enumeration flags
and again with the dry-run flag. In both cases the recipe ran and the file
appeared. The version used was the one shipped with this operating system, and
that version is named in the document because it is a decade old.

The academic work on parsing the internal database was fetched for how others
extract targets and for the phony-target false-positive problem.

## Findings

### Enumerating make targets executes code, which is documented and was verified here

This is the finding that changes how a pack behaves rather than what it
reports.

The manual states that after reading all makefiles, make _"will consider each
as a goal target, in the order in which they were processed, and attempt to
update it."_ Dry run does not prevent it:

> `-q` (or `--question`) and `-n` (or `--just-print`) do not prevent updating
> of makefiles, because an out-of-date makefile would result in the wrong
> output for other targets.

So a makefile with `include generated.mk` and a rule that builds
`generated.mk` will build it when anything reads the makefile - including a
dry run and including question mode.

Verified on GNU Make 3.81, the version macOS ships. A makefile containing
`include generated.mk` and a rule whose recipe writes to standard error and
creates the file was read with `make -pRrq`, the flags a pack would use to
enumerate targets without building anything. The recipe ran: the message
appeared on standard error and `generated.mk` was created in the working
directory. The same happened under `make -n`.

Three consequences, and they are the most important in this document.

Reading a make project is not side-effect free. A pack that enumerates
targets to resolve a verb may have run a recipe the repository's author wrote,
with whatever that recipe does.

A check may modify the working tree. The created file is a change the
harness caused while claiming to be inspecting, which breaks the rule that a
check does not change what it checks.

The escape is narrow. The manual gives one: naming the makefile explicitly
as a goal makes `-n` apply to it. That is not general enough to rely on, since
the pack does not know the generated makefile's name before reading the
makefile that includes it.

The honest posture is to treat enumeration as an action. Do it only in a
repository the user is working in, report that it ran, and prefer a static read
of the makefile text for detection.

### There is no task metadata, so every resolution is an inference

A target is a file rule. It may or may not be phony, may or may not be a test,
may or may not be callable independently. `.PHONY` marks a target as naming no
file, and once declared _"the recipe will be executed every time the target
comes up for remaking"_. Declaring it is a convention many makefiles omit, and
a target that happens to share a name with a file silently stops running.

The database from `-p` is parseable and is what the research literature uses
for this, with the noted problem that phony targets produce false positives in
a dependency graph unless they are identified and substituted. The same is true
here in reverse: phony targets are exactly the ones a runner pack wants, and
they are only reliably identifiable where `.PHONY` was declared.

### So the pack resolves narrowly and reports unresolved often

The rule that falls out: resolve a verb only to an **exactly named phony target
the pack can see** - `test`, `lint`, `fmt`, `build` - and report the verb
unresolved otherwise.

Deciding that `make check` is the test verb is exactly the failure the
unresolved-verb rule exists to prevent. A makefile is where the temptation is
strongest, because the name is nearly always close enough to be plausible.

### Recursion makes the target list incomplete by construction

A makefile that invokes `$(MAKE)` in a subdirectory has targets that do not
appear in the parent's database. So the enumerated list is a list of one
directory's targets, and a repository built with recursive make has as many
lists as it has makefiles.

A pack that reports the parent's list as the project's has reported a fraction.

### The version installed is frequently a decade old

The machine this was verified on runs GNU Make 3.81, released in 2006, which is
what macOS ships. GNU Make 4.x added `.ONESHELL`, `--output-sync`, the `!=`
assignment and `$(file ...)`, none of which exist in 3.81.

So a makefile using a 4.x feature fails on a stock macOS machine, and a pack
reporting that failure as a project defect is wrong. The version is part of the
environment report.

BSD make is a different program again, and a `Makefile` that works under GNU
make may not parse under it.

### Parallelism and failure semantics differ from every other runner

`-j` runs recipes in parallel and interleaves their output unless
`--output-sync` is available and used, so captured output from a parallel make
may not be attributable to a target. `-k` continues after a failure, which
means a non-zero exit summarises several failures rather than naming one.

`.DELETE_ON_ERROR` is the special target that deletes a failed recipe's output
file. Without it a partially written target file stays and looks up to date on
the next run, which is the classic make defect that survives every review.

### What the pack authors

A makefile, cautiously. Adding a `.PHONY` declaration for the verb targets is
the single highest-value edit. It is what makes the project's own targets
detectable, and what stops a target silently ceasing to run when a file of the
same name appears.

### What a reviewer needs that no command reports

Whether the phony targets are declared, and which ones were forgotten.

Whether `.DELETE_ON_ERROR` is set, because without it a failed build leaves a
file that looks finished.

Whether the makefile is parallel-safe, given that `-j` is how anyone would run
it on a large project.

Whether recursion is hiding a dependency the parent cannot see.

Whether an `include` regenerates something, which is now known to be a question
about what reading the file does.

### What the skill has to contain

In the body, in this order:

1. The enumeration hazard, first. Reading a makefile may run recipes, even
   under `-n` and `-q`; this is documented and verified; treat enumeration as
   an action.
2. Detection. `Makefile`, `GNUmakefile`, and the make version installed.
3. The narrow resolution rule. Exactly named phony targets only;
   everything else unresolved.
4. Recursion. The list is per makefile, not per repository.
5. What must never happen. Guessing that a similarly named target is the
   verb. Reporting a 3.81 failure on a 4.x feature as a project defect.
   Attributing interleaved parallel output to a target.

In supporting files: the special targets and what each changes; the
database format and how to read it; the version differences between 3.81 and
4.x; and the dated facts with what to re-check.

## Conclusions

1. Enumerating make targets is an action, not an inspection. make updates
   the makefiles it reads, and `-n` and `-q` do not prevent it, so reading a
   project may run recipes and create files.
2. A pack states that enumeration ran where it did, because a check that
   modified the working tree has to say so.
3. Detection prefers a static read of the makefile text, and full
   enumeration is used only where running the repository's own code is already
   expected.
4. A verb resolves only to an exactly named phony target, and reports
   unresolved otherwise, because a near-miss name is the likeliest wrong
   answer.
5. A target without `.PHONY` is reported as unreliable, since it stops
   running as soon as a file of that name exists.
6. The enumerated list is per makefile, and a recursive build has as many
   lists as makefiles, so the parent's list is never reported as the project's.
7. The make version is part of the environment report, because the version
   macOS ships predates `.ONESHELL`, `--output-sync`, `!=` and `$(file ...)`,
   and a failure on one of those is an environment failure.
8. BSD make is a different program and a GNU makefile is not assumed to
   parse under it.
9. Output from a parallel run is not attributed to a target unless output
   synchronisation was used, because otherwise it is interleaved.
10. A non-zero exit under `-k` summarises several failures, so the report
    does not name one.
11. `.DELETE_ON_ERROR` is checked, because without it a failed recipe
    leaves an output file that looks up to date.
12. Adding `.PHONY` for verb targets is the pack's highest-value edit, and
    is proposed rather than applied silently.
13. The skill body carries the enumeration hazard, detection, the narrow
    resolution rule, recursion, and the prohibitions, in that order.

## Sources

All read or run 2026-09-20.

- [How makefiles are remade](https://www.gnu.org/software/make/manual/html_node/Remaking-Makefiles.html)
  - that after reading all makefiles make considers each as a goal target and
    attempts to update it; that `-q` and `-n` do not prevent updating of
    makefiles because an out-of-date makefile would give the wrong output for
    other targets; and that naming the makefile explicitly as a goal makes those
    options apply to it.
- [The GNU make manual](https://www.gnu.org/software/make/manual/make.html) -
  `.PHONY` marking targets that do not name files, with the recipe executed
  every time the target comes up for remaking; `-n` printing recipes without
  running them; `-p` printing the internal database; `-k` continuing after
  errors; and the sections on output and input during parallel execution.
- **Run locally, 2026-09-20, GNU Make 3.81 as shipped with macOS.** A makefile
  containing `include generated.mk` and a rule whose recipe wrote to standard
  error and created that file was read with `make -pRrq` and again with `make
-n`. In both cases the recipe ran: the message appeared on standard error and
  `generated.mk` was created. This is the verification of the documented
  behaviour above, and the evidence for treating enumeration as an action.
- [Detecting build dependency errors in incremental builds](https://arxiv.org/pdf/2404.13295)
  - extracting declared build dependencies by parsing make's internal database
    from `make -p`, and the treatment of phony targets as a source of false
    positives that must be identified through the `.PHONY` variable.
