---
id: BUG-1268
artifact: bug
status: approved
severity: minor
violates: REQ-1756
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 731
---

# The prose gate blocks a heredoc read through `-F /dev/stdin` as a hidden file

`meow-prose-gate` treats `/dev/stdin` as a path the text hides behind, so a
commit whose message is a readable heredoc read with `-F /dev/stdin` is
blocked with P3. The same heredoc read with `-F -` passes. The gate blocks a
text it could have read, which REQ-1756 forbids.

## Reproduction

`main` after #720, with `meow-prose-gate` 0.2.0 built by
`crates/meow/build-units`, on macOS on arm64.

1. Feed `plugins/meow-prose-gate/bin/meow-prose-gate check` a hook event
   whose `tool_input.command` is a `git commit -F /dev/stdin` with a heredoc
   `<<'EOF'` holding the line `Cache pages`.
2. Feed it the same command with `-F -` in place of `-F /dev/stdin`.

## What the system does

The first exits 2 and prints
`P3 | "/dev/stdin" | give the text inline, ...`. The second exits 0. In
`publishing` in `crates/meow/src/prose.rs`, `take` reads only `-` as standard
input and reports every other value of `-F`, `--file`, `--body-file` or
`--notes-file` as a path.

## What it should do, and why

`/dev/stdin` and `/dev/fd/0` name standard input, so the gate should read
them as it reads `-`: check the heredoc or here-string that feeds the command
with P1 and P2, and report a file redirected with `<` as P3. REQ-1756 asks a
check to match the defect and never a word that appears innocently, and a
heredoc on standard input is readable text, not a hidden file. ADR-1600
decides that `-F -` with a heredoc passes, and `/dev/stdin` is the same input
spelt as a path.

## Triage

It enters at implement, because ADR-1600 and SPC-1010 decide that text on
standard input is read, and the program misreads one spelling of it. Minor,
because `-F -` is the form the fix message suggests, and a writer blocked
this way can switch to it.

## Closed by

Fixtures in `plugins/meow-prose-gate/tests/test_gate.py`: a clean heredoc read
through `-F /dev/stdin` and through `--body-file /dev/fd/0` passing, and an
idiom in a heredoc read through `-F /dev/stdin` blocked with P1.

## Tasks

- [ ] T-001 TSK-2578 read `/dev/stdin` and `/dev/fd/0` as standard input, in
      `crates/meow/src/prose.rs`
