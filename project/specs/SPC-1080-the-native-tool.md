---
id: SPC-1080
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#277"
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
    REQ-0074,
    REQ-0076,
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
    REQ-3178,
  ]
---

# The native tool

## Scope

This covers `meow`, the one command-line tool every unit's program is a
subcommand of: where its source lives, how a unit gets a binary built with its
own features, how a unit's launcher finds and runs it, and how a release ships
it. What each subcommand does is its unit's specification, which cites this one,
so this one names none of them.

ADR-1110 decides it, EPC-1080 realises it, and the `meow` crate with its
launchers and release implements it, verified under issue 160.

## Boundary

| Surface                         | What it is                                                                |
| ------------------------------- | ------------------------------------------------------------------------- |
| `crates/meow/`                  | The tool's source: one crate, with a feature per unit and its own tests   |
| `plugins/<unit>/bin/<unit>`     | The unit's launcher, which picks the binary for the machine               |
| `plugins/<unit>/bin/<target>/`  | The unit's binaries, one per target, built and never committed            |
| `.github/workflows/build.yml`   | The six-target build, run by CI when the crate changes and by the release |
| `.github/workflows/release.yml` | The release: one archive per unit, a marketplace file                     |
| `retran/meow.retran.me`         | The site serving the marketplace file at `meow.retran.me`                 |

## Behaviour

### One crate, a feature per unit

The crate `crates/meow/` builds one binary, `meow`, whose subcommands are the
units' programs: `verbs`, `scm`, `git` and `record`. Each subcommand sits behind
a feature named for its unit, and a unit's binary is built with that unit's
feature alone, so it carries its own code and nothing of another unit's
(REQ-0076). The profile reading, the report shapes and the exit codes the
units share are one module every feature uses.

### The launcher

`plugins/<unit>/bin/<unit>` stays the command a skill or hook runs. It names the
machine's target from the operating system and the processor, looks for
`bin/<target>/meow`, sets its executable bit if the delivery didn't keep it,
and runs it with the unit's subcommand and the arguments it was given. Where no
binary exists for the target, it reports every check as unrun and exits as the
unit's specification says a missing program does, never with success on a
check.

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
gate runs the crate's tests, and this repository's `test` verb runs the units'
fixtures against the launchers.

### A release

CI builds all six targets with `crates/meow/build-units <target>`, the script
the local build runs, on every pull request and push that changes the crate, a
unit's launcher or the build. A person runs the release workflow by hand, and
it calls that same build. It packs
each unit whose version has no release yet as a zip of the unit's tracked files
and its binaries, and publishes it as a release tagged `<unit>-v<version>`, so
each unit carries its own version (REQ-0074). A unit whose version already has
a release keeps its archive. A release named `marketplace` holds one
`marketplace.json` whose entries point at every unit's archive by `url` and
`sha256`. A person adds it by the address the next section gives. Claude Code
reads an address on `github.com` as a git repository, so the release's own copy
is added by downloading it and adding it by its path (RES-0274), which stays as
a fallback:

```bash
curl -fsSLo marketplace.json https://github.com/meowshed/meowpaw/releases/download/marketplace/marketplace.json
claude plugin marketplace add ./marketplace.json
```

A later release reaches that fallback when the file is downloaded again.

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

### What stays optional

The features of the tool that read the record and project it onto a tracker,
which later decisions add, are features no step of the method depends on
(REQ-0032). A unit is complete with the record kept by hand and no tracker.

### Adopted in part

A repository adopts any subset of the units, and each is a working harness on
its own: no file a unit ships reaches outside the unit's directory, which
`tools/check_standalone.py` holds (REQ-0012, REQ-0014, REQ-0034). Installing a
unit adds nothing to the repository, the record is optional and the other
units work without it, the harness names no language, its artifacts are plain
text, and a repository overrides a convention with a file of its own that wins
over the unit's (REQ-0010, REQ-0016, REQ-0018, REQ-0022, REQ-0024, REQ-0026,
REQ-0028, REQ-0030). A capability that isn't available is reported as
unresolved or unchecked, never replaced by a weaker one, and the report names
what would supply it: the profile's `[verbs]` for a verb, a reinstall for a
missing binary (REQ-0036, REQ-0038, REQ-0040) (ADR-1270).

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

## Failure paths

| Condition                              | What happens                                            |
| -------------------------------------- | ------------------------------------------------------- |
| No binary for the machine's target     | The launcher reports every check as unrun, never passed |
| The binary has lost its executable bit | The launcher sets it and runs the binary                |
| A unit's feature fails to build        | The gate fails, naming the unit                         |
| A target fails to build at release     | The release publishes nothing, and names the target     |
| The dispatch to the site fails         | The release stays published; the step fails, naming it  |
| The site's deployment fails            | The address keeps serving the previous file             |
