---
reader: someone who has meow-method installed and sees its notice
answers: why meow-method is a stub now, and how to move to meow-flow
kind: reference
describes: [meow-method@0.30.0, meow-flow@0.31.0]
---

# meow-method

`meow-method` is now `meow-flow`, and this unit is a stub that says so. It
carries no skill and no program, so `/meow-method:run`, the `method` skill and
`paw` are gone under this name. Each session it prints a short notice with the
two commands that move your install:

```bash
claude plugin install meow-flow@meowpaw
claude plugin uninstall meow-method@meowpaw
```

After the move, `/meow-flow:run` does what `/meow-method:run` did, and `paw` is
in `meow-flow`'s `bin/` directory. [`meow-flow`'s
page](https://github.com/meowshed/meowpaw/blob/main/plugins/meow-flow/README.md)
covers the rest.

## What it costs you

Nothing in context on every turn. The notice is about 250 characters, printed
once when a session starts.

## When it goes

The release after `meow-flow` 0.31.0 removes this stub from the catalogue.
