---
id: REQ-4616
artifact: requirement
topic: pi-packages
class: functional
status: approved
verification: static
elaborates: RES-0340
revised: 2026-10-11
---

# REQ-4616

A run starts from a Pi session the way it starts from a Claude Code session:
the `meow-loop` extension registers a `meow-loop:run` command, and the person
typing it starts the run through the same native binary subcommands the
Claude Code hooks run. The extension feeds every other submitted input to the
runner's `prompt` subcommand, so the person's next prompt ends the run
`cancelled`, and at the settle boundary it asks the runner's `stop`
subcommand whether the run continues, carrying the frozen prompt it names
into the session once more when it does. The bounds stay outside the model,
because the runner decides every ending from the record.