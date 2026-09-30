---
id: ADR-1900
artifact: adr
status: approved
revised: 2026-09-28
addresses: [REQ-0083, REQ-2352, REQ-2434, REQ-2438, REQ-2452, REQ-2454]
postpones: [REQ-2424, REQ-2484]
supersedes: []
---

# 1900. A Markdown pack reads the settings behind each verb, and reports an unreachable link as unreachable

## Decision

A new pack, `meow-markdown`, ships a program with four commands, `status`,
`bind`, `check` and `links`, and a skill that tells the model to use them. It
is the first language pack. It keeps the boundary SPC-1140 sets for the runner
packs, and it states that boundary once for every language pack after it:

- A pack detects its language from files the repository commits, and starts no
  tool to find out, because detection runs before anyone has chosen to trust
  the repository's tools, and must run no code the repository didn't ask for.
  The one program it runs is git, as `git ls-files` for the tracked file list
  and `git check-ignore` for an ignored path, because git is the version
  control the repository already runs under, and neither command runs a hook
  or anything the repository commits.
- `bind` prints a `[verbs]` table for the repository to paste, and prints
  nothing for a verb the profile already declares, since the repository's
  declaration comes first (REQ-0134). No command writes the profile or any
  tool's configuration.
- A verb the language can't have is printed as a comment naming the reason,
  such as `# check: unresolved, Markdown has no types`, because a verb absent
  from the profile reads as undeclared, and undeclared hides that nothing is
  missing.
- A pack's own settings live in the profile under a table named for its
  language, here `[markdown]`, so two packs installed together never write to
  one table, and a reader can tell which pack a setting belongs to.
- Each command exits 0 on a clean result, 1 on a finding and 3 on anything
  unresolved, as the runner packs do. A state that isn't a finding takes its
  name from REQ-2774: `tool absent`, `tool broken`, `unreachable` or
  `unresolved`.
- The skill carries what a reviewer needs beyond the commands in a supporting
  file, and names the tool versions the pack was observed against, so a reader
  can tell when an observation may have gone stale because the tool moved on.

### Detection and the verbs

`status` detects a Markdown corpus where git tracks two or more `*.md` files,
or any `.markdownlint*` file (REQ-2352). I chose two
files because every repository has a README, and a lone README is no corpus to
bind verbs for. Where it finds none, every command reports `unresolved: not a
Markdown repository` and exits 3.

`bind` binds each verb from what the repository configured, and never from
what is installed:

| Verb     | Bound to                                                                                                       | Where                                                                             |
| -------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `format` | `prettier --check '**/*.md'`                                                                                   | A `.prettierrc*`, a `prettier.config.*` or a `package.json` `prettier` key exists |
| `format` | `mdformat --check .`                                                                                           | Else, a `.mdformat.toml` exists                                                   |
| `lint`   | `markdownlint-cli2 '**/*.md'`                                                                                  | A `.markdownlint-cli2.*` or `.markdownlint.*` file exists                         |
| `lint`   | `meow-markdown check`                                                                                          | Else, no linter configuration of any kind exists                                  |
| `check`  | nothing; printed as unresolved, Markdown has no types                                                          | Always                                                                            |
| `test`   | `meow-markdown links`                                                                                          | A `lychee.toml` exists                                                            |
| `build`  | nothing; the site generator's configuration is named, and the verb is printed as unbound with that as a reason | A `mkdocs.yml`, `book.toml`, `hugo.toml` or `docusaurus.config.*`                 |

A verb with no row that applies is printed as unbound, with what the pack
looked for. Where `lint` is bound to a linter, `bind` prints a comment under it
naming `meow-markdown check` as the command that runs the settings checks,
because a verb holds one command and the linter's findings come first. Until a
repository wires `check` in, those checks run only when somebody runs it.

A verb printed as unresolved or unbound, with its reason, is resolved in the
sense REQ-2352 asks for. To resolve a verb is to settle what it runs, and
"nothing, for this reason" is a settled answer. Printing a guessed command in
its place would break the rule that an unresolved verb is never a pass. A `.remarkrc*` or `.textlintrc*` is named as a configured linter
the pack binds no command for yet. Where a runner's configuration exists, such
as a `mise.toml` or a `Taskfile.yml`, `bind` says so and points at that
runner's pack, because a repository that runs its tools through a runner binds
its verbs to the runner's tasks, and this pack doesn't read another tool's
tasks.

`build` stays unbound even where a site generator is configured, because I
haven't observed any generator's build command fail on a broken page, and a
bound command nobody has watched fail is a guess (RES-0111, conclusion 13).

### The render target

`check` reads `[markdown] target` from `.meowpaw/profile.toml` and reports a
missing or empty value as a finding (REQ-2452). Any string is a declaration.
`status` says whether the skill knows the named target, and the skill carries
what it knows about front matter, admonitions and diagram blocks for `github`,
`gitlab`, `mkdocs`, `docusaurus`, `hugo`, `mdbook` and `obsidian`. I accept a
target outside that list, because the requirement asks the repository to
declare one, and a closed list would leave a repository on another renderer
unable to pass.

### The settings that decide lint

`status` lists every markdownlint configuration file git tracks, by directory,
and says which front end reads each: markdownlint-cli2 reads both families, and
markdownlint-cli reads only `.markdownlint.*` (RES-0294). `check` reads the
`lint` verb's command in the profile and reports three findings (REQ-2434):

- The command runs `markdownlint-cli2` and no configuration file exists, so
  the verb runs the default rule set and nothing says so.
- The command runs `markdownlint`, the older front end, and a
  `.markdownlint-cli2.*` file exists, which that front end ignores. The finding
  names the file.
- One directory holds both a `.markdownlint.*` and a `.markdownlint-cli2.*`
  whose `config` sets rules, so one of the two has no effect. The finding names
  both, and says that in RES-0294's fixture markdownlint-cli2 0.23.2 applied
  the `.markdownlint.jsonc`.

The third is found from the files alone, whatever the verb runs.

### The link check

`meow-markdown links [<input>...]` runs `lychee --format json --no-progress`
from the repository's root, passing the inputs through, `**/*.md` where none is
given. It takes inputs only and forwards no flag, so lychee's settings for a
`links` verb live in `lychee.toml`, where `check` reads them. It classifies each result from the JSON and never from lychee's exit
status, because lychee exits 2 for a timeout exactly as for a broken link
(RES-0294). Each result prints as one line naming the file, the line, the
address and lychee's own words (REQ-2438):

| lychee reports                                                                                              | Printed as    |
| ----------------------------------------------------------------------------------------------------------- | ------------- |
| A timeout                                                                                                   | `unreachable` |
| An error with no status code on a network address: a failed connection, a refusal, TLS                      | `unreachable` |
| A 5xx, a 429, a 408, a 401 or a 403                                                                         | `unreachable` |
| A missing file behind a relative link                                                                       | `finding`     |
| Any other 4xx                                                                                               | `finding`     |
| An address in `excluded_map`, by lychee's default exclusions or `offline`                                   | `skipped`     |
| Anything else                                                                                               | `unresolved`  |
| lychee isn't on `PATH`                                                                                      | `tool absent` |
| lychee exits 3, rejecting its configuration, or exits 1, reading no input, or prints output that isn't JSON | `tool broken` |
| JSON missing a map `links` expects, or carrying one it doesn't know                                         | `tool broken` |

Each class of response code has its own reason. A 5xx says the server failed,
not the document. A 429 or a 408 says the checker was throttled or too slow.
A 401 or a 403 says the site refused the checker, and a page behind a login is
no broken link. RES-0294 observed 403, 404, 410, 429 and 503, and the exit
statuses 0, 1, 2 and 3. The rows for 401, 408 and every 5xx other than 503 are
extrapolated from those, not observed.

A skipped address was never checked, so it is neither a finding nor a pass of
that address. `links` prints how many it skipped and leaves them out of the
exit status, because the repository declared `offline` or accepted lychee's
exclusions, and lychee exits 0 on a run with only excluded addresses
(RES-0294, REQ-2774).

`links` exits 1 where any line is a finding, and still lists each unreachable
address under its own heading. It exits 3 where nothing is a finding and
anything is unreachable, unresolved, absent or broken, and 0 where every
checked link resolved. A site that is down therefore never produces a finding,
and never produces a pass either.

### What a link check declares

`check` finds each verb whose command runs `lychee` or `meow-markdown links`,
and reads that check's settings from where lychee reads them: `lychee.toml` at
the root, or the file `--config` names (RES-0294). For a command that runs
`lychee` directly, `check` also reads the flags in the command. A `links` verb
forwards no flag, so its settings are read from `lychee.toml` alone. Each of `offline`, `max_retries` and `cache` that neither place
sets is a finding, because lychee then applies its default without saying so,
and the requirement asks for the three to be declared (REQ-2454). A
configuration that doesn't parse as TOML is a finding naming the file. Where
`cache` is on, `status` says lychee writes `.lycheecache` at the root, and
`check` reports it as a finding where the repository's own ignore files don't
ignore that path. A cache that isn't ignored gets committed, and then every
clone starts from somebody else's results and skips links for up to
`max_cache_age`, so the check passes on answers it never fetched. A global
excludes file or `.git/info/exclude` protects one clone only, so `check`
counts neither.

### What a reviewer needs

The skill's body follows the order RES-0111 sets: the render target first, then
verb resolution with the link check under `test` and the reason, then what the
structural linter can't tell, then where prose linting stops, then the
prohibitions. It forbids running markdownlint-cli against a
`.markdownlint-cli2.*` file, failing a check on an unreachable link without
saying it was unreachable, and running a spell check with no project word list.
It says that the writing standard belongs to `meow-prose`, and not to this
pack.

A supporting file, `reviewing.md`, carries the six points RES-0111 lists
under what a reviewer needs that no command reports: whether the heading
outline is the argument, tables against lists, the right language tag on a
fence, reference links for a source cited more than twice, links that survive
a move, and whether a diagram claims something the prose doesn't (REQ-0083).
The skill loads it when Markdown is reviewed, and not on every turn.

### Postponed

REQ-2424 is postponed until an approved decision gives a pack a command that
writes or edits a tool's configuration file, such as a linter's or a link
checker's configuration or a spelling word list. No command here writes one,
so the requirement has nothing to hold. RES-0111 describes the word list as
something a pack maintains, and that is where the requirement would bind.

REQ-2484 is postponed again. ADR-1580 set its condition as the first language
pack, and this is it, but Markdown has no manifest that declares scripts, so
the requirement still has nothing to govern. It comes with the first pack for
an ecosystem whose manifest declares scripts, such as a `package.json`.

### After this decision

A repository with a Markdown corpus gets a `[verbs]` table for the tools it
configured, a finding where its lint runs on settings it never wrote or
silently ignores, a finding where its render target or its link check's network
behaviour is undeclared, and a link check that names a site that is down as
unreachable. This repository declares `[markdown] target = "github"`, and
appends `meow-markdown check` to its `lint` verb. What still doesn't work:

- `meow-verbs` reads a command's exit status alone, so a `test` verb bound to
  `links` that exits 3 is reported as failed. The lines it quotes say
  `unreachable`, and its summary word says `failed`.
- `check` sees a linter or a link checker only where the verb names it. A tool
  run through a runner's task, as this repository's `mise run lint` runs
  markdownlint-cli2, isn't seen, so here `check` holds the render target and
  the markdownlint files alone.
- A verb bound to `meow-markdown links` runs where the unit's `bin/` is on
  `PATH`, which Claude Code arranges for its Bash tool, or where the profile
  names the program by its path. A CI job that has neither gets exit status 127.
- Where `lint` is bound to a linter, the settings checks for REQ-2434,
  REQ-2452 and REQ-2454 run only once the repository adds
  `meow-markdown check` itself, and `bind` names it only as a comment.
- `build`, remark-lint, textlint, spelling and diagrams bind nothing.

## Why

RES-0111 found that no single Markdown exists, so a check needs the target, and
that the link check reaches outside the repository and so belongs under `test`
with its offline behaviour, retries and cache declared. RES-0294 observed that
lychee's exit status can't tell a site that is down from a broken link, and its
JSON can; that lychee takes its settings from `lychee.toml` and its flags; and
that markdownlint-cli ignores a markdownlint-cli2 configuration while
markdownlint-cli2 runs its defaults in silence where none exists. Each of those
is a case where the tool's own output reads the same whether the repository
got what it meant or not, which is what REQ-2434 and REQ-2438 ask a pack to
tell apart.

The strongest objection is that on this repository, the pack's only user so
far, `check` sees almost nothing: every verb reaches its tool through a mise
task, so it holds the render target and the markdownlint files, and the link
check here is `tools/check_links.py`, which reaches no network. The value lands
on a repository that binds its verbs to tools directly. I accept that, because
the pack is the protocol's first instance, and a repository with no runner is
the common case the protocol has to serve.

Premortem. A lychee release renamed `timeout_map`, and every run of `links`
reported `tool broken` for a month while CI stayed red. The table followed
lychee's JSON and no fixture ran a newer lychee. A deleted page returned 403
from a host that hides deletions, so `links` reported it as unreachable, never
as a finding, and it stayed in the corpus until a person clicked it.

## Alternatives

| Option                                                     | Better at                                                        | Why it lost                                                                                                                                                                                                          |
| ---------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bind `test` to `lychee` directly                           | No program between the verb and the tool                         | lychee exits 2 for a timeout as for a 404, so a site that is down reads as a broken document (RES-0294)                                                                                                              |
| Bind `lychee --accept-timeouts`                            | One flag, no program                                             | A timeout then passes, which reports a check that didn't run as passed, and a refused connection or a 503 still reads as broken                                                                                      |
| Declare the link check's settings in `[markdown.links]`    | One file holds every setting the harness checks                  | lychee never reads it, so the declaration and what the check does could disagree and nothing would notice                                                                                                            |
| Accept only a closed list of render targets                | A misspelt target is caught                                      | A repository on a renderer outside the list could never pass, and the requirement asks for a declaration, not one of ours                                                                                            |
| Put Markdown into `meow-prose`, which every repository has | No new unit to install                                           | `meow-prose` holds the writing standard and may name no tool, and this pack is made of tool names                                                                                                                    |
| Bind `check` to `meow-markdown check`                      | The settings checks run by default wherever `lint` runs a linter | `check` is the type check in every language, and a repository with code has one `check` verb, which its type checker holds, so a Markdown pack claiming it would take the verb from the code or give it two meanings |
| Wait for a shared detection engine for every pack          | Each later pack reuses one detector                              | It waits on decisions not yet made, and this pack works without one                                                                                                                                                  |
| Do nothing                                                 | No new unit                                                      | Six requirements stay unmet, and a Markdown repository writes each verb by hand with nothing checking the settings behind it                                                                                         |

## What it costs

Every repository that installs the pack keeps its skill description in context
on every turn, and `reviewing.md` costs context only when Markdown is reviewed.
`status`, `bind` and `check` run no tool, and read the profile, the tracked
file list and the configuration files. `links` reaches every remote address the
corpus cites on every run of `test`, which is the price of a link check at all.
A repository that turns lychee's cache on gets `.lycheecache` in its work tree,
and a finding until it ignores the file.

A repository that adopts `check` must write down three lychee settings it may
have been happy to leave at their defaults, and a render target it may never
have thought about. Whoever maintains `crates/meow` takes on a classification
table that follows lychee's JSON, which carries no stability promise; a lychee
that renames a map makes `links` report `tool broken` until the table follows.

## What would reverse it

I would drop the classification and bind lychee directly if lychee gave an
unreachable source an exit status of its own. I would let `meow-verbs` report
a `links` exit of 3 as unresolved, not failed, if a later decision gave a
verb's command a declared way to say it couldn't run. I would drop the finding
for a missing markdownlint configuration if markdownlint-cli2 started naming
the configuration it applied. I would bind `build` for a site generator once
its build command has been observed failing on a broken page. I would move
403 from `unreachable` to `finding` if a corpus's link check showed deleted
pages returning 403 more often than pages behind a login.

## Consequences

- A unit `meow-markdown`, with a program, a skill, `reviewing.md`, a README, a
  budget and a marketplace entry.
- A native feature `markdown` in `crates/meow`, built by `build-units`.
- Two specifications from the spec step: one stating the boundary every
  language pack keeps, and one for this pack.
- This repository's profile gains `[markdown] target = "github"`, appends
  `meow-markdown check` to its `lint` verb, its `test` verb runs the pack's tests, and
  the documentation index names the unit.

## How I will know it was realised

1. A fixture repository with two tracked `*.md` files is detected, one with a
   lone `README.md` isn't, and one with a lone README and a
   `.markdownlint.yaml` is.
2. Fixtures show `bind` printing `lint` for a `.markdownlint-cli2.yaml`, with
   `meow-markdown check` named in a comment, `lint` as `meow-markdown check`
   where no linter is configured, `format` for a `.prettierrc`, `check` as
   unresolved with its reason, `test` for a `lychee.toml`, `build` as unbound
   naming `mkdocs.yml` where one exists, and nothing for a verb the profile
   already declares.
   Another shows a `mise.toml` named with a pointer to the runner's pack.
3. `check` exits 1 naming the missing target where the profile has no
   `[markdown] target`, and 0 on a profile declaring `github` or `forgejo`.
4. `check` exits 1 on a `lint` verb running markdownlint-cli2 with no
   configuration, on one running `markdownlint` beside a
   `.markdownlint-cli2.jsonc`, naming the file, and on a directory holding both
   configuration families. This repository's `.markdownlint-cli2.yaml` is
   listed by `status` as read by markdownlint-cli2.
5. `check` exits 1 naming `max_retries` on a `lychee.toml` without it, 0 on one
   declaring all three settings, and 0 where a verb running `lychee` directly
   passes `--offline --max-retries 0 --cache=false`, which lychee 0.24.2
   accepts (RES-0294).
6. A stand-in lychee printing RES-0294's JSON with a timeout and a failed
   connection makes `links` print both as `unreachable` and exit 3, as do a
   403 and a 503. A 404 or a missing relative file exits 1 as a finding, a mix
   exits 1 with the unreachable addresses listed apart, a run with only
   excluded addresses prints them as `skipped` and exits 0, and no lychee on
   `PATH` prints `tool absent` and exits 3. A stand-in exiting 3, one printing
   text that isn't JSON, and one printing RES-0294's JSON with `timeout_map`
   renamed each make `links` print `tool broken` and exit 3. A stand-in whose
   JSON holds a rejected 3xx response, which no row matches, prints
   `unresolved` and exits 3. One run against the real lychee on a fixture with a missing
   relative file exits 1.
7. A test reads `reviewing.md` and finds each of RES-0111's reviewer points.
8. `git status --porcelain --ignored` reads the same before and after `status`,
   `bind` and `check`.
9. Every requirement ADR-1900 addresses lands in exactly one closed task, and
   REQ-2424 and REQ-2484 read as postponed.

## What this does not settle

- How a spell check is bound and where its word list lives, and how a Vale
  style is checked.
- Parsing a fenced diagram as part of lint.
- Binding `build` to a site generator, and binding remark-lint or textlint.
- Which verb runs `meow-markdown check` where `lint` is bound to a linter. It
  can't be `check`, as Alternatives says, and `lint` holds one command, so the
  answer needs either a verb that holds a chain of commands, which is the verb
  contract's to decide, or a pack that edits the profile, which this decision
  rules out.
- Reading the tasks a runner declares to see which tool a verb reaches.
- A shared detector every language pack uses, which the runner packs'
  marker work may bring.
- Whether a `test` verb whose command couldn't run is reported by
  `meow-verbs` as anything but failed.
