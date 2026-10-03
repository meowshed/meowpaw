---
id: TSK-5145
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2580
closes: [REQ-3800]
issue:
---

# Pin comments in the profile format

A profile parser fixture proves that comments beside declarations remain
valid TOML.

## Acceptance criteria

1. Given comments before a table, beside a value and after it, when the native
   profile parser reads the file, then it returns the declared value with no
   parse finding. Closed by: a crate fixture for REQ-3800.

## What to do

Add the smallest parser fixture in `crates/meow/`; change no profile syntax.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

YAML front matter, which REQ-2954 no longer requires the profile to share.
