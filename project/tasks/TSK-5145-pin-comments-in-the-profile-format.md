---
id: TSK-5145
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2580
closes: [REQ-3800]
issue: 1009
projected: 2fec0b9d5caa
tracked: 122480f0c707
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

Criterion 1 closes with the crate test `a_profile_with_comments_parses`,
which reads a profile carrying comments before a table, beside a value and
after it, and parses to the declared stages with no unknown key. Seen
failing in `8941de27` only as a missing fixture name; the behaviour held.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

YAML front matter, which REQ-2954 no longer requires the profile to share.
