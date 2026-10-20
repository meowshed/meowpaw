---
id: SPC-1390
artifact: spec
status: live
revised: 2026-10-20
states: [REQ-2350, REQ-2416, REQ-2420, REQ-2442, REQ-2446, REQ-2450, REQ-3048]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Scheme pack

## Scope

This covers `meow-scheme`, the language pack for Scheme projects. It states
what `status` detects, what `bind` prints and what `check` finds. Every rule
SPC-1190 states for a language pack holds here, and this document states only
what is Scheme's. It binds stages for Racket alone, and leaves coverage,
documentation generation and every other implementation's commands unbound.

ADR-2660 decides this pack and EPC-2560's TSK-5115 ships it.

## Boundary

| Surface                                          | What it is                                                      |
| ------------------------------------------------ | --------------------------------------------------------------- |
| `plugins/meow-scheme/bin/meow-scheme`            | The program: `status`, `bind` and `check`                       |
| `plugins/meow-scheme/skills/scheme/SKILL.md`     | The skill                                                       |
| `plugins/meow-scheme/skills/scheme/reviewing.md` | What a reviewer of Scheme needs beyond the program              |
| `plugins/meow-scheme/README.md`                  | The unit's page, with the toolchain versions it's current as of |

The program is the `scheme` feature of `crates/meow`. It runs git alone, as
`git ls-files` and `git check-ignore`, and starts no Scheme implementation
(SPC-1190). The pack reads no table of its own in the profile.

## Behaviour

### Detection

A directory activates the pack where git tracks an `info.rkt`, which marks
Racket, a `*.egg` file, which marks CHICKEN, or a `guix.scm`, which marks a
Guix package and so Guile (REQ-2350, RES-0110, RES-0360). A `*.scm` file
alone activates nothing, because it names Scheme and no implementation. Each
report opens with the directory's scope line and names the markers (REQ-3048).

### The implementation

The pack decides which implementation the directory's Scheme runs on before it
binds a stage (REQ-2446, RES-0110). One implementation's marker makes it that
implementation. A directory with markers of two prints `unresolved: Racket and
CHICKEN are all detected, so which one evaluates the language isn't known`,
and `bind` prints each of its stages unresolved with that reason, because a
command from the wrong implementation frequently succeeds and does something
else.

### What `bind` prints

Each command runs in the directory the markers activate, as `cd <directory> &&`
where that isn't the root:

| Stage    | Printed as                                           | When                                                       |
| -------- | ---------------------------------------------------- | ---------------------------------------------------------- |
| `format` | `# format: unbound, raco fmt has no check mode`      | Racket                                                     |
| `lint`   | `# lint: unbound, ...`                               | Always, because no linter is committed for any of them     |
| `check`  | `# check: unbound, ...`                              | Racket, because `raco make` writes `compiled/` beside code |
| `test`   | `raco test --table .`                                | Racket                                                     |
| `build`  | `# build: unbound, ...`                              | Racket, for the reason `check` gives                       |
| any      | `# <stage>: unbound, no command is bound for <name>` | CHICKEN or Guile                                           |

The pack binds Racket's tests because the repository's `info.rkt` is the tool
configuration it committed: `raco test` finds the tests there and nowhere else
(REQ-2420, RES-0110). It passes no `--make` and binds no `raco make`, because
only those write bytecode into the tree (REQ-2442, RES-0360, RES-0367). It
binds no `raco fmt`, because `raco fmt` prints the formatted program or
rewrites the file and reports no difference (RES-0360). The `test` command
runs in the directory holding `info.rkt`, because `raco test` searches a
directory and `info.rkt` names its paths relative to it (RES-0367).

Racket has no machine-readable report, so the evidence of `test` is captured
output with the table `--table` prints, and exit 0 means every test passed,
2 a timeout and 1 another failure (REQ-2416, RES-0110, RES-0367). CHICKEN's
and Guile's tests are a library that runs nothing, so no command exists to
bind from what the repository committed (RES-0110).

Where several directories activate, a stage joins each directory's command with
`&&`, and a directory that leaves the stage unbound or unresolved is a comment
naming the directory. `bind` prints nothing for a stage the profile declares,
exits 3 where any directory's implementation isn't known, and exits 0
otherwise.

### Generated files

`status` prints, for each Racket directory, `commit: info.rkt, which is project
state` and `ignore: compiled/, which is bytecode written beside each source`,
and for each directory the test paths `info.rkt` declares through
`test-omit-paths` and `test-include-paths`, or that it declares none and
`raco test` runs every file under the directory (REQ-2450, RES-0110,
RES-0360).

### What `check` finds

| Finding                                                        | When                                                                     |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `<stage> runs raco make or --make, which writes compiled/ ...` | A stage's command runs `raco make`, `raco test --make` or `raco test -y` |
| `<dir>: compiled/ isn't ignored`                               | A Racket directory and `git check-ignore` finds no rule ignoring it      |
| `<dir>: compiled/ is tracked: <file>`                          | Git tracks a file under `compiled/`                                      |

`check` exits 1 on any finding, and prints `no findings` with what it checked
and exits 0 when there is none (REQ-2442, REQ-2450).

## Failure paths

| State                                            | Reported as                                            | Exit |
| ------------------------------------------------ | ------------------------------------------------------ | ---- |
| No marker is tracked                             | `unresolved: not a Scheme repository`                  | 3    |
| A directory holds markers of two implementations | `unresolved: Racket and CHICKEN are all detected, ...` | 3    |
| The profile doesn't parse                        | `unresolved: the profile doesn't parse: ...`           | 3    |
| `check` finds no profile                         | `unresolved: no profile at .meowpaw/profile.toml`      | 3    |
| An unknown argument                              | the usage line                                         | 2    |
