---
id: RES-0297
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0122
---

# What `mise exec` runs, as observed

## Summary

`mise exec` loads each `<tool>@<version>` word before `--` onto `PATH` and
runs only the command after `--`, or the string `-c` gives it. So
`mise exec lychee@0.24.2 -- sh -c '...'` runs `sh` with lychee on `PATH`, and
runs no lychee. `mise x` is the same command. This adds to RES-0122 the
grammar of the words `mise exec` takes before its command.

## The question

A pack that reads a verb's command to find the programs it runs counts a word
naming a tool as a run. RES-0122 records `mise exec -- <command>` and no tool
words, so it doesn't say whether a word such as `lychee@0.24.2` in a
`mise exec` command is a program the command runs.

## Method

I ran mise 2026.9.11 on 2026-09-29 on this machine, a Mac on arm64, from a
scratch directory with no `mise.toml`, and read `mise exec --help`.

## Findings

### The words before `--` are tools mise loads

`mise exec --help` gives the usage as
`mise exec [FLAGS] [TOOL@VERSION]... [-- COMMAND]...` and says
`"--" separates tools from the command to pass along to the subprocess`.

`mise exec lychee@0.24.2 -- sh -c 'echo ran=$0; command -v lychee'` printed
`ran=/bin/sh` and the path of lychee 0.24.2 in mise's install directory, and
exited 0. `mise exec lychee@0.24.2 npm:markdownlint-cli2@0.23.2 -- sh -c 'command -v markdownlint-cli2'`
printed the path of markdownlint-cli2 0.23.2, so each tool word before `--`
lands on `PATH`.

### `mise x` is `mise exec`, and a command is required

`mise x lychee@0.24.2 -- true` exited 0. `mise exec lychee@0.24.2` with no
command exited 2 with
`error: the following required arguments were not provided: [-- COMMAND]...`.

## Conclusions

1. In a `mise exec` or `mise x` command, the words before `--`, or before the
   `-c` flag that gives a command string, are mise's flags and the tools it
   loads. None of them is a program the command runs.
2. The command `mise exec` runs starts at the word after `--`, or inside the
   string after `-c`.

## Sources

- mise 2026.9.11, `mise exec --help` and the runs above, on this machine on
  2026-09-29 - the usage line, and that the tool words put a tool on `PATH`
  and run nothing.
