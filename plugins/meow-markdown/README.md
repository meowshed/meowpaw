---
reader: someone choosing or running meow-markdown
answers: what meow-markdown does, what it adds to a session and how to run it
kind: reference
describes: [meow-markdown@0.2.0]
---

# meow-markdown

`meow-markdown` tells you whether your repository holds a Markdown corpus,
lists the tools you configured for it, prints a `[verbs]` table bound from
that configuration, and checks the settings behind your verbs. It runs no Markdown tool and writes no file: it reads the
files git tracks and runs git alone. It installs on its own, with no other part
of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-markdown@meowpaw
```

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-markdown status
```

From your own shell, run the same launcher by its path in the installed unit.

The program counts a repository as Markdown where git tracks two or more `*.md`
files, or any `.markdownlint*` file. A lone `README.md` isn't a corpus, since
every repository has one.

`status` prints, in order:

1. How many `*.md` files git tracks.
2. The render target your profile declares in `[markdown] target`, and whether
   the skill knows it: `github`, `gitlab`, `mkdocs`, `docusaurus`, `hugo`,
   `mdbook` and `obsidian` are known, and another string is reported as
   declared and unknown to the skill.
3. Each markdownlint configuration file git tracks, by directory, with the
   front ends that read it. markdownlint-cli2 alone reads a
   `.markdownlint-cli2.*` file, and markdownlint-cli2 and markdownlint-cli both
   read a `.markdownlint.*` file.
4. Each other tool it recognises: prettier, mdformat, remark-lint, textlint,
   lychee and a site generator's configuration.
5. Where `lychee.toml` sets `cache = true`, a line saying lychee writes
   `.lycheecache` at the root.

## Bind your verbs

`meow-markdown bind` prints a `[verbs]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[verbs]
format = "prettier --check '**/*.md'"
lint = "markdownlint-cli2 '**/*.md'"
# meow-markdown check runs the settings checks; this lint command doesn't
# check: unresolved, Markdown has no types
test = "meow-markdown links"
# build: unbound, mkdocs.yml configures a site build
```

Each verb takes the first binding that applies:

| Verb     | Bound to                       | When                                                                              |
| -------- | ------------------------------ | --------------------------------------------------------------------------------- |
| `format` | `prettier --check '**/*.md'`   | A `.prettierrc*`, a `prettier.config.*` or a `package.json` with a `prettier` key |
| `format` | `mdformat --check .`           | A `.mdformat.toml`                                                                |
| `lint`   | `markdownlint-cli2 '**/*.md'`  | A `.markdownlint-cli2.*` or `.markdownlint.*` file                                |
| `lint`   | `meow-markdown check`          | No linter configuration of any kind                                               |
| `check`  | nothing, printed as unresolved | Always, since Markdown has no types                                               |
| `test`   | `meow-markdown links`          | A `lychee.toml`                                                                   |
| `build`  | nothing, printed as unbound    | A `mkdocs.yml`, `book.toml`, `hugo.toml` or `docusaurus.config.*`, which it names |

A verb with no binding is a comment naming what the program looked for.
`build` stays unbound where a site generator is configured, because nobody has
yet watched a generator's build fail on a broken page. `bind` prints nothing
for a verb your profile already declares. It names a `.remarkrc*` or
`.textlintrc*` as a linter it binds no command for, and names a `mise.toml` or
a `Taskfile.yml` with the runner's pack, `meow-mise` or `meow-gotask`, since a
repository that runs its tools through a runner binds its verbs to the
runner's tasks.

`links` isn't shipped yet, so a table binding `test` names a command this
version doesn't run: until it ships, it prints the usage line and exits 2.

## Check your settings

`meow-markdown check` reports each setting your verbs depend on that is
missing or has no effect, one line for each finding, and exits 1 on any:

| Line                                                                     | When                                                                                               |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `no render target: declare [markdown] target`                            | Your profile's `[markdown] target` is missing or empty                                             |
| `markdownlint-cli2 runs its defaults: no configuration file`             | Your `lint` verb runs `markdownlint-cli2` and git tracks no markdownlint configuration             |
| `markdownlint ignores <file>`                                            | Your `lint` verb runs `markdownlint` and git tracks a `.markdownlint-cli2.*` file                  |
| `<dir>: <a> and <b> both configure rules; markdownlint-cli2 applies <a>` | One directory holds a `.markdownlint.*` and a `.markdownlint-cli2.*` whose `config` sets any rules |

Any string in `[markdown] target` counts as a declaration. The last finding
comes from the files alone, whatever your `lint` verb runs. `check` reads the
tool your `lint` verb names, so a linter run through a runner's task, such as
`mise run lint`, isn't seen. With no finding it prints `no findings` and exits 0.

To run the checks with your linter, append the command to your `lint` verb,
naming the program by its path so a CI job without the unit's `bin/` on
`PATH` still finds it:

```toml
[verbs]
lint = "markdownlint-cli2 '**/*.md' && plugins/meow-markdown/bin/meow-markdown check"
```

The shell stops at the linter's first failure, so on a run where lint fails
the settings checks don't run.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check` exits 1 on a
finding, and every command exits 3 when it can't:

| Line                                              | Means                                                           |
| ------------------------------------------------- | --------------------------------------------------------------- |
| `unresolved: not a Markdown repository`           | Git tracks fewer than two `*.md` files and no markdownlint file |
| `unresolved: no profile at .meowpaw/profile.toml` | The repository has no profile                                   |
| `unresolved: the profile doesn't parse: ...`      | The profile isn't valid TOML; the parser's message follows      |

`bind` exits 0 whatever comments its table holds, because a verb printed with
its reason is settled.

## What it costs you

The skill's description stays in context on every turn, within the 380
characters the unit's budget states. The program is a native binary shipped
inside the unit, and needs git on the machine. On a machine the unit carries
no binary for, it reports the repository as unresolved and exits 3.

## What it needs

Claude Code 2.1.280 or later, declared in
`plugins/meow-markdown/requires.toml`, and git.
