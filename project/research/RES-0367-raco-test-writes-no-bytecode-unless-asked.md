---
id: RES-0367
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0110, RES-0360
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# raco test writes bytecode only when asked, and runs every file under a directory

## Summary

`raco test` writes `.zo` bytecode only when it's given `--make`, so a Scheme
pack can bind Racket's tests without leaving `compiled/` in the working tree,
which `raco make` would. Given a directory, `raco test` finds and runs every
file under it, and it exits 0 when every test passes, 2 when a test timed out
and 1 for any other failure. `test-omit-paths` and `test-include-paths` in
`info.rkt` take paths relative to the directory holding the file.

## The question

RES-0360 has a Scheme pack bind Racket's tests as `raco test --table .` and
bind no `raco make`, because `raco make` writes bytecode beside each source.
It doesn't say whether `raco test` writes that bytecode too, which decides
whether the test stage keeps the tree clean.

## Method

I read the `raco test` page of Racket's documentation on 2026-10-13. Nothing
was run, because no Racket is installed on this machine.

## Findings

### `--make` is what turns bytecode on

The page gives `-y` or `--make` as _"Enable automatic generation and update of
compiled ".zo" files."_ It says nothing else about writing bytecode, so a run
without the option writes none by the page's account.

### A directory is searched, and the exit status says how the run failed

_"When an argument path refers to a directory, raco test recursively discovers
and runs all files within the directory"_. _"If any test fails due to a
timeout, the exit status of raco test is 2"_; another failure gives 1, and
success 0. `--table` _"Print a summary table after all tests."_

### `info.rkt` paths are relative to the file

`test-omit-paths` and `test-include-paths` each take _"a list of path strings
(relative to the enclosing directory) and regexp values"_.

## Conclusions

1. A Scheme pack binds Racket's tests without `--make`, because only that
   option writes bytecode into the tree.
2. A Scheme pack runs `raco test` on the directory holding `info.rkt`, because
   `raco test` searches a directory and `info.rkt` names its paths relative to
   that directory.
3. A Scheme pack reports a stage that runs `raco test --make` or `raco make`
   as writing `compiled/` into the tree.

## Sources

- [raco test](https://docs.racket-lang.org/raco/test.html), read 2026-10-13 -
  `--make`, `--table`, directory discovery, the exit statuses and the
  `info.rkt` keys.
