---
id: SPC-1080
artifact: spec
status: live
revised: 2026-09-30
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
    REQ-1186,
    REQ-1350,
    REQ-1351,
    REQ-1352,
    REQ-1353,
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
    REQ-1388,
    REQ-1392,
    REQ-1394,
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
    REQ-3178,
    REQ-3192,
    REQ-3320,
    REQ-3322,
    REQ-3324,
    REQ-3326,
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
decides how this repository's five verbs check the crate, and EPC-1570
realises that. BUG-1240 and TSK-2520 bring the launchers and the build
script under the same verbs. ADR-1800 adds the check that `project` groups
an issue nowhere, and EPC-1710 realised it, verified under issue 625. ADR-1810
sends every GitHub request through one layer, and EPC-1720 realises it.

## Boundary

| Surface                         | What it is                                                                 |
| ------------------------------- | -------------------------------------------------------------------------- |
| `crates/meow/`                  | The tool's source: one crate, with a feature per unit and its own tests    |
| `mise.toml`                     | The tasks that format, lint, check, test and build the crate and its shell |
| `plugins/<unit>/bin/<unit>`     | The unit's launcher, which picks the binary for the machine                |
| `plugins/<unit>/bin/<target>/`  | The unit's binaries, one per target, built and never committed             |
| `.github/workflows/build.yml`   | The six-target build, run by CI when the crate changes and by the release  |
| `.github/workflows/release.yml` | The release: one archive per unit, a marketplace file                      |
| `retran/meow.retran.me`         | The site serving the marketplace file at `meow.retran.me`                  |
| `plugins/meow-github/hooks/`    | The hook that runs `meow-github governance-guard` before a Bash command    |

## Behaviour

### One crate, a feature per unit

The crate `crates/meow/` builds one binary, `meow`, whose subcommands are the
units' programs: `verbs`, `scm`, `git`, `record`, `github`,
`licence` and `author`. Each
subcommand sits behind a feature named for its unit, and a unit's binary is
built with that unit's feature alone, so it carries its own code and nothing of
another unit's (REQ-0076). The profile reading, the report shapes and the exit
codes the units share are one module every feature uses.

### The launcher

`plugins/<unit>/bin/<unit>` stays the command a skill or hook runs. It names
the machine's target from the operating system and the processor, looks for
`bin/<target>/meow`, sets its executable bit if the delivery didn't keep it,
and runs it with the unit's subcommand and the arguments it was given. Where no
binary exists for the target, it reports every check as unrun and exits as the
unit's specification says a missing program does, never with success on a
check.

### The checks the crate passes

This repository's five verbs check the crate as they check every other file
it ships, so evidence kept from the verbs covers the code every unit runs
(REQ-1186). Each verb runs a task in `mise.toml`, and the gate's `all` task
depends on each of them apart from `build`, whose binaries CI builds in its own
workflow:

| Verb     | Task          | Runs on `crates/meow`                                                  |
| -------- | ------------- | ---------------------------------------------------------------------- |
| `format` | `crate-fmt`   | `cargo fmt --check`                                                    |
| `lint`   | `crate-lint`  | `cargo clippy --all-features --all-targets -- -D warnings`             |
| `check`  | `crate-check` | `cargo check --all-features --all-targets`                             |
| `test`   | `crate`       | `cargo test --all-features`                                            |
| `build`  | `build`       | `crates/meow/build-units`, one binary per unit for the machine it's on |

Each verb runs the crate's task after the checks it already runs on the
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

| Verb     | Task         | Runs                                  |
| -------- | ------------ | ------------------------------------- |
| `format` | `shell-fmt`  | `shfmt -i 2 -d` over the shell files  |
| `lint`   | `shell-lint` | `shellcheck`, at its default severity |

Both tasks take the list from `shfmt -f plugins crates/meow`, which picks a
file by its shebang, so a launcher added later is checked with no edit to
either task. Each task fails when the list is empty, because a check over
nothing is no pass. Each verb runs its shell task before the crate's, so the
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

Before it packs a unit, the release refuses one whose commits since its last
release include one marked breaking, with `!` or a `BREAKING CHANGE:` footer,
unless its version raises the major number, or the minor while the major is
zero (REQ-3192). A commit belongs to each unit whose directory it touches, and
one touching `crates/meow/` to every unit that ships the binary (ADR-1570).
`tools/check_release.py` makes the check, and the workflow runs it before
packing, with the full history so it can read each unit's tags.

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
method completes with none (REQ-1372, REQ-1376, REQ-1380). A repository
declares its tracker as `[tracker] kind` in its profile (REQ-1351).
`meow-github project <epic>` projects an approved epic's tasks through the
request layer, one issue each, citing the requirements and dependencies and
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

A replay changes nothing, a changed task updates its issue, an edited issue is
reported and left, a closed issue on an unmarked task is reported, the issue's
state is the tracker's and never written, and `--check` computes the state on
demand and writes nothing (REQ-1353, REQ-1355, REQ-1388, REQ-1392,
REQ-1394, REQ-1400). The docs give the `gh` commands that project a task by
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

## Failure paths

| Condition                                        | What happens                                                                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| No binary for the machine's target               | The launcher reports every check as unrun, never passed                                                      |
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
