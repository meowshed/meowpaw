---
id: TSK-1430
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1100
closes: [REQ-0526, REQ-0528]
issue: 190
---

# The templates, shipped with meow-method and overridable

One task, one branch, one pull request, one review.

## What to do

Move `templates/*.md` to `plugins/meow-method/templates/`, correct their citations of the old requirement scheme, such as `[R-H-058]`, to the requirements in force, and change `CLAUDE.md`'s layout section to say where the templates are. Show that `meow-method template <kind>` prints the unit's template, and the repository's where `.meowpaw/templates/<kind>.md` exists.

## Depends on

TSK-1420, because `template` resolves the path this move creates.

## Evidence

The ten templates moved to `plugins/meow-method/templates/` and `templates/` is
gone. Each was rewritten to the shape this record uses: the front matter and
sections `lib/layout.toml` requires, and no citation of the old scheme, such as
`[R-H-058]`, `RSH-` or `DSN-`, because a template ships to repositories where
this repository's identifiers mean nothing, so each piece of guidance carries
its own reason. `CLAUDE.md` and `REUSE.toml` name the new place.

```text
$ grep -rn 'R-H-\|R-AREA\|RSH-\|DSN-' plugins/meow-method/templates | wc -l
0
$ meow-method template task
.../plugins/meow-method/templates/task.md
$ printf '# ours\n' > .meowpaw/templates/task.md && meow-method template task
.../.meowpaw/templates/task.md
```

`test_template_prefers_the_repository_own` now exercises the unit's template,
and the unit's 34 fixtures run `OK`.

## Left alone

The content rules each template states, which later decisions revise.
