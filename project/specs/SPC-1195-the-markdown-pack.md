---
id: SPC-1195
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-0083,
    REQ-2352,
    REQ-2434,
    REQ-2438,
    REQ-2452,
    REQ-2454,
    REQ-2290,
    REQ-2292,
    REQ-2294,
    REQ-2296,
    REQ-2300,
    REQ-2302,
    REQ-2304,
  ]
---

# The Markdown pack

## Scope

This covers `meow-markdown`, the language pack for Markdown. It states what
`status` detects and lists, what `bind` prints, what `check` finds, how
`links` classifies a link check, and what the skill and `reviewing.md` carry.

Every rule SPC-1190 states for a language pack holds here, and this document
states only what is Markdown's. It leaves spelling, prose linting and site
builds unbound. Running a verb is SPC-1040's, and the writing
standard is SPC-1010's.

ADR-1900 decides this part and EPC-1800 realised it, verified under issue 624.
ADR-2620 adds the diagrams: their notation, the check that parses them and
the rules a diagram keeps.

## Boundary

| Surface                                              | What it is                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------- |
| `plugins/meow-markdown/bin/meow-markdown`            | The program: `status`, `bind`, `check`, `links` and `diagrams` |
| `.meowpaw/profile.toml`, `[docs] diagrams`           | The diagram notation the repository declares                   |
| `plugins/meow-markdown/skills/markdown/SKILL.md`     | The skill                                                      |
| `plugins/meow-markdown/skills/markdown/reviewing.md` | What a reviewer of Markdown needs beyond the commands          |
| `plugins/meow-markdown/README.md`                    | The unit's page                                                |
| `.meowpaw/profile.toml`, `[markdown] target`         | The render target the repository's documents are written for   |
| `lychee.toml` at the root                            | Where `check` reads a link check's settings, besides its flags |

The program is the `markdown` feature of `crates/meow`, built by
`build-units`. `status`, `bind` and `check` run git alone, as SPC-1190 states.
`links` runs `lychee`, and lychee writes `.lycheecache` at the root where its
cache is on.

The pack was observed against lychee 0.24.2, markdownlint-cli2 0.23.2 and
markdownlint-cli 0.49.1 (RES-0294, RES-0295).

## Behaviour

### Detection

A work tree holds a Markdown corpus where git tracks two or more `*.md` files,
or any `.markdownlint*` file (REQ-2352).

### What `status` reports

In this order:

1. The tracked Markdown files, as a count.
2. The render target from `[markdown] target`, and whether the skill knows it:
   `github`, `gitlab`, `mkdocs`, `docusaurus`, `hugo`, `mdbook` and `obsidian`
   are known. Another string is reported as declared and unknown to the skill.
3. Each markdownlint configuration file git tracks, by directory, with the
   front ends that read it: a `.markdownlint-cli2.*` file is read by
   markdownlint-cli2 alone, a `.markdownlint.*` file by markdownlint-cli2
   and markdownlint-cli, and a `.markdownlintrc` by markdownlint-cli alone,
   run in that file's directory (RES-0295).
4. Each other configured tool it recognises: a prettier, mdformat, remark-lint
   or textlint configuration, a `lychee.toml`, and a site generator's
   configuration.
5. Where `lychee.toml` sets `cache = true`, a line saying lychee writes
   `.lycheecache` at the root.

### What `bind` prints

Each verb takes the first row that applies (REQ-2352):

| Verb     | Printed as                                         | When                                                                              |
| -------- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `format` | `format = "prettier --check '**/*.md'"`            | A `.prettierrc*`, a `prettier.config.*` or a `package.json` with a `prettier` key |
| `format` | `format = "mdformat --check ."`                    | A `.mdformat.toml`                                                                |
| `lint`   | `lint = "markdownlint-cli2 '**/*.md'"`             | A `.markdownlint-cli2.*` or `.markdownlint.*` file                                |
| `lint`   | `lint = "markdownlint '**/*.md'"`                  | A `.markdownlintrc` at the root                                                   |
| `lint`   | `lint = "meow-markdown check"`                     | No linter configuration of any kind                                               |
| `check`  | `# check: unresolved, Markdown has no types`       | Always                                                                            |
| `test`   | `test = "meow-markdown links"`                     | A `lychee.toml`                                                                   |
| `build`  | `# build: unbound, <file> configures a site build` | A `mkdocs.yml`, `book.toml`, `hugo.toml` or `docusaurus.config.*`                 |
| any      | `# <verb>: unbound, looked for <files>`            | No row above applies                                                              |

`lint` binds `meow-markdown check` where no linter is configured, because the
settings checks are then the only lint the repository has. A root
`.markdownlintrc` binds markdownlint-cli, because markdownlint-cli2 ignores
that file (RES-0295). Where `lint` binds either front end, a comment under it names `meow-markdown check` as the command
that runs the settings checks. A verb's value is one command run by the shell
(SPC-1040), so a chain such as `markdownlint-cli2 '**/*.md' && meow-markdown
check` is allowed, but `bind` doesn't print it: the shell stops at the linter's
first failure, so the settings checks would go unreported on exactly the run
where lint fails, and the verb's one exit status couldn't say which of the two
failed. A repository that accepts that loss writes the chain itself, as this one
does. A `.remarkrc*` or `.textlintrc*` is named in a comment as a configured
linter the pack binds no command for. A verb the profile already declares is
left out, and a runner's configuration, such as a `mise.toml` or a
`Taskfile.yml`, is named with a pointer to that runner's pack. `bind` exits 0
once it prints the table, whatever comments the table holds, because a verb
printed as unresolved or unbound with its reason is settled (ADR-1900).

### What `check` finds

`check` exits 1 on any finding, each naming the file or the setting:

| Finding                                                                  | When                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `no render target: declare [markdown] target`                            | `[markdown] target` is missing or empty (REQ-2452)                                                                                                                                                                    |
| `markdownlint-cli2 runs its defaults: no configuration file`             | The `lint` command runs `markdownlint-cli2`, names no file after a `--config` word, and git tracks no markdownlint configuration (REQ-2434)                                                                           |
| `markdownlint runs its defaults: no configuration file`                  | The `lint` command runs `markdownlint` or `markdownlint-cli`, names no file with `-c <path>`, `--config <path>` or `--config=<path>`, and git tracks no `.markdownlint.*` or `.markdownlintrc` at the root (REQ-2434) |
| `markdownlint ignores <file>`                                            | The `lint` command runs `markdownlint` or `markdownlint-cli`, and a `.markdownlint-cli2.*` file is tracked (REQ-2434)                                                                                                 |
| `<dir>: <a> and <b> both configure rules; markdownlint-cli2 applies <a>` | One directory holds a `.markdownlint.*` and a `.markdownlint-cli2.*` whose `config` sets rules (REQ-2434)                                                                                                             |
| `link check declares no <setting>`                                       | A verb runs `lychee` or `meow-markdown links`, and neither its settings file nor its flags set `offline`, `max_retries` or `cache` (REQ-2454)                                                                         |
| `<file> doesn't parse as TOML: <message>`                                | The link check's settings file doesn't parse                                                                                                                                                                          |
| `.lycheecache isn't ignored`                                             | The link check's cache is on, and `git check-ignore` finds no ignore file in the repository covering the path                                                                                                         |

Any string in `[markdown] target` is a declaration. A command runs a tool
where one of its words, split at white space and the shell's `;`, `&`, `|`,
`(` and `)`, has the tool's name as its last path component with any
`@<version>` suffix removed, so `npx markdownlint-cli2@0.23.2` and
`node_modules/.bin/markdownlint` both count (RES-0295). The words `mise exec`
or `mise x` takes before `--`, `-c` or `--command` name tools mise loads and
runs none of, so `mise exec lychee@0.24.2 -- python3` runs no lychee
(RES-0297). A `--config` word
followed by a path gives markdownlint-cli2 its configuration, and a
`--config=<path>` word doesn't, because markdownlint-cli2 reads it as a glob.
markdownlint-cli takes its configuration from `-c <path>`, `--config <path>`
or `--config=<path>`, and run from the root it reads no `.markdownlint.*` or
`.markdownlintrc` below the root, so those count only at the root (RES-0295,
RES-0296). The finding
for two configurations in one directory is read from the files, whatever the
verb runs. A `.markdownlint-cli2.jsonc`, `.json`, `.yaml` or `.yml` sets rules where
its `config` key holds a value other than null or an empty object, and one
that doesn't parse sets none, because markdownlint-cli2 then fails on it
itself. A `.markdownlint-cli2.cjs` or `.mjs` is code `check` doesn't run, so
it sets rules where its text contains `config`. `check` prints each finding
on a line of its own, and `no findings` when there is none.

For a verb running `lychee`, the settings file is the one `--config` names,
or `lychee.toml` at the root, and its flags count, among them `--offline`,
`--max-retries` and `--cache`; for a verb running `meow-markdown links`, the
settings file is `lychee.toml` alone. A global excludes file and
`.git/info/exclude` don't count as ignoring `.lycheecache`. A command that
runs a linter or a link checker through a runner's task isn't read.

### What `links` reports

`meow-markdown links [<input>...]` runs `lychee --format json --no-progress` at
the repository's root, with the inputs given, or `**/*.md` where none is, and
forwards no flag. lychee's exit status decides only whether lychee ran: exit 3
or 1 is `tool broken`, even where lychee printed valid JSON. On exit 0 or 2,
`links` classifies each result from lychee's JSON, never from the exit status,
because lychee exits 2 for a timeout as for a broken link (RES-0294). It prints
one line per result naming the file, the line, the address and lychee's own
words (REQ-2438):

| lychee reports                                                                     | Printed as    |
| ---------------------------------------------------------------------------------- | ------------- |
| An entry in `timeout_map`                                                          | `unreachable` |
| An error with no status code on a network address                                  | `unreachable` |
| A 5xx, 429, 408, 401 or 403 response                                               | `unreachable` |
| A missing file behind a relative link, with a `file://` address                    | `finding`     |
| Any other 4xx response                                                             | `finding`     |
| An entry in `excluded_map`                                                         | `skipped`     |
| Any other entry in `error_map`, such as a rejected 3xx                             | `unresolved`  |
| lychee isn't on `PATH`                                                             | `tool absent` |
| lychee exits 3 or 1, or prints output that isn't JSON                              | `tool broken` |
| JSON missing `error_map`, `timeout_map` or `excluded_map`, or carrying another map | `tool broken` |

An entry in `success_map`, `redirect_map` or `suggestion_map` prints nothing:
the first two resolved, and a suggestion names an address `error_map` already
holds. Those six are the maps `links` knows, and another is `tool broken`. A
missing file is an error with no status code whose text starts
`File not found`, and another error on a `file://` address is `unresolved`.

It prints the findings first, then the unreachable and the unresolved results
under a heading each, then the number of skipped addresses. A skipped address
counts towards no exit status. `links` exits 1 where any result is a finding, 3 where
none is and any result is unreachable, unresolved, absent or broken, and 0
where every checked link resolved.

### Diagrams

A diagram is text in a fenced block in the document that carries it, and
never an embedded image (REQ-2290). A repository declares its notation in
`[docs] diagrams`, and `mermaid` is the default where it declares none,
because GitHub renders a `mermaid` block in Markdown with no build step, no
plugin and no generated file (REQ-2292, REQ-2296). A notation that needs a
build step, such as `plantuml`, is refused for the record: `check` reports
`[docs] diagrams = <notation> needs a build step; the record can't use it`.
Outside the record, a document using such a notation states its cost in
that document, which review holds (REQ-2294).

`meow-markdown diagrams [<input>...]` parses each `mermaid` block in the
tracked Markdown, or in the inputs given, with the Mermaid command-line tool,
`mmdc`, writing its output outside the working tree, and prints one line per
block that fails, naming the file, the line and the parser's words
(REQ-2304). It also prints a finding for each image link to a `.png` or
`.svg` file in a document under the record's root. It exits 1 on any
finding, 3 where `mmdc` is absent or broken, and 0 otherwise. Where the
corpus holds a `mermaid` block, `bind` prints
`check = "meow-markdown diagrams"` in place of the line saying Markdown has
no types, so a block that fails to parse fails the `check` verb.

Everything a diagram asserts is also stated in the prose beside it, because a
reader who gets the source and not the picture still needs the fact
(REQ-2300). A diagram carries no obligation, which belongs in a requirement,
and no reason, which belongs in a decision (REQ-2302). `reviewing.md`
carries both rules, because no parser tells what a diagram claims.

### What the skill carries

The skill's body gives, in order: the render target, the verbs with the link
check under `test`, what the structural linter can't tell, where prose linting
stops, and the prohibitions. It forbids running markdownlint-cli against a
`.markdownlint-cli2.*` file, failing a check on an unreachable link without
saying so, and running a spell check with no project word list. It names
`meow-prose` as the owner of the writing standard. It carries front matter,
admonitions and diagram blocks for each known render target.

`reviewing.md` carries what a Markdown reviewer checks that no command reports
(REQ-0083): whether the heading outline is the argument, a table against a
list, the language tag on a fence, reference links for a source cited more than
twice, links that survive a move, and whether a diagram claims something the
prose doesn't.

## Failure paths

Each is printed as SPC-1190 states, by every command it applies to:

| State                                                  | Reported as                                    | Exit |
| ------------------------------------------------------ | ---------------------------------------------- | ---- |
| Fewer than two tracked `*.md` and no markdownlint file | `unresolved: not a Markdown repository`        | 3    |
| No profile, or a profile that doesn't parse            | `unresolved: <what is wrong with the profile>` | 3    |
| `links`: lychee isn't on `PATH`                        | `tool absent: lychee`                          | 3    |
| `links`: lychee exits 3 or 1, or prints no JSON        | `tool broken: lychee ...`                      | 3    |
| `links`: a map is missing or unknown                   | `tool broken: lychee printed <map>`            | 3    |
