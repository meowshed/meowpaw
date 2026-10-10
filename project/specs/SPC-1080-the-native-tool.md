---
id: SPC-1080
artifact: spec
status: live
revised: 2026-10-10
states:
  [
    REQ-0010,
    REQ-0012,
    REQ-0014,
    REQ-0016,
    REQ-0018,
    REQ-0022,
    REQ-0024,
    REQ-0026,
    REQ-0028,
    REQ-0030,
    REQ-0032,
    REQ-0034,
    REQ-0036,
    REQ-0038,
    REQ-0040,
    REQ-1364,
    REQ-1366,
    REQ-1370,
    REQ-1390,
    REQ-1398,
    REQ-2562,
    REQ-2570,
    REQ-2584,
    REQ-2586,
    REQ-2588,
    REQ-2824,
    REQ-3800,
    REQ-3900,
    REQ-3902,
    REQ-4000,
    REQ-4508,
    REQ-4500,
    REQ-4502,
    REQ-4504,
    REQ-4506,
    REQ-1186,
    REQ-1350,
    REQ-1351,
    REQ-1352,
    REQ-1354,
    REQ-1355,
    REQ-1356,
    REQ-1360,
    REQ-1368,
    REQ-1372,
    REQ-1376,
    REQ-1380,
    REQ-1382,
    REQ-1384,
    REQ-1386,
    REQ-1392,
    REQ-4700,
    REQ-4702,
    REQ-4704,
    REQ-4706,
    REQ-1396,
    REQ-1400,
    REQ-1402,
    REQ-1485,
    REQ-1720,
    REQ-1722,
    REQ-1724,
    REQ-1726,
    REQ-1728,
    REQ-1730,
    REQ-1732,
    REQ-1734,
    REQ-1736,
    REQ-1740,
    REQ-1742,
    REQ-1744,
    REQ-1746,
    REQ-1748,
    REQ-1750,
    REQ-1752,
    REQ-1754,
    REQ-1756,
    REQ-1758,
    REQ-1762,
    REQ-1766,
    REQ-2556,
    REQ-2558,
    REQ-2560,
    REQ-2564,
    REQ-2566,
    REQ-2568,
    REQ-2572,
    REQ-2574,
    REQ-2576,
    REQ-2578,
    REQ-2582,
    REQ-2826,
    REQ-2832,
    REQ-2906,
    REQ-2940,
    REQ-2942,
    REQ-2944,
    REQ-2946,
    REQ-2948,
    REQ-2950,
    REQ-3178,
    REQ-3192,
    REQ-3320,
    REQ-3322,
    REQ-3324,
    REQ-3326,
    REQ-1170,
    REQ-1172,
    REQ-1174,
    REQ-1176,
    REQ-1178,
    REQ-1180,
    REQ-1182,
    REQ-1184,
    REQ-1190,
    REQ-2784,
    REQ-2786,
    REQ-2788,
    REQ-2790,
    REQ-2792,
    REQ-1480,
    REQ-1481,
    REQ-1482,
    REQ-1483,
    REQ-1484,
    REQ-1488,
    REQ-1494,
    REQ-1738,
    REQ-2990,
    REQ-2994,
    REQ-2996,
    REQ-2998,
    REQ-3000,
    REQ-3002,
    REQ-3006,
    REQ-1486,
    REQ-2194,
    REQ-2218,
    REQ-0072,
    REQ-0084,
    REQ-0086,
    REQ-0088,
    REQ-0343,
    REQ-3040,
    REQ-1424,
    REQ-1429,
    REQ-2992,
    REQ-2358,
    REQ-2360,
    REQ-4142,
    REQ-4146,
    REQ-4148,
  ]
---

# The native tool

## Scope

This covers `meow`, the one command-line tool every unit's program is a
subcommand of: where its source lives, how a unit gets a binary built with its
own features, how a unit's launcher finds and runs it, and how a release ships
it. What each subcommand does is its unit's specification, which cites this
one, so this one names none of them.

ADR-1110 decides it, EPC-1080 realises it, and the `meow` crate with its
launchers and release implements it, verified under issue 160. ADR-1610
decides how this repository's five stages check the crate, and EPC-1570
realises that. BUG-1240 and TSK-2520 bring the launchers and the build
script under the same stages. ADR-1800 adds the check that `project` groups
an issue nowhere, and EPC-1710 realised it, verified under issue 625. ADR-1810
sends every GitHub request through one layer, and EPC-1720 realises it.
ADR-2500 decides the unattended install, and TSK-4600 realises it. ADR-2520
adds the release's attestation and the report of the trunk's protections, and
EPC-2420 realises them. ADR-2710 decides what a hook's launcher does with no
binary. ADR-2460 decides where the harness writes and that it never touches a
secret. ADR-2490, as ADR-2720 amends it, decides the interface page and its
generator. ADR-2650 adds the parts a repository declares and the profile
layered for each, ADR-2600 and ADR-2620 add keys to the table of keys,
ADR-2640 keeps every pack optional, and ADR-2660 names the code host and the
tracker the harness serves.

## Boundary

| Surface                         | What it is                                                                  |
| ------------------------------- | --------------------------------------------------------------------------- |
| `crates/meow/`                  | The tool's source: one crate, with a feature per unit and its own tests     |
| `.meowpaw/profile.toml`         | The shared profile, read at the repository root and committed               |
| `.meowpaw/profile.local.toml`   | The personal profile, `[stages]` only, excluded through `.git/info/exclude` |
| `mise.toml`                     | The tasks that format, lint, check, test and build the crate and its shell  |
| `plugins/<unit>/bin/<unit>`     | The unit's launcher, which picks the binary for the machine                 |
| `plugins/<unit>/bin/<target>/`  | The unit's binaries, one per target, built and never committed              |
| `.github/workflows/build.yml`   | The six-target build, run by CI when the crate changes and by the release   |
| `.github/workflows/release.yml` | The release: one archive per unit, a marketplace file                       |
| `retran/meow.retran.me`         | The site serving the marketplace file at `meow.retran.me`                   |
| `plugins/meow-github/hooks/`    | The hook that runs `meow-github governance-guard` before a Bash command     |

## Behaviour

### One crate, a feature per unit

The crate `crates/meow/` builds one binary, `meow`, whose subcommands are the
units' programs: `verbs`, `scm`, `git`, `record`, `github`,
`licence` and `author`. Each
subcommand sits behind a feature named for its unit. The core unit ships the one
build, with every unit's feature, for every platform the harness supports, and
a unit that runs a program declares the core unit under `dependencies` and no
other unit (REQ-4500, REQ-4502, ADR-2870). A unit's launcher reads the path of
the core unit's installed root from the core unit's data directory, which the
core unit's session start writes, and it reports each of its checks unresolved,
naming the core unit, where it finds none (REQ-4504, REQ-4506). Until EPC-2790
lands, a unit still carries a build of its own beside it. The profile reading,
the report shapes and the exit codes the units share are one module every
feature uses.

### The profile

The profile is TOML and permits comments before, beside and after its values
(REQ-3800).

The tool reads `.meowpaw/profile.toml` at the repository root, which is the top
of the version control working tree it runs in, or the current directory where
there is none, and never from a directory above the root (REQ-2940). Every
command that reads the profile prints its state on a line of its own,
`profile: <state>`, as one of three (REQ-2948):

| State         | Means                             | What follows                                                                                                                                        |
| ------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `absent`      | No file at the root               | Each unit does what its specification states for no profile, and `meow-checks` reports every stage unresolved as `no profile`                       |
| `unparseable` | The file exists and doesn't parse | The report carries the parser's message and the line it gives, every stage is unresolved, and no stage falls back to anything                       |
| `parsed`      | The file parses                   | The report names each key the table of keys doesn't list, one line a key, and the command goes on with the exit status it would have had (REQ-2942) |

The table of keys is one list in `crates/meow/src/profile.rs`. Each entry names
a key, such as `stages.test` or `commits.types`, and the reason nothing else
answers it: the ecosystem doesn't declare it, the platform doesn't own it, it
isn't prose, and detection can't produce it (REQ-2950). A pull request that
adds a key adds its entry, and a test fails on an entry with no reason. A key
is known when an entry names its path or a path below it, so `[stages.test]`
is known through `stages.test.command`. The keys below an entry with nothing
listed below it, such as each type under `commits.types`, are the
repository's own names, and the tool doesn't check them.

The report is these lines, each kind opening with its own first word:

```text
profile: unparseable
profile error: line 3: unclosed table, expected `]`
```

```text
profile: parsed
unknown key: stages.tset
```

A unit whose output already prefixes each line with its command, such as
`meow-git push-guard:`, prefixes these lines the same way. `paw` and
`meow-markdown bind` print them on standard error, because their standard
output is what a step reads or a person pastes, such as a template, an
identifier or a table for the profile.
Two hooks print nothing about the profile. `meow-loop`'s guard judges each tool
call during a run, and a line on every call would bury the refusals it exists
to make. `paw status --waiting` runs at the start of every session and says
nothing unless something waits, so a repository with no record
pays nothing for it.

A repository declares its parts in the root profile under `[parts]`, one
entry a part, naming the part and its directory, because only the project
knows what it is built from (REQ-0343). A part is a directory and never
assumed to be a unit of installation. Where a part's directory holds its own
`.meowpaw/profile.toml`, the tool reads it over the root's: a key the part
declares replaces the root's for that part, and the part's `[stages]` declares
every stage the part needs, because a stage the part leaves out is unresolved
there and never taken from the root (REQ-3040). A part's profile carries no
`[record]` or `[parts]` table, because the record stays at the root, and the
tool reports either as an unknown key. A repository that declares no
`[parts]` is one part, its root. The tool layers the profiles itself and
relies on no setting the platform inherits from a parent directory.

The table of keys lists `parts` for the parts, `record.kinds` for a kind a
repository declares, and `docs.diagrams` for the diagram notation, each with
its reason.

A personal profile, `.meowpaw/profile.local.toml`, sits beside the shared one
and holds `[stages]` only, in the forms the shared one takes. The tool reads it after
the shared profile, and a stage it sets replaces the shared one on that machine.
Any other table in it is an unknown key. `meow-checks local <stage> <command>`
writes a stage to it, creating the file where there is none, and in the same
step adds `/.meowpaw/profile.local.toml` to `.git/info/exclude` unless a line
there already excludes it, so no file the repository keeps changes (REQ-2944).
Every report that names a resolved stage names the file it came from.

A stage in the personal profile whose command starts with `~` or with an
absolute path outside the repository stays unresolved, of the kind
`machine path`, and the report names the path and says to find the tool
through the repository's toolchain declaration (REQ-2946). The same command in
the shared profile is not refused by this rule.

### The launcher

`plugins/<unit>/bin/<unit>` stays the command a skill or hook runs. It names
the machine's target from the operating system and the processor, looks for
`bin/<target>/meow`, sets its executable bit if the delivery didn't keep it,
and runs it with the unit's subcommand and the arguments it was given. Where no
binary exists for the target, it reports every check as unrun and exits as the
unit's specification says a missing program does, never with success on a
check. A launcher that a blocking hook runs denies instead, with exit 2 and
the command that installs the unit again, as SPC-1240 states (REQ-1426).

### Each subcommand makes one determination

`meow` is the helper the harness ships, and no unit ships a second one beside
it (REQ-1170). Each subcommand makes one determination, such as
`paw check coverage` or `paw ready <step>`, and reports it without choosing
what happens next (REQ-1174, REQ-1182). Its output is lines of text, each kind
of line opening with a first word the subcommand's help states, and the lines
stay the same from one release to the next unless the commit that changes one
is marked breaking. A test per subcommand pins its lines (REQ-1184).

Each subcommand's help names what a person reads to reach the same answer by
hand, so the method still runs where the tool is missing (REQ-1176). A step of
the method calls the subcommand that computes a count, a set difference,
coverage, staleness, a resolution or a match, and never computes one by
reading files itself (REQ-1172). A step that cites a subcommand's output as
evidence cites the command, its exit status, its output and the tree revision
it ran at (REQ-1178). Where the output contradicts what the step sees in the
tree, the step reports both and doesn't defer to the tool (REQ-1180). Where a
hook can run a subcommand before the model reads, the unit runs it from the
hook, as `meow-flow`'s `SessionStart` hook runs `paw status --waiting`
(REQ-1190).

### The public interface

The harness declares its public interface on one page,
`docs/interface.md`, which names the five stages and their outcomes,
the artifact kinds and their front matter, the record's paths and identifier
formats, the profile's keys, every subcommand of the tool, and the form of a
piece of evidence (REQ-2992). The tool generates the page from the
documentation comments on what it parses and reads: each subcommand, each
stage's outcomes, each kind and its fields, the layout's paths and identifier
formats, each entry in the table of keys and the ledger's record. Each entry
on the page carries its item's comment as its reason. `meow interface`
prints the page, and a crate test runs it and fails where the committed page
differs, or where an item carries no documentation comment. A change that
removes or renames an entry is a change to the interface, and its commit is
marked breaking (ADR-2490, ADR-2720).

### The checks the crate passes

The record check reports an approved requirement that no approved decision
addresses or postpones, and an approved addressing decision with no approved
epic or direct task (REQ-3900, REQ-3902). A decision that only postpones work
needs no implementation plan.

This repository's five stages check the crate as they check every other file
it ships, so evidence kept from the stages covers the code every unit runs
(REQ-1186). Each stage runs a task in `mise.toml`, and the gate's `all` task
depends on each of them apart from `build`, whose binaries CI builds in its own
workflow:

| Stage    | Task          | Runs on `crates/meow`                                                  |
| -------- | ------------- | ---------------------------------------------------------------------- |
| `format` | `crate-fmt`   | `cargo fmt --check`                                                    |
| `lint`   | `crate-lint`  | `cargo clippy --all-features --all-targets -- -D warnings`             |
| `check`  | `crate-check` | `cargo check --all-features --all-targets`                             |
| `test`   | `crate`       | `cargo test --all-features`                                            |
| `build`  | `build`       | `crates/meow/build-units`, one binary per unit for the machine it's on |

Each stage runs the crate's task after the checks it already runs on the
Markdown, prompts and fixtures, apart from `test`, which runs `crate` right
after `build-units` so a failing crate test stops the run before the fixtures
start. `.meowpaw/profile.toml` names each task
through `mise run`, so `meow-mise check` reads every one. The `fmt` task,
which writes, runs `cargo fmt` on the crate as well as Prettier on the
Markdown, so one command fixes a `format` failure of either kind.

`-D warnings` sits on the lint task's command line, and the manifest has no
`[lints]` table, so a warning fails `lint` and still leaves `cargo build`
and `build-units` producing a binary. The lint and the type check run with
every feature on, and a shipped binary carries one feature, so a warning that
only one feature alone produces passes both (ADR-1610). Clippy's lints are its
default set, as the Rust version `mise.toml` pins ships them.

### The checks the shell passes

Each launcher, each hook script a unit ships and `crates/meow/build-units` are
POSIX shell, and `format` and `lint` check them as they check the crate
(REQ-1186). `mise.toml` pins `shfmt` and `shellcheck`, and the gate's `all`
task depends on both tasks:

| Stage    | Task         | Runs                                  |
| -------- | ------------ | ------------------------------------- |
| `format` | `shell-fmt`  | `shfmt -i 2 -d` over the shell files  |
| `lint`   | `shell-lint` | `shellcheck`, at its default severity |

Both tasks take the list from `shfmt -f plugins crates/meow`, which picks a
file by its shebang, so a launcher added later is checked with no edit to
either task. Each task fails when the list is empty, because a check over
nothing is no pass. Each stage runs its shell task before the crate's, so the
crate's task stays last. The `fmt` task runs `shfmt -i 2 -w` over the same
list. Each unit's fixtures run its launcher with no binary beside it and
assert what it reports, so `test` fails when a launcher's fallback reads as a
pass.

### Six targets

| Target                       | Serves                                 |
| ---------------------------- | -------------------------------------- |
| `aarch64-apple-darwin`       | macOS on Apple silicon                 |
| `x86_64-apple-darwin`        | macOS on Intel                         |
| `aarch64-unknown-linux-musl` | Linux on ARM64, glibc and Alpine alike |
| `x86_64-unknown-linux-musl`  | Linux on x64, glibc and Alpine alike   |
| `aarch64-pc-windows-msvc`    | Windows on ARM64                       |
| `x86_64-pc-windows-msvc`     | Windows on x64                         |

### Building locally

`mise run build` builds each unit's binary for the machine it runs on into the
unit's `bin/<target>/`, which `.gitignore` excludes, so a checkout loaded in
place by a local-directory marketplace runs the tool without a release. The
gate runs the crate's tests, and this repository's `test` stage runs the units'
fixtures against the launchers.

### A release

CI builds all six targets with `crates/meow/build-units <target>`, the script
the local build runs, on every pull request and push that changes the crate, a
unit's launcher or the build. Every target builds under Linux: the two musl
targets natively on their matching runners, the two darwin targets through
osxcross in a container, and the two windows targets through cargo-xwin,
which fetches the Windows SDK from Microsoft's servers. A darwin binary
built this way carries no signature, so CI writes the ad-hoc signature with
`ldid` before packing, and the installer signs again with `codesign` after
download, because macOS kills an unsigned arm64 binary on sight and a
person who places a binary by hand bypasses both. A person
runs the release workflow by hand, and
it calls that same build. It packs
each unit whose version has no release yet as a zip of the unit's tracked files
and its binaries, and publishes it as a release tagged `<unit>-v<version>`, so
each unit carries its own version (REQ-4508). A person also releases by
pushing the unit's tag from the trunk, which releases that unit alone and,
for a unit the Pi registry mirrors, publishes its npm package from the
tag (REQ-4146). A unit tag is cut from the marketplace release's tree at
most once per release, and a unit's version is one number on every agent
platform: the npm registry's versions are immutable and never moved
(REQ-4148). A unit whose version already has
a release keeps its archive. A release named `marketplace` holds one
`marketplace.json` whose entries point at every unit's archive by `url` and
`sha256`. A run for one unit's tag packs that unit alone and takes the other entries
from the file already published, and it fails before it publishes a file that
holds a relative `source` (REQ-1485). A person adds it by the address the next section gives. Claude Code
reads an address on `github.com` as a git repository, so the release's own copy
is added by downloading it and adding it by its path (RES-0274), which stays as
a fallback:

```bash
curl -fsSLo marketplace.json https://github.com/meowshed/meowpaw/releases/download/marketplace/marketplace.json
claude plugin marketplace add ./marketplace.json
```

A later release reaches that fallback when the file is downloaded again.

Before it packs a unit, the release refuses one whose commits since its last
release include one marked breaking, with `!` or a `BREAKING CHANGE:` footer,
unless its version raises the major number, or the minor while the major is
zero (REQ-3192). A commit belongs to each unit whose directory it touches, and
one touching `crates/meow/` to every unit that ships the binary (ADR-1570).
`tools/check_release.py` makes the check, and the workflow runs it before
packing, with the full history so it can read each unit's tags.

The job that publishes produces a build provenance attestation for each
archive with `actions/attest-build-provenance`, so a consumer checks what an
archive was built from, without trusting the publisher, by running
`gh attestation verify <archive> --repo meowshed/meowpaw` (REQ-2218). That job
alone holds `id-token: write` and `attestations: write`, beside the
`contents: write` it already holds. A run that doesn't publish attests
nothing.

A person installs a released unit from that marketplace and never needs Rust,
Python or Node.js. The repository's own `marketplace.json` keeps its relative
paths for development. Run without publishing, the workflow builds and packs
only, and leaves the archives, their sizes and their SHA-256 as a workflow
artifact.

### The marketplace address

The released `marketplace.json` is served at
`https://meow.retran.me/meowpaw/marketplace.json`, and a person adds it once,
by its address (REQ-1485):

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
```

Claude Code reads that address as a `url` marketplace (RES-0275), so
`claude plugin marketplace update meowpaw` fetches the file again and brings a
later release. A person who turns on auto-update for the marketplace under
`/plugin` gets each release without running anything.

The file is served by the Pages site of `retran/meow.retran.me`, which the
owner's personal account owns, because `retran.me` is verified for that
account and only its repositories may publish to the domain's subdomains. A
`CNAME` record for `meow` at EuroDNS points at `retran.github.io`. The site's
workflow downloads the `marketplace` release's `marketplace.json` and deploys
it at `meowpaw/marketplace.json`. It runs on a `repository_dispatch` of type
`meowpaw-release`, which the release workflow sends after publishing with the
secret `MARKETPLACE_DISPATCH_TOKEN`, a fine-grained token that can write to
that repository alone, and it runs when someone starts it by hand.

### Each unit is a plugin

Each unit installs through the platform's plugin mechanism from
`.claude-plugin/marketplace.json`, and no unit ships an installer of its own
(REQ-1480).

A machine-provisioning system installs and configures the harness with no
person and no prompt by running the platform's own commands,
`claude plugin marketplace add <address>` and
`claude plugin install <unit>@meowpaw`, which take every argument on the
command line (REQ-1486). `docs/README.md` gives those commands as the
unattended form. A test under `tools/`, run by the `test` stage, runs them
against a scratch configuration directory and fails on a unit the platform
doesn't list as enabled afterwards. Where the platform's command-line tool
isn't installed, the test reports itself as skipped with that reason, and
never as passed. Each carries a version in its `.claude-plugin/plugin.json`
(REQ-2990), and every version's major number stays zero while the public
interface still moves (REQ-2994). A released version never changes: the
release exits 1 before it packs anything, naming each unit whose tracked files
differ from its last release tag while its version still equals that tag's,
so a change ships only as a new version (REQ-2996).

Units reach each other only through files and commands (REQ-1481), and no
unit's behaviour depends on the order in which the platform runs hooks from
several units (REQ-1483). Each unit's `requires.toml` states:

| Key           | What it states                                                             |
| ------------- | -------------------------------------------------------------------------- |
| `claude_code` | The platform version the unit was tested on                                |
| `layer`       | `kernel`, `method`, `practice` or `pack`                                   |
| `units`       | The units it needs, as a list, empty where it needs none (REQ-1482)        |
| `kernel`      | In a pack only, the range of `meow-core` versions it works with (REQ-2998) |

`meow-author check` fails a unit with no version, no `requires.toml`, no
`layer` or `units`, or a pack with no `kernel` range. Where a unit names
another in `units`, the platform enables the one required and won't disable it
while the first is on, and the unit's README says so where it recommends the
install (REQ-3006). A unit's launcher run on a platform older than its
`claude_code` prints both versions and exits 3 without running the binary
(REQ-1738).

A repository's configuration and record live in the repository, so an
upgrade keeps both, and no unit stores anything that must survive an upgrade
under its own installed root (REQ-1484, REQ-3000). Machine-specific or secret
configuration lives in the user's own settings, never in a file the
repository keeps or in a unit's files (REQ-1488). Every file of configuration
the harness owns is TOML (REQ-1494). A unit's release carries the notes its
author wrote for the person whose repository changes, from the section for
that version in the unit's `CHANGELOG.md`, and never notes generated from
commits; the release refuses a new version whose changelog has no section for
it (REQ-3002).

### What stays optional

The features of the tool that read the record and project it onto a tracker,
which later decisions add, are features no step of the method depends on
(REQ-0032). A unit is complete with the record kept by hand and no tracker.

Knowledge of a language, a platform, a domain or an external tool lives in a
pack, a unit a repository may leave out, and the tools the harness itself
uses, such as `git`, `gh` and `mise`, live in packs of the same kind:
`meow-git`, `meow-github` and `meow-mise` (REQ-0072, REQ-0084). The method
assumes no external tool is present, no step, gate or obligation needs a
pack, and the method completes with none installed, each capability a missing
pack would supply reported as unresolved (REQ-0086, REQ-0088) (ADR-2640).

### What the harness writes and reads

The harness writes outside the repository only to its own run state under
`<state>/meowpaw/` and to the record at the location the profile declares,
and a unit test in the crate fails where a subcommand writes anywhere else
(REQ-1429). It never reads, prints or sends a repository's secret material,
and never puts it in an artifact (REQ-1424). `meow-core`'s output style
states that rule for every repository, because a constitution is one of
several documents loaded and a repository's own may not carry it, and
CLAUDE.md's `never_touch_secrets` states it for this one. No program can
show the rule holds, so the instruction and review hold it (ADR-2460).

### Adopted in part

A repository adopts any subset of the units, and each is a working harness on
its own except for the core unit it depends on: no file a unit ships reaches
outside the unit's directory, and a unit names the core unit and no other under
`dependencies`, which `tools/check_standalone.py` holds (REQ-0012, REQ-0014,
REQ-0034, REQ-4502). Installing a
unit adds nothing to the repository, the record is optional and the other
units work without it, the harness names no language, its artifacts are plain
text, and a repository overrides a convention with a file of its own that wins
over the unit's (REQ-0010, REQ-0016, REQ-0018, REQ-0022, REQ-0024, REQ-0026,
REQ-0028, REQ-0030). A capability that isn't available is reported as
unresolved or unchecked, never replaced by a weaker one, and the report names
what would supply it: the profile's `[stages]` for a stage, a reinstall for a
missing binary (REQ-0036, REQ-0038, REQ-0040) (ADR-1270).

### Reading a code host's history

The feature `github` carries `history`, which `meow-github` ships: it reads a
GitHub repository's issues, pull requests with whether each merged,
conversation comments and review comments through the request layer, one page
a call, following each listing's `Link` header with `--cache 1h`, and prints
them as one JSON document (REQ-2826, REQ-2906, REQ-2558, REQ-2560, REQ-2564).
It takes each field by name and fails by name on a missing one (REQ-2556),
writes nothing to the code host (REQ-2832), and reports a refused, throttled or
impossible read as unread, naming the listings it read, with no partial
document (ADR-1290). The document also carries `credential`, the credential's
form, and `budget`, the budget lines the next section states (REQ-2568,
REQ-2582) (ADR-1810).

### Reporting the trunk's protections

The feature `github` carries `protections`, which `meow-github` ships: it reads
the protection of the trunk the profile declares as `[git] trunk`,
`repos/{r}/branches/{trunk}/protection`, and the rules in force on that branch,
`repos/{r}/rules/branches/{trunk}`, through the request layer, and writes
nothing (REQ-2194). A protection a ruleset sets counts as in force. It prints
one line for each of six protections, in this order, each as
`<protection>: in force` or `<protection>: absent`:

1. `force pushes blocked`
2. `deletion blocked`
3. `required reviews`
4. `required checks`
5. `signed commits`
6. `linear history`

A 404 answering that the branch isn't protected makes every classic
protection absent, and the rules are still read. A refused or throttled read
is reported as the request layer reports it, with every protection it didn't
read named as unread, never as absent, and exits 3. Where no trunk is
declared, `protections` says so and exits 3 (ADR-2520).

### The GitHub request layer

Every request `meow-github` sends to GitHub goes through one request layer,
`crates/meow/src/github/request.rs`, and no other code in the `github` feature
starts `gh`. The layer runs `gh api --include`, so it reads the status line,
the headers and the body of every response, a refused one included. Naming the
repository reads `repos/{owner}/{repo}` through it (ADR-1810).

The layer reads `x-ratelimit-limit`, `x-ratelimit-remaining`,
`x-ratelimit-used`, `x-ratelimit-resource`, `x-ratelimit-reset`, `retry-after`
and `Date` on every response, matching the names without regard to case. It
records a response carrying none of them as carrying none, and the run goes on
(REQ-2566). The layer sends a run's first call without `--cache`, and each
uncached response, every write among them, records the offset between its
`Date` and the local clock when it arrived. A cached response is a replay when
its `Date` is 60 seconds or more before the moment the layer started the call,
moved onto GitHub's clock by that offset. The layer doesn't read a replay's
limit headers as current and doesn't count it as a request (REQ-2566).

One table per service turns a header into a wait, and no other code converts
a header into a duration (REQ-2578). A value that doesn't parse in its unit
gives no wait: the run reports the wait as unknown, sends nothing more and
exits 3. GitHub's rows:

| Header              | Unit              | The wait it gives                                            |
| ------------------- | ----------------- | ------------------------------------------------------------ |
| `retry-after`       | seconds           | that many seconds from when the response arrived             |
| `x-ratelimit-reset` | UTC epoch seconds | the reset minus the response's `Date`, from when it arrived  |
| `Date`              | HTTP date         | none; it is the reference `x-ratelimit-reset` is measured to |

A response is throttled when it is a 429, or a 403 carrying `retry-after`,
`x-ratelimit-remaining: 0` or a message naming a secondary rate limit. Its
wait is `retry-after` where present, the reset where `remaining` is 0, and
otherwise 60 seconds, doubled for each further secondary throttle in the same
run. A fresh response with `remaining` at 0 holds the next request to the same
resource the same way. By default the run then sends nothing more, the
read-back listing included, prints
`throttled: <method> <endpoint>, retry after <UTC time> (<header>)` and exits
3 (REQ-2566). With `--wait`, which `history` and `project` both accept, the
layer sleeps until that time, never less, and sends the throttled request
again. Where the waits the run has slept, with this one added, would pass an
hour, it starts no sleep and stops as throttled.

The layer keeps four counts for the run, checks them before each request, and
prints them as the last lines of every run's report (REQ-2568):

- primary requests: the requests the run sent, and for each
  `x-ratelimit-resource` the limit, remaining and reset the last fresh
  response stated, the limit read from `x-ratelimit-limit`;
- secondary points: 1 for each `GET` and 5 for each other method, over the
  last minute, against 900;
- content creation: each `POST`, over the last minute against 80 and over the
  last hour against 500;
- spacing: writes go one at a time, each at least one second after the
  previous one.

A request that would pass a ceiling isn't sent: the run stops as it does at a
throttle, naming the count and when it frees. Each count covers the run alone.

The first line of `project`'s report names the credential's form:
`GH_TOKEN from the environment`, `GITHUB_TOKEN from the environment` or
`gh's stored credential`, in the order of precedence `gh` documents, with
`, inside a GitHub Actions workflow` added when `GITHUB_ACTIONS` is `true`
(REQ-2582). The layer reads whether each variable is set and never its value.

A 401 is reported as `unauthenticated: <method> <endpoint>`, and a 403 that
isn't a throttle as `refused: <method> <endpoint> needs <permission>`
(REQ-2574). A 404 on an object the record says exists is reported the same
way with `, or it is hidden from this credential` added. The permission comes
from `X-Accepted-GitHub-Permissions`, and otherwise from
`X-Accepted-OAuth-Scopes` beside the credential's own `X-OAuth-Scopes`. Where
both are empty, the report says `GitHub named no permission` and quotes
GitHub's message. Every other line ends with `; GitHub said "<message>"`
where GitHub's answer carries a message, so each report carries GitHub's own
reason (REQ-3324). Each exits 3.

After a 401 the layer sends no further request in the run, because GitHub
rejects an account's valid credentials too after several rejected requests
(REQ-3326). `project` then stops as it does at a throttle, and `history`
reports the listing unread (ADR-2330).

The layer sends a write only to an endpoint on its allow list,
`POST repos/{r}/issues` and `PATCH repos/{r}/issues/{n}`, and refuses any other
method than `GET` before `gh` starts, as
`refused by meow-github: <method> <endpoint> isn't a write this pack makes`
(REQ-2576). The crate holds a governance list, and no allow-list entry matches
it: `repos/{o}/{r}` itself, `branches/{b}/protection`, `rulesets`,
`actions/permissions`, `actions/workflows/{id}/enable` and `/disable`,
`actions/secrets`, `actions/variables`, `environments`, `hooks`,
`collaborators` and `contents/.github/workflows/`, each with everything under
it.

`meow-github` ships a `PreToolUse` command hook on Bash that runs
`meow-github governance-guard` on every command containing `gh` as a word
(REQ-2576). The guard splits the command at `&&`, `||`, `;`, `|` and each new
line, skips a part's leading variable assignments and a leading `env` with its
assignments, and reads the part only when the next word is `gh`. It answers
`ask` for a part that is one of these:

- `gh api` to a path on the governance list with a method other than `GET`,
  or with a field or an `--input` body and no method;
- `gh api graphql` whose query contains `mutation`, or comes from a file or
  from standard input;
- `gh repo edit`, `gh repo rename`, `gh repo archive` or `gh repo delete`;
- `gh workflow enable` or `gh workflow disable`;
- `gh secret` or `gh variable` with `set` or `delete`.

Its reason names the method and the endpoint and never the command. For any
other command it prints nothing and exits 0.

### Projecting the record onto a tracker

The record is the system of record and a tracker a projection of it, and the
method completes with none (REQ-1372, REQ-1376, REQ-1380). `meow-github`
serves the code host GitHub, creating, linking and reading back the issues an
epic projects onto (REQ-2358), and GitHub Issues as the tracker, projected as
a mapping from each task to its issue and never as an integration that keeps
state of its own (REQ-2360) (ADR-2660). A repository
declares its tracker as `[tracker] kind` in its profile (REQ-1351).
`meow-github project <record>` projects the tasks of an approved epic, an
approved defect that carries tasks directly, or an approved decision realised
without an epic. It selects defect tasks by their `bug` field, derives their
completion from the defect's task marks and otherwise uses the same mapping,
replay, read-back, disagreement and failure behaviour (REQ-4000). The command
uses the request layer, one issue for each task, citing the requirements and dependencies and
marked as a synchronisation's write, and records `issue:` and `projected:` on
the task (REQ-1350, REQ-1352, REQ-1354, REQ-1356, REQ-1360, REQ-1382,
REQ-1384, REQ-1386, REQ-1396). After its last create it reads the issues it
created back in one uncached, paged listing,
`repos/{r}/issues?state=all&since=<start>&per_page=100`, where `<start>` is
the earliest `updated_at` among the create answers of the run, or the `Date`
of the run's first response where no create answer carries one, and matches
each by number (REQ-3322) (ADR-2320). It then reads by number,
`repos/{r}/issues/{n}`, uncached, each created issue the listing left out,
because the listing can lag a create by seconds, and stops these reads at a
throttle, a ceiling or a 401 (REQ-3322) (ADR-2340). It reads
an issue already mapped to a task on its own, and each link is read back from
the tracker, in this run's listing or through its mapping in the next run
(REQ-1368). The listing runs after a failed write or a refusal, and not after
a throttle, a ceiling or a 401 (ADR-1810, ADR-2330).

A replay changes nothing and a changed task updates its issue. `meow-github
sync` compares each task with its issue by a fingerprint of each side taken at
the last synchronisation: the side that changed is applied to the other, the
record's text is applied where both changed, an approved record is never
reworded from the tracker and its difference is reported, and the issue's state
still flows to the record (REQ-4700, REQ-4702, REQ-4704, ADR-2890). A closed
issue on an unmarked task is reported, and `--check` computes the state on
demand and writes nothing (REQ-1355, REQ-1392, REQ-1400). The method runs the
synchronisation at the start and the end of an epic's work and nothing runs it
in the background (REQ-4706). The docs give the `gh` commands that project a task by
hand, the headers to read and the one-second spacing between writes
(REQ-1402) (ADR-1310, ADR-1810).

Whenever `project` stops before it has projected every task, or holds a
created issue it didn't read back, it prints
`partial: projected TSK-a; created, not read back TSK-b; not projected TSK-c`
after the read-back listing, where the listing runs, and exits 3 (REQ-2572).
A task is projected when its issue was updated or found unchanged in this run,
or was created and read back matching the record. A created issue that neither
the listing nor its read by number shows as written goes under
`created, not read back`, with the reason. Its task holds the mapping, so the
next run reads that issue through it and creates no second one.

`project` groups an issue nowhere: it passes no `--milestone`, `--parent`,
`--project` or `--label` and creates no blocked-by relation, and the issue's
body carries each dependency line with its `(blocking)` or `(not blocking)`
marker as the task writes it (REQ-3320) (ADR-1800).

### Quality attributes

The commands that read the record write nothing and print the same text run
twice with nothing changed, and a step reads the chain's state from the
artifacts alone (REQ-1720, REQ-1728, REQ-1730, REQ-1732). `index --write`
writes to a temporary file and renames it into place, so an interruption never
leaves an index half-written (REQ-1722, REQ-1724). Each unit declares the
Claude Code version it needs in `requires.toml`, and its page names the
platform behaviours it relies on with where each is documented (REQ-1736,
REQ-1740, REQ-1742). A unit that fails degrades alone through its launcher's
fallback (REQ-1726), the record's shape changes by expand, migrate and
contract (REQ-1744, REQ-1746), the kernel works installed alone (REQ-1748), a
unit's description states its job and cost (REQ-1750), the record uses no
syntax of its own (REQ-1752), every check runs locally by the command CI runs
(REQ-1754, REQ-1756, REQ-1758), tools come from `mise.toml` (REQ-1762), no
spend happens without a person (REQ-1766), and every report separates what was
verified from what was assumed (REQ-1734) (ADR-1200).

### The threat model

The harness keeps one threat model, here, and it changes in the pull request
that adds or removes a trust boundary. It considers accidents by a legitimate
insider before attackers (REQ-2784), and the first insider it names is the
harness itself, acting on a repository it has just met (REQ-2792).

Data changes trust level at four boundaries, and every threat below crosses
one of them (REQ-2788):

| Boundary              | What crosses it                                                                  |
| --------------------- | -------------------------------------------------------------------------------- |
| The repository's text | A file the harness reads into a prompt, written by whoever committed it          |
| The tracker           | An issue's title and body, which anyone with access to the tracker can write     |
| The code host's talk  | A pull request comment or review comment, read back by `meow-github history`     |
| A tool's output       | What a command prints, read by the model as a result and never as an instruction |

Each threat is ranked in words, as likely or unlikely and as severe or minor,
and carries no numeric score (REQ-2790). The insiders come first:

| Threat                                                                | Likelihood | Impact | Control                                                                                                                |
| --------------------------------------------------------------------- | ---------- | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| The harness runs a destructive command on a repository it misread     | likely     | severe | `meow-flow:route` before any edit, `meow-git`'s trunk and push guards, and the governance guard above                  |
| The harness reports a check as passed with nothing behind it          | likely     | severe | `meow-checks` never reports an unresolved stage as passed, and every report separates verified from assumed (REQ-1734) |
| The harness rewords an approved record to match what was built        | likely     | minor  | `paw check frozen`                                                                                                     |
| The harness changes configuration outside the repository              | unlikely   | severe | The crate's unit tests on `git config --global` and `--system`, and on a write outside the run state and the record    |
| The person's own session reads or prints a secret from the repository | unlikely   | severe | The instruction alone: `meow-core`'s output style and `CLAUDE.md`'s `never_touch_secrets`; no program checks it        |
| Text across a boundary instructs the model to act                     | likely     | severe | None by program; a shipped agent ends `BLOCKED` on a denied call, which limits what it reaches                         |
| A commit claims an author who didn't make it                          | unlikely   | severe | `meow-git`'s push guard accepts only a good signature from a trusted key                                               |
| A released archive is replaced                                        | unlikely   | severe | `marketplace.json` names each archive's SHA-256 (the release above)                                                    |
| A run spends a code host's request budget                             | unlikely   | minor  | The request layer's counts and ceilings (the request layer above)                                                      |

The model works through STRIDE, the six categories OWASP's threat-modelling
process uses, and maps each to the control that answers it, or says none does
(REQ-2786):

| Category               | Control                                                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Spoofing               | The push guard's signature check, and the credential's form named by `meow-github`                                                       |
| Tampering              | `paw check frozen` on approved records, the SHA-256 of each released archive and its build provenance attestation                        |
| Repudiation            | Signed and signed-off commits, and one squashed pull request per task                                                                    |
| Information disclosure | None by program; the instruction in `CLAUDE.md` alone                                                                                    |
| Denial of service      | The request layer's ceilings for the code host; none for a slow hook                                                                     |
| Elevation of privilege | The governance guard's `ask`, the write allow list, and `meow-author check` refusing `Agent`, `Task` or `*` in a shipped agent's `tools` |

## Failure paths

| Condition                                        | What happens                                                                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| No binary for the machine's target               | The launcher reports every check as unrun, never passed; a blocking hook's launcher denies, naming the fix   |
| A part's profile carries `[record]` or `[parts]` | The table is reported as an unknown key, and the root's record and parts stand                               |
| A part's profile leaves out a stage              | That stage is unresolved in that part, and never taken from the root's profile                               |
| The committed interface page differs             | The crate's test fails, naming the entry that differs; regenerating the page fixes it                        |
| The profile doesn't parse                        | `profile: unparseable` with the parser's message and line; every stage unresolved, nothing falls back        |
| The profile carries a key the table doesn't list | The key is named on a line of its own, and the exit status stays what it would have been                     |
| A personal stage names a path on this machine    | The stage is unresolved, of the kind `machine path`, naming the path                                         |
| `local` outside a git working tree               | Refused, exit 1, because nothing can exclude the personal file there                                         |
| A unit changed since its release, same version   | The release exits 1 before packing, naming the unit                                                          |
| A new version with no changelog section          | The release exits 1 before packing, naming the unit and the version                                          |
| The platform is older than `claude_code`         | The launcher prints both versions and exits 3, running nothing                                               |
| The platform's version can't be read             | The launcher says so and runs the binary, because an unknown version isn't an older one                      |
| The binary has lost its executable bit           | The launcher sets it and runs the binary                                                                     |
| A unit's feature fails to build                  | The gate fails, naming the unit                                                                              |
| The crate isn't in the formatter's form          | `format` and the gate fail, naming each file                                                                 |
| Clippy reports a finding                         | `lint` and the gate fail, naming the lint and the line                                                       |
| The crate fails its type check                   | `check` and the gate fail, naming the error                                                                  |
| The toolchain lacks rustfmt or clippy            | `format` or `lint` fails with cargo's own error                                                              |
| A shell file isn't in shfmt's form               | `format` and the gate fail, showing the diff                                                                 |
| Shellcheck reports a finding                     | `lint` and the gate fail, naming the code and the line                                                       |
| A target fails to build at release               | The release publishes nothing, and names the target                                                          |
| The dispatch to the site fails                   | The release stays published; the step fails, naming it                                                       |
| The site's deployment fails                      | The address keeps serving the previous file                                                                  |
| GitHub throttles a request                       | The run sends nothing more, prints `throttled`, the endpoint and when to retry, and exits 3                  |
| A throttle with `--wait`                         | The layer sleeps until the stated time and resends, and stops as throttled once the waits would pass an hour |
| A limit header's value doesn't parse in its unit | The wait is reported as unknown, the run sends nothing more and exits 3                                      |
| A request would pass a budget's ceiling          | It isn't sent, and the run stops as at a throttle, naming the count and when it frees                        |
| `project` stops before visiting every task       | It prints `partial:` with what it projected, created and didn't project, and exits 3                         |
| GitHub answers 401                               | `unauthenticated:` with the method and endpoint, exit 3                                                      |
| GitHub answers a 403 that isn't a throttle       | `refused:` with the method, endpoint and permission, or GitHub's message, exit 3                             |
| GitHub answers 404 on a mapped object            | As a 403, adding that it may be hidden from this credential, exit 3                                          |
| A write to an endpoint off the allow list        | Refused before `gh` starts, naming the method and the endpoint                                               |
| A Bash command's `gh` changes governance         | The hook answers `ask`, naming the method and the endpoint                                                   |
| `protections` can't read a protection            | The protection is named as unread, never as absent, exit 3                                                   |
| The platform's command-line tool is missing      | The unattended install test reports itself skipped, never passed                                             |
