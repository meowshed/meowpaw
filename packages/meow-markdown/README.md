---
reader: someone installing or running meow-markdown on Pi
answers: what meow-markdown provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-markdown@0.10.1]
---

# @meowshed/meow-markdown

Detects a Markdown corpus from what git tracks, lists the tools a repository configured for it, and prints a stages table bound from that configuration, reports a missing render target, markdownlint settings the lint stage lacks, ignores or never applies and a link check that leaves its network behaviour undeclared, and runs lychee to report a link it couldn't reach as unreachable, never as a finding, writing no file, and carries what a reviewer of a Markdown document checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-markdown
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Bind your stages

`meow-markdown bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself. Commit what it prints, so the stages run from
the declaration the repository holds:

```toml
[stages]
format = "prettier --check '**/*.md'"
lint = "markdownlint-cli2 '**/*.md'"
# meow-markdown check runs the settings checks; this lint command doesn't
# check: unresolved, Markdown has no types
test = "meow-markdown links"
# build: unbound, mkdocs.yml configures a site build
```

Each stage takes the first binding that applies:

| Stage    | Bound to                       | When                                                                              |
| -------- | ------------------------------ | --------------------------------------------------------------------------------- |
| `format` | `prettier --check '**/*.md'`   | A `.prettierrc*`, a `prettier.config.*` or a `package.json` with a `prettier` key |
| `format` | `mdformat --check .`           | A `.mdformat.toml`                                                                |
| `lint`   | `markdownlint-cli2 '**/*.md'`  | A `.markdownlint-cli2.*` or `.markdownlint.*` file                                |
| `lint`   | `markdownlint '**/*.md'`       | A `.markdownlintrc` at the root, which markdownlint-cli2 ignores                  |
| `lint`   | `meow-markdown check`          | No linter configuration of any kind                                               |
| `check`  | `meow-markdown diagrams`       | A tracked document holds a `mermaid` block                                        |
| `check`  | nothing, printed as unresolved | No `mermaid` block, since Markdown has no types                                   |
| `test`   | `meow-markdown links`          | A `lychee.toml`                                                                   |
| `build`  | nothing, printed as unbound    | A `mkdocs.yml`, `book.toml`, `hugo.toml` or `docusaurus.config.*`, which it names |

A stage with no binding is a comment naming what the program looked for.
Where you configured two tools for one stage, such as a `.prettierrc` beside
a `.mdformat.toml`, the stage binds the first in this table, and a comment
under it names the other with its file, so you can see which one runs.
`build` stays unbound where a site generator is configured, because nobody has
yet watched a generator's build fail on a broken page. `bind` prints nothing
for a stage your profile already declares. It names a `.remarkrc*` or
`.textlintrc*` as a linter it binds no command for, and names a `mise.toml` or
a `Taskfile.yml` with the runner's pack, `meow-mise` or `meow-gotask`, since a
repository that runs its tools through a runner binds its stages to the
runner's tasks.

`meow-markdown links` is the link check that table binds, as
[Run your link check](#run-your-link-check) describes.

## Check your settings

`meow-markdown check` reports each setting your stages depend on that is
missing or has no effect, one line for each finding, and exits 1 on any:

| Line                                                                       | When                                                                                                                                                                                            |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `no render target: declare [markdown] target`                              | Your profile's `[markdown] target` is missing or empty                                                                                                                                          |
| `markdownlint-cli2 runs its defaults: no configuration file`               | Your `lint` stage runs `markdownlint-cli2`, names no `--config <file>`, and git tracks no markdownlint configuration                                                                            |
| `markdownlint runs its defaults: no configuration file`                    | Your `lint` stage runs `markdownlint` or `markdownlint-cli`, names no `-c <file>`, `--config <file>` or `--config=<file>`, and git tracks no `.markdownlint.*` or `.markdownlintrc` at the root |
| `markdownlint ignores <file>`                                              | Your `lint` stage runs `markdownlint` or `markdownlint-cli`, and git tracks a `.markdownlint-cli2.*` file                                                                                       |
| `<dir>: <a> and <b> both configure rules; markdownlint-cli2 applies <a>`   | One directory holds a `.markdownlint.*` and a `.markdownlint-cli2.*` whose `config` sets any rules                                                                                              |
| `link check declares no <setting>`                                         | A stage runs `lychee` or `meow-markdown links`, and nothing it reads sets `offline`, `max_retries` or `cache`                                                                                   |
| `<file> doesn't parse as TOML: <message>`                                  | The link check's settings file isn't valid TOML                                                                                                                                                 |
| `.lycheecache isn't ignored`                                               | The link check's cache is on, and no ignore file in your repository covers `.lycheecache`                                                                                                       |
| `[docs] diagrams = <notation> needs a build step; the record can't use it` | Your profile's `[docs] diagrams` names `plantuml`, `graphviz`, `dot`, `d2`, `structurizr`, `tikz`, `latex` or `drawio`                                                                          |

Any string in `[markdown] target` counts as a declaration. For a stage running
`lychee`, `check` reads the file `--config` names, or `lychee.toml` at the root,
and the flags `--offline`, `--max-retries` and `--cache`. For a stage running
`meow-markdown links` it reads `lychee.toml` alone, because `links` forwards no
flag. A global excludes file and `.git/info/exclude` protect one clone only, so
neither counts as ignoring `.lycheecache`. The last finding
comes from the files alone, whatever your `lint` stage runs. `check` reads the
tool your `lint` stage names, so a linter run through a runner's task, such as
`mise run lint`, isn't seen. It names a program without an `@<version>`
suffix, so `npx markdownlint-cli2@0.23.2` counts as markdownlint-cli2. Write
markdownlint-cli2's `--config` with the path as the next word, because
markdownlint-cli2 reads `--config=<path>` as a glob and applies no
configuration from it. With no finding it prints `no findings`, followed on
the same line by the groups of settings it checked: the render target, the
markdownlint settings, the link check's settings and the diagram notation, so a
clean result says what it covers. It then exits 0.

To run the checks with your linter, append the command to your `lint` stage,
naming the program by its path so a CI job without the unit's `bin/` on
`PATH` still finds it:

```toml
[stages]
lint = "markdownlint-cli2 '**/*.md' && packages/meow-markdown/bin/meow-markdown check"
```

The shell stops at the linter's first failure, so on a run where lint fails
the settings checks don't run.

## Run your link check

`meow-markdown links [<input>...]` runs
`lychee --format json --no-progress` at the root of your repository, on the
inputs you give or `**/*.md` where you give none, and forwards no flag, so
lychee takes its settings from `lychee.toml`. It reads lychee's JSON and never
its exit status, because lychee exits 2 for a site that timed out exactly as
for a broken link. Each result prints on a line of its own with its class, the
file, the line, the address and lychee's own words:

| Class         | lychee reported                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------- |
| `finding`     | A 4xx response other than those below, or `File not found` on a relative link's `file://` address       |
| `unreachable` | A timeout, an error with no status code on an `http` or `https` address, or a 5xx, 429, 408, 401 or 403 |
| `skipped`     | An address lychee excluded, by its defaults or by `offline`, so it was never checked                    |
| `unresolved`  | Any other error, such as a rejected 3xx                                                                 |

`links` lists the findings first, then the unreachable and the unresolved
results under their own headings, then how many addresses it skipped. It exits
1 on any finding, 3 where there is no finding but anything is unreachable or
unresolved, and 0 where every checked link resolved. A skipped address counts
towards no exit status. A site that is down therefore never makes a finding,
and never makes a pass either.

`links` prints `evidence: lychee's JSON report, read from lychee's standard
output`, because it reads lychee's machine-readable report and not the text
lychee writes for people.

`links` compares `git status --porcelain` before and after lychee runs, and
prints `left in the working tree: <path>` for each file the run added, such as
a `.lycheecache` no ignore file covers. That line doesn't change the exit
status, because `check` already reports an unignored cache as a finding.

`meow-checks` reads a `test` stage's exit status alone, so it reports a `links`
run that exits 3 as failed, and the lines it quotes say `unreachable`.

## Check your diagrams

A diagram is text in a fenced block in the document that carries it, never an
embedded image, because an image drifts from its source with no diff to show
it. Mermaid is the notation unless your profile declares another under
`[docs] diagrams`, because GitHub renders a `mermaid` block with no build step,
no package and no generated file:

```toml
[docs]
diagrams = "mermaid"
```

`meow-markdown diagrams [<input>...]` parses each `mermaid` block in the
tracked Markdown, or in the inputs you give, with `mmdc`, the Mermaid
command-line tool. It writes the blocks and the output `mmdc` renders outside
your working tree. It prints one line for each block that doesn't parse, as
`<file>:<line>: mermaid block doesn't parse: <mmdc's words>`, with the line
the fence opens on. It also prints `<file>:<line>: image <target> embedded; ...`
for each image link to a `.png` or `.svg` file in a document under the
record's root, `[record] root` or `project`, and says nothing of the same link
in a document outside it. It exits 1 on any finding, 3 where `mmdc` is
missing or broken, and 0 otherwise. A repository with no `mermaid` block never
runs `mmdc`.

A notation that needs a build step is refused for the record: `check` reports
`[docs] diagrams = plantuml needs a build step; the record can't use it`. In
a document outside the record you may use one, and that document states its
cost. No program reads whether it does, so review holds that.

State in the prose beside a diagram everything the diagram asserts, because a
reader of the raw file gets the source and not the picture. Put no obligation
in a diagram, which belongs in a requirement, and no reason, which belongs in
a decision. No parser reads whether the prose says what the diagram does, so
review holds both rules.

`mmdc` pulls a headless browser, so installing it costs download size and the
run takes longer. This repository's fixtures run a stand-in `mmdc`, and the
command wasn't observed against a release of the real one.

## Generated files

Commit no generated file: Markdown's tools generate nothing that is project
state, and the configuration files `meow-markdown bind` reads are files you
write. Ignore `.lycheecache`, the cache lychee writes at the root where
`lychee.toml` sets `cache = true`, because it is regenerated on the next run.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check`, `links` and `diagrams`
exit 1 on a finding, and every command exits 3 when it can't:

| Line                                              | Means                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `unresolved: not a Markdown repository`           | Git tracks fewer than two `*.md` files and no markdownlint file                             |
| `unresolved: no profile at .meowpaw/profile.toml` | The repository has no profile                                                               |
| `unresolved: the profile doesn't parse: ...`      | The profile isn't valid TOML; the parser's message follows                                  |
| `tool absent: lychee`                             | `links` found no lychee on `PATH`                                                           |
| `tool broken: lychee ended with exit status ...`  | lychee exited 3 on its configuration or 1 on its inputs                                     |
| `tool broken: lychee printed ...`                 | lychee printed no JSON, or JSON missing a map `links` reads or carrying one it doesn't know |
| `tool absent: mmdc`                               | `diagrams` found a `mermaid` block and no `mmdc` on `PATH`                                  |
| `tool broken: mmdc ended with ...`                | `mmdc` ended with an exit status other than 0 or 1, checking nothing                        |

`bind` exits 0 whatever comments its table holds, because a stage printed with
its reason is settled.

## Review a document

When Pi reviews a Markdown document, the skill has it read your
render target first, and then load `reviewing.md`, which holds seven points no
command reports:

1. Whether the heading outline, read alone, is the document's argument.
2. Whether a table or a list fits what the reader compares.
3. Whether each fence carries the right language tag, where the linter accepts
   any tag.
4. Reference links for a source cited more than twice.
5. Relative links written in a style that survives a move.
6. Whether the prose beside a diagram states everything it asserts, and the
   diagram claims nothing the prose doesn't.
7. Whether a diagram carries an obligation or a reason, which belong in a
   requirement and a decision.

The skill carries what it knows of front matter, admonitions and diagram
blocks for each known render target, and judges none of them for a target it
doesn't know. It reports a clean lint as clean structure and never as a good
document, and a style linter such as Vale as checking consistency, never
quality. It never runs markdownlint-cli against a `.markdownlint-cli2.*` file,
never fails a check on an unreachable link without saying it was unreachable,
and never runs a spell check where you keep no project word list. The writing
standard belongs to `meow-prose`, not to this pack.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when a Markdown document is reviewed. The program is a native binary shipped
inside the unit, and needs git on the machine. `links` reaches every remote
address your documents cite on each run, and `diagrams` starts a headless
browser through `mmdc` for each `mermaid` block. On a machine the unit carries
no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-markdown --help` lists the subcommands, and `meow-markdown <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
