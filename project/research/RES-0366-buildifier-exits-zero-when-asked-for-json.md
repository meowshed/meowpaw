---
id: RES-0366
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0109, RES-0360
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# buildifier exits 0 whenever it's asked for JSON, and fixes files unless told to check

## Summary

buildifier forces its exit status to 0 whenever `--format` is given, so a
stage bound to `buildifier --mode=check --format=json` passes on a file that
needs reformatting and on every lint warning. Without `--format`, check mode
exits 4 for a file that needs reformatting and for any lint warning. Its
default mode is `fix`, which rewrites files, so a pack has to pass
`--mode=check` to keep the tree as it was. buildifier finds `.buildifier.json`
from its working directory upwards, and `-r` makes it find every Starlark file
under a directory. Bazel's `//...` names every rule target in the main
repository, `bazel` runs from the workspace directory or any directory under
it, and `bazel test` exits 4 where it finds no test.

## The question

RES-0109 and RES-0360 say buildifier formats and lints, that `--format=json`
needs `--mode=check`, and where Bazel writes. They don't say what buildifier
exits with or where it looks for its configuration, so a Starlark pack bound
from them alone could print a stage that passes whatever buildifier finds.

## Method

I read buildifier's README, its `buildifier.go` and `config/config.go` on the
`main` branch, and Bazel's pages on building and on calling Bazel from
scripts, on 2026-10-13. Nothing was run, because neither Bazel nor buildifier
is installed on this machine.

## Findings

### buildifier forces exit 0 when a format is given

`buildifier.go` lists the exit statuses: _"0: success"_, _"1: syntax errors in
input"_, _"2: usage errors"_, _"3: unexpected runtime errors"_ and _"4: check
mode failed (reformat is needed)"_. A lint warning sets 4 as well, in any
mode. Where `--format` is set, the code prints the diagnostics and sets the
status to 0, with the comment _"Exit code should be set to 0 so that other
tools know they can safely parse the json"_. The README says the same: when
`--format` is provided, _"buildifier always returns `0` unless there are
internal failures or wrong input parameters"_.

### The default mode rewrites files

`config.go` gives the mode as _"formatting mode: check, diff, or fix (default
fix)"_ and the lint mode as _"lint mode: off, warn, or fix (default off)"_.

### buildifier finds its configuration from its working directory upwards

`config.go` _"First tries the value of the BUILDIFIER_CONFIG environment
variable"_, and otherwise _"The configuration file will be resolved starting
from the process cwd and searching up the file tree"_. `-r` is _"find
starlark files recursively"_.

### Bazel runs from anywhere in the workspace, and `bazel test` exits 4 with no test

Bazel's build page says _"go to your base workspace directory or any of its
subdirectories and type `bazel`"_, and gives `//...` as _"All rule targets in
packages in the main repository"_. Its scripting page gives 3 for _"Build OK,
but some tests failed or timed out"_ and 4 for _"Build successful but no tests
were found even though testing was requested"_.

## Conclusions

1. A Starlark pack binds buildifier without `--format`, so the stage's exit
   status carries the result, and says the evidence is captured output,
   because the JSON form exits 0 on every finding.
2. A Starlark pack reports a stage that runs buildifier with `--format` as a
   finding, because that stage passes whatever buildifier finds.
3. A Starlark pack passes `--mode=check` to every buildifier command it binds,
   because the default mode rewrites the files it checks.
4. A Starlark pack runs buildifier in the directory the configuration governs,
   with `-r .`, because buildifier reads `.buildifier.json` from its working
   directory upwards.
5. A Starlark pack binds Bazel's test and build stages over `//...` run from
   the workspace directory, and its page says a workspace with no test target
   fails `test` with exit 4.

## Sources

- [buildifier README](https://github.com/bazelbuild/buildtools/blob/main/buildifier/README.md),
  read 2026-10-13 - `-r`, `--lint=warn` and the exit status with `--format`.
- [buildifier.go](https://github.com/bazelbuild/buildtools/blob/main/buildifier/buildifier.go),
  `main` read 2026-10-13 - the exit statuses and the forced 0.
- [config.go](https://github.com/bazelbuild/buildtools/blob/main/buildifier/config/config.go),
  `main` read 2026-10-13 - the modes, their defaults and where the
  configuration is found.
- [Bazel: build programs](https://bazel.build/run/build), read 2026-10-13 -
  where `bazel` runs from and `//...`.
- [Bazel: calling Bazel from scripts](https://bazel.build/run/scripts), read
  2026-10-13 - the exit statuses of `bazel build` and `bazel test`.
