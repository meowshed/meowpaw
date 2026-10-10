---
id: SPC-1190
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-0083,
    REQ-2434,
    REQ-2438,
    REQ-0082,
    REQ-0085,
    REQ-0133,
    REQ-3048,
    REQ-2332,
    REQ-2334,
    REQ-2336,
    REQ-2338,
    REQ-2340,
    REQ-2342,
    REQ-2344,
    REQ-2346,
    REQ-2348,
    REQ-2350,
    REQ-2410,
    REQ-2412,
    REQ-2414,
    REQ-2416,
    REQ-2418,
    REQ-2420,
    REQ-2422,
    REQ-2426,
    REQ-2428,
    REQ-2430,
    REQ-2432,
    REQ-2436,
    REQ-2440,
    REQ-2442,
    REQ-2444,
    REQ-2446,
    REQ-2448,
    REQ-2450,
  ]
---

# The language packs

## Scope

This covers what every language pack keeps, whatever its language: how it
detects the language, what it runs, what it writes, where its settings live,
how it exits and what its skill carries. A pack's own document states its
detection markers, its bindings and its findings, and refers here for the
rest.

`meow-markdown` is the one language pack so far, with a document of its own. The
runner packs, SPC-1140 and SPC-1150, keep the same boundary for a runner and
aren't restated here. Running a bound stage is SPC-1040's.

ADR-1900 decides this part and EPC-1800 realised it, verified under issue 624.
ADR-2640 adds the versions a pack states and the configuration it writes,
ADR-2650 makes a pack activate where its marker is, ADR-2660 orders the
packs, and ADR-2670 adds the rules every pack keeps on what it runs, what it
reports, what it changes and what it keeps.

## Boundary

A language pack is a unit holding a program and a skill that tells the model
to use it:

| Surface                                 | What it is                                                  |
| --------------------------------------- | ----------------------------------------------------------- |
| `plugins/<pack>/bin/<pack>`             | The program, with at least `status`, `bind` and `check`     |
| `plugins/<pack>/skills/<name>/SKILL.md` | The skill, which names the program and forbids guessing     |
| A supporting file beside the skill      | What a reviewer needs beyond the commands, loaded on review |
| `plugins/<pack>/README.md`              | The unit's page                                             |
| `.meowpaw/profile.toml`, `[stages]`     | What `check` reads; the pack never writes it                |
| `.meowpaw/profile.toml`, `[<language>]` | The pack's own settings, in a table named for its language  |

The program writes no file, in the repository or outside it, and never writes
the profile or any tool's configuration, because the repository's declaration
comes first (REQ-0134) and a file the pack writes is a change nobody reviewed as
a diff. It prints what it would declare, and the repository commits it. It runs
one program, git, as `git ls-files` for the tracked file list and `git
check-ignore` for an ignored path. A command that runs the language's tools on
purpose, such as a link check, is named as such in the pack's document, and
`status`, `bind` and `check` run none.

Exit status, for every command:

| Status | Means                                                                   |
| ------ | ----------------------------------------------------------------------- |
| 0      | The command reported what it was asked, and found nothing               |
| 1      | The command found at least one finding                                  |
| 2      | The command line was wrong                                              |
| 3      | Nothing was a finding, and something was unresolved, absent or unusable |

## Behaviour

### Detection

A pack identifies the toolchain it serves by a marker file git tracks, such as
a manifest or a lockfile, and starts none of the language's tools to decide
(REQ-0133). It activates for each directory that holds a marker, and not once
for the repository, so a repository holding two languages has each pack
report for the directories its marker is in, and each report names the
directory it ran for (REQ-3048). A work tree the pack doesn't detect makes
every command print `unresolved: not a <language> repository` and exit 3.

### The supported packs

The harness gives each language a pack that follows this document, detected
from its marker, and ships them one at a time in this order:

| Order | Language                  | Marker                                                                  | Requirement        |
| ----- | ------------------------- | ----------------------------------------------------------------------- | ------------------ |
| 1     | Rust                      | `Cargo.toml`                                                            | REQ-2332           |
| 2     | TypeScript and JavaScript | `package.json`                                                          | REQ-2338           |
| 3     | Python                    | `pyproject.toml`                                                        | REQ-2336           |
| 4     | Go                        | `go.mod`                                                                | REQ-2334           |
| 5     | C#                        | a `.sln` or `.csproj` file                                              | REQ-2340           |
| 6     | Lua, and Neovim plugins   | a rockspec or `.luarc.json`; a `lua/` tree beside a `plugin/` directory | REQ-2342, REQ-2344 |
| 7     | Godot and GDScript        | `project.godot`                                                         | REQ-2346           |
| 8     | Starlark                  | a Bazel or Buck workspace file                                          | REQ-2348           |
| 9     | Scheme                    | a Scheme project file                                                   | REQ-2350           |

Each pack resolves the five stages for its language, bound from what the
repository commits or unresolved with a reason, and has its own document
beside this one once it ships. Lua and Neovim plugins share one pack, because
Neovim is the host that evaluates the plugin's Lua. `docs/README.md` lists
each pack with its state, as SPC-1110 states.

### `bind`

`bind` prints a `[stages]` table for the repository to paste. It binds each stage
from the configuration the repository commits, and never from what is
installed. It prints nothing for a stage the profile already declares. A stage
it doesn't bind is printed as a comment naming the reason: `# <stage>:
unresolved, <reason>` for a stage the language can't have, and `# <stage>:
unbound, <what the pack looked for>` for one it found nothing to bind. Where a
runner's configuration exists, `bind` names it and the runner's pack.

### `check`

`check` reads each stage's command in the profile. For each tool whose meaning
depends on settings more than on the command line, it reads those settings from
where the tool reads them, and reports each one that is absent, ignored or
overridden in silence as a finding naming the file or the setting (REQ-2434).
A setting the pack's own table declares is read from that table. A profile that
is missing or doesn't parse is reported as unresolved, exit status 3.

### A check that reaches outside the repository

A result caused by a source outside the repository, such as a site that is
down, a refused connection or a throttled request, is printed as
`unreachable`, with the tool's own words, and is never a finding (REQ-2438). A
tool that rejected its own configuration or read no input is printed as `tool
broken`, and one not on `PATH` as `tool absent`. Output the pack can't parse is
`tool broken`, never a pass. A result the pack can't classify is `unresolved`.
A command exits 1 where any result is a finding, and lists what was
unreachable apart from the findings; it exits 3 where nothing is a finding and
anything is unreachable, unresolved, absent or broken.

### What a pack runs

A pack runs what the repository configured, and nothing it chose:

- Where several tools serve one stage in the ecosystem, it binds the stage to
  the one the repository configured, and never picks between them (REQ-2420).
- It turns on no lint group, strictness setting or analysis level the
  repository didn't ask for (REQ-2422).
- Where the project declares an environment or a package manager, it runs
  each tool through it, and never through whatever the shell finds first
  (REQ-2426).
- Where the repository pins a toolchain version, it runs the stages under that
  version, and reports a difference between it and the installed one
  (REQ-2428).
- Where a host evaluates the language or the language has several
  implementations, it detects which one applies before it binds, and reports
  every stage unresolved until it has (REQ-2446).
- Where a build step has a prerequisite another form of the step performs
  implicitly, it performs the prerequisite explicitly (REQ-2448).

### What a pack reports it didn't check

- Where the bound tool covers less than the ecosystem's default, the pack
  runs the rest as well, or names what is no longer checked (REQ-2410).
- Where the language runs the examples in its documentation as tests, `test`
  runs them, and never resolves to a runner that leaves them out (REQ-2412).
- Where the language ships a detector for the defect class its programs most
  often have, such as a race detector, `test` turns it on, and a repository
  that turns it off has that recorded in the profile's table for the language
  (REQ-2414).
- A report of a clean stage names the rule groups or analyses enabled
  (REQ-2432), and where the tool hides findings below a level by default, the
  level it ran at (REQ-2444).
- A supply-chain check states whether it covers transitive dependencies and
  whether it reports a dependency's presence or its reachability (REQ-2436).

### What a pack never changes

- It never applies a fix its tool marks unsafe (REQ-2430).
- It reports a suggestion to use a newer language feature, and applies none
  during a check (REQ-2440).
- A stage leaves no file in the working tree, and where the tool writes output
  there by default, the pack points it outside the tree (REQ-2442).

### What a pack keeps

- Where the ecosystem has a machine-readable report format for a stage, the
  pack collects the result in it, and where none exists it says the evidence
  is captured output (REQ-2416).
- Where a stage's tool deletes files unless the run asks for them, the pack
  asks for them and names where it kept them (REQ-2418).
- Its document states which of the ecosystem's generated files are project
  state to commit and which are cache to ignore (REQ-2450).

### Its tool's configuration and its versions

A pack writes its tool's configuration to the project's conventions by
printing it for the repository to commit, as `bind` prints a `[stages]`
table, and amends an existing configuration the same way (REQ-0082). Its
README states the versions of its toolchain it is current as of, because a
tool's defaults change under the same command name (REQ-0085).

### The skill

The skill tells the model to run the program and never to guess a command. A
supporting file beside it carries what a reviewer of the language needs that no
command reports, and the skill loads that file when the language is reviewed,
not on every turn (REQ-0083). The skill names the tool versions the pack was
observed against.

## Failure paths

| State                                   | Reported as                                                 | Exit |
| --------------------------------------- | ----------------------------------------------------------- | ---- |
| The language isn't detected             | `unresolved: not a <language> repository`                   | 3    |
| The profile is missing or doesn't parse | `unresolved: <what is wrong with the file>`                 | 3    |
| A tool the command runs isn't on `PATH` | `tool absent: <tool>`                                       | 3    |
| A tool exits on its own configuration   | `tool broken: <tool> exited <n>: <its line>`                | 3    |
| A tool prints output of another shape   | `tool broken: <tool> printed <first line>`                  | 3    |
| The language's host isn't detected yet  | `unresolved: <host> not detected`                           | 3    |
| The pinned toolchain isn't installed    | `unresolved: <tool> <pinned> pinned, <installed> installed` | 3    |
| An unknown argument                     | the usage line                                              | 2    |
