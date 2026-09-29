---
id: RES-0295
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0294
---

# What the markdownlint front ends read, as observed

## Summary

markdownlint-cli 0.49.1 reads a `.markdownlintrc` in the directory it runs
from, which RES-0294 didn't try, and markdownlint-cli2 0.23.2 ignores that
file. Both front ends apply a configuration file named on the command line:
markdownlint-cli takes it from `-c` or `--config`, and markdownlint-cli2 from
`--config` followed by the path as a separate word. markdownlint-cli2 reads
`--config=<path>` as a glob and applies no configuration from it. With no
configuration file, markdownlint-cli runs its default rules and prints nothing
that says so, as RES-0294 saw markdownlint-cli2 do. `npx` runs a program
named with a version, such as `markdownlint-cli2@0.23.2`, so a command names
a front end in that form too.

This adds observations to RES-0294 on the structural linter alone. It leaves
out lychee, the formatter and the site generators.

## The question

A pack that reports a lint verb running on its defaults has to know every file
and flag each front end takes its configuration from. RES-0294 observed the
`.markdownlint.*` and `.markdownlint-cli2.*` families and concluded that
markdownlint-cli reads only `.markdownlint.*`. It never tried markdownlint-cli
with no configuration, a `.markdownlintrc`, or a configuration named by a
flag, so the question is where each front end reads its rules from and which
of those it reports.

## Method

I ran the tools on 2026-09-29 on this machine, a Mac on arm64, in scratch
directories outside any repository:

- markdownlint-cli 0.49.1, run with `mise exec npm:markdownlint-cli@0.49.1`;
- markdownlint-cli2 0.23.2, on markdownlint 0.41.1, as installed through mise,
  and once through `npx --yes markdownlint-cli2@0.23.2`.

Each fixture held `README.md` and `docs/b.md`, each with a 149-character line.
A configuration disabled rule MD013 with `{ "MD013": false }`, so a MD013
finding shows the tool ran without that configuration. Each run passed the
glob `'**/*.md'`, quoted so the tool expanded it. I didn't try the INI form a
`.markdownlintrc` can take, or a `.markdownlintrc` in a parent directory or
the home directory.

## Findings

### markdownlint-cli reads a `.markdownlintrc` where it runs, and markdownlint-cli2 doesn't

With `.markdownlintrc` at the root, markdownlint-cli reported no MD013 line
and exited 0. With the file removed, it reported MD013 on both files, against
the default 80, and exited 1. markdownlint-cli2 run beside the same file
reported MD013 on both files. With the file in `docs/` and markdownlint-cli
run from the root, it reported MD013 on both files, so markdownlint-cli
doesn't read a `.markdownlintrc` below the directory it runs in.
markdownlint-cli2's `--help` lists its configuration files, and
`.markdownlintrc` isn't among them.

### Each front end applies a configuration file named on the command line

markdownlint-cli reported no MD013 line when run with `-c .config/mdl.json`,
and none with `--config .config/mdl.json`. markdownlint-cli2 reported no MD013
line with `--config .config/mdl.json`, where the same run without the flag
reported two. With `--config=.config/mdl.json`, markdownlint-cli2 printed
`Finding: --config=.config/mdl.json **/*.md`, so it took the word as a glob
and linted with no configuration. Its `--help` gives the form `[--config
file]`.

### markdownlint-cli runs its defaults in silence where no configuration exists

With no configuration file and no flag, markdownlint-cli printed one line per
MD013 finding against the default limit of 80, exited 1, and printed no line
saying no configuration was found. Its output reads the same whether the
repository configured the rule set or never did.

### `npx` runs a front end named with its version

`npx --yes markdownlint-cli2@0.23.2 '**/*.md'` printed
`markdownlint-cli2 v0.23.2 (markdownlint v0.41.1)` and linted the files, so a
command can name the program as `<name>@<version>`.

## Conclusions

1. A `.markdownlintrc` at the root is a markdownlint-cli configuration, read
   by markdownlint-cli alone and ignored by markdownlint-cli2.
2. A configuration file named by the lint command configures the run: for
   markdownlint-cli by `-c` or `--config`, and for markdownlint-cli2 by
   `--config` with the path as the next word. A `--config=<path>` word gives
   markdownlint-cli2 no configuration.
3. A lint verb running markdownlint-cli with no `.markdownlint.*`, no root
   `.markdownlintrc` and no `-c` or `--config` runs the default rule set, and
   nothing in the tool's output says so.
4. A command names a program by its word with any `@<version>` suffix removed,
   because `npx` runs `markdownlint-cli2@0.23.2` as markdownlint-cli2.

## Sources

- markdownlint-cli 0.49.1, run on this machine on 2026-09-29 - that it read a
  root `.markdownlintrc`, ignored one in `docs/`, applied a file named by `-c`
  or `--config`, and ran its defaults in silence with no configuration.
- markdownlint-cli2 0.23.2, run on this machine on 2026-09-29, on markdownlint
  0.41.1, and its `--help` output that day - that it ignored a
  `.markdownlintrc`, applied a file named by `--config <path>`, read
  `--config=<path>` as a glob, and ran when named `markdownlint-cli2@0.23.2`
  through `npx`.
