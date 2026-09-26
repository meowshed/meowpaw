---
id: BUG-1130
artifact: bug
status: approved
severity: minor
found: 2026-09-26
revised: 2026-09-26
issue: 181
---

# meow-method counted one finding as "1 findings"

## Reproduction

With `meow-method` 0.1.0, plant one defect in a scratch record and run one
check, as the fixture `test_front_matter_reports_a_status_outside_the_vocabulary`
does:

```text
$ meow-method check front-matter
project/tasks/TSK-0001-a-task.md:4: status done is not one a task stores: ...
front-matter: 1 findings
```

## What the system does

Each check ends with a line counting its findings, and the count's noun was
always plural, so one finding read as `1 findings`. The fixtures asserted that
text, and `docs/meow-method.md` showed it.

## What it should do, and why

The line should say `1 finding`, and `0 findings` or `2 findings` otherwise. A
count whose noun disagrees with its number reads as a slip in the tool, and a
reader who meets one slip starts doubting the findings around it. No
requirement states the wording, so this is a defect against SPC-1070's line
counting each check's findings and against the writing standard, not against a
requirement.

Fixing it turned up a second defect in the same unit. The layout required
`violates` on every defect, where the defect template says to leave it out when
no requirement covers the defect yet, as this record does. `meow-method check`
reported this record as `front matter has no violates`, a false positive.

## Triage

Implementation. The program, its fixtures and its page change, and `meow-method`
is released as 0.1.1.

## Closed by

`meow record` prints `finding` for a count of one and `findings` otherwise. The
fixtures assert `1 finding` with the line ending after it, and
`test_two_findings_are_counted_in_the_plural` asserts `2 findings`. The layout
no longer requires `violates` on a defect, and
`test_a_defect_may_name_no_requirement` checks it. Against 0.1.0 the changed
fixtures fail, and against the fix all 20 pass.
