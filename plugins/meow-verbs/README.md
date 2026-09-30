---
reader: someone who has meow-verbs installed and sees its notice
answers: why meow-verbs is a stub now, and how to move to meow-checks
kind: reference
describes: [meow-verbs@0.9.0, meow-checks@0.9.0]
---

# meow-verbs

`meow-verbs` is now `meow-checks`, and this unit is a stub that says so. It
carries no skill and no program, so the `verify` skill and the `meow-verbs`
command are gone under this name. When a session starts it gives Claude a
short notice to pass on to you, with the two commands that move your install:

```bash
claude plugin install meow-checks@meowpaw
claude plugin uninstall meow-verbs@meowpaw
```

After the move, `meow-checks run`, `status` and `evidence` do what the
`meow-verbs` commands did, and the skill loads as `meow-checks:verify`. Your
`.meowpaw/profile.toml` stays as it is: the `[verbs]` table and the five verb
names didn't change. [`meow-checks`'
page](https://github.com/meowshed/meowpaw/blob/main/plugins/meow-checks/README.md)
covers the rest.

## What it costs you

Nothing in context on every turn. The notice is about 400 characters, given
to Claude once when a session starts.

## When it goes

The release after `meow-checks` 0.9.0 removes this stub from the catalogue.
