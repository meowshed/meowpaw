---
id: BUG-1010
artifact: bug
status: approved
severity: minor
violates: REQ-1126
found: 2026-09-21
revised: 2026-09-21
unit: U-0001
issue: 16
---

# Three record checks report a false positive on a plugin file and a page

## Reproduction

With `plugins/meow-core/output-styles/meow.md` and `docs/meow-core.md` in the
tree, at `b228817`:

```bash
python3 tools/check_index.py
python3 tools/check_front_matter.py
python3 tools/check_prose.py
```

## What the system does

`check_index` reports `plugins/meow-core/output-styles/meow.md` as not in the
index. `check_front_matter` reports the same file as carrying no `id`,
`artifact`, `status` or `revised`, and reports `docs/meow-core.md` as carrying
no front matter. `check_prose` reports `unfortunately` and `uh oh` on line 37
of the style.

Each check walks every Markdown file outside `project/` and treats what it
finds as a record.

## What it should do, and why

A plugin's own file is not a documentation page, and an output style's front
matter is the platform's: `name`, `description`, `keep-coding-instructions` and
`force-for-plugin`. A documentation page is not a record either.

The two words the prose check flags are quoted as the failing case the rule
forbids, which REQ-1126 requires of material teaching a judgement. The check
already knows this case: it exempts `CLAUDE.md` and `RES-0038-reporting.md` for
the same reason, under a comment saying that quoting a defect is not committing
one.

`CLAUDE.md` states the governing rule: a check reporting a false positive is a
defect in the check and never a reason to reword the text around it, and a
check that trips on what it should not gets switched off within a week.

## Triage

This enters at implementation. The checks are the harness's own tooling, no
requirement changes, and the texts they flag stay as they are.

## Closed by

`check_index` and `check_front_matter` walk past `plugins/`, and
`check_front_matter` walks past `docs/`. `check_prose` lists `meow.md` beside
the two documents it already exempts.

Each was seen failing first on a case that is a real defect, so none of the
three was widened into a check that cannot fail.
