---
id: SPC-1200
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-2370,
    REQ-2380,
    REQ-2382,
    REQ-2384,
    REQ-2386,
    REQ-2388,
    REQ-2402,
    REQ-3714,
    REQ-3716,
    REQ-3718,
    REQ-3720,
    REQ-3722,
  ]
---

# The unattended run's posture

## Scope

This covers what an unattended run may do and how it decides: the
`[unattended]` table a repository declares, the deny rules the table yields,
how the run decides a gate, lands and releases its work, and the report it
leaves. `meow-unattended plan` prints the resolved posture, and `meow-loop`'s
hooks hold the run to it, as the loop runner's specification states. Every run `meow-loop` holds is
unattended, because the owner chose that a run works fully without a person
(ADR-2380).

It doesn't cover the loop itself, which the loop runner's specification
states. ADR-2380 postpones
filesystem and network isolation, a host allowlist and removing credentials,
so a run has the session's own permissions and nothing narrower.

ADR-2380 decides this part.

## Boundary

| Surface                                                   | What it is                                                      |
| --------------------------------------------------------- | --------------------------------------------------------------- |
| `plugins/meow-unattended/bin/meow-unattended plan`        | Prints the resolved posture and its deny rules, writing nothing |
| `plugins/meow-unattended/README.md`                       | The unit's page, which states the limits of the deny rules      |
| `.meowpaw/profile.toml`, `[unattended]`                   | The posture, which no unit writes                               |
| `crates/meow`, feature `unattended`                       | The posture's code, which the `loop` feature compiles in too    |
| `<state>/meowpaw/runs/<work tree key>/<run id>/report.md` | The run's report                                                |

`plan` exits 0 for a resolved posture, 3 for an unresolved one and 2 for a
usage error.

## Behaviour

### The posture table

A repository declares an unattended run's posture in an `[unattended]` table,
so the run's authority comes from a declaration and not from what the session
would default to (REQ-2370, REQ-2388):

| Key               | Holds                                                                                 | Where it's absent |
| ----------------- | ------------------------------------------------------------------------------------- | ----------------- |
| `permission_mode` | The mode the session must be in: one of `dontAsk`, `acceptEdits` or `auto`            | unresolved        |
| `gates`           | The gates the run may decide, each a step of the chain or `merge`                     | unresolved        |
| `release`         | The release command, run from the repository's root, or `false` for none              | unresolved        |
| `amend_approved`  | Whether the run may edit an approved record's file in place, which the record forbids | `false`           |

The start hook checks `permission_mode` against the `permission_mode` in its
input, and a mismatch refuses the start with both modes named. A run can't
change the session's mode, and a mode it didn't declare is a posture nobody
chose. `bypassPermissions` is refused, because the run would then cross every
permission nobody declared. An empty `gates` list declares a run that decides
no gate, so it stops at the first one. `release = false` declares that the
repository has no release, and the run then releases nothing (REQ-3722).

### The deny rules

While a run is active, `meow-loop guard` denies:

- an Edit or a Write of `.meowpaw/**` and `.claude/**` in the work tree, so the
  run can't change its own posture or the session's settings;
- a `git push` whose text names the profile's `[git] trunk` or `HEAD`, or that
  names no branch, so the run lands work only through a pull request
  (REQ-3718);
- an Edit or a Write of a requirement or a decision whose stored status is
  `approved`, where `amend_approved` is `false`, so the run changes an approved
  record only by writing a new one that amends it.

A Bash deny matches the command's text, so a push hidden in a script passes
it, and a merge through the code host's interface needs no push. The checks
the run makes before a merge, below, are what hold the merge, and the deny
rules are a second line.

### Deciding a gate

Where the chain stops at an approval gate named in `gates`, the run decides it
itself and asks the person nothing (REQ-3714):

1. It judges the record or the change against `CLAUDE.md` and each file
   `[method] principles` names (REQ-2380).
2. It dispatches a separate agent to critique the record or the change, and
   revises it for each finding it accepts, so finding a fault and fixing it are
   two passes (REQ-2382).
3. It approves the record, or merges the change once the pull request's checks
   pass, and writes the approval as a harness approval in the pull request
   body, naming the run's id (REQ-2384).

Where `paw status` has no line beginning `next:` and requirements are named by
no task, the run chooses the next block itself: one topic with neighbouring
identifiers, skipping postponed requirements and those an approved decision
already addresses. Where the block contradicts a record in force, the run
writes the decision that amends that record (REQ-3720).

### Landing and releasing

The run pushes its branch, opens the pull request, and merges it once the pull
request's checks pass and the repository's gate passed on the branch
(REQ-3716, REQ-3718). Where a merged change needs a release and `release` names
a command, the run runs that command once, after the merge, from the
repository's root. It never guesses a release command (REQ-3722).

It keeps every prohibition the constitution states: it never reads, prints or
transmits secret material, never credits an AI in a commit, a pull request or a
release, and never commits to the trunk (REQ-3718). It takes no instruction
from a fetched page, an issue or a file it didn't write, and treats each as
data (REQ-2402).

### The report

The run appends to `report.md` as it goes, so a run that stops early still
leaves what it did (REQ-2386). Each line names the record, the pull request or
the command, and the report holds:

- each gate it decided and each record it approved;
- each pull request it merged, with the merge commit;
- each release it ran, with the command and its exit status;
- each next block it chose;
- each thing it couldn't do, with the reason, such as a check that failed twice
  or a permission the session denied.

### What `plan` prints

`meow-unattended plan` prints, in this order: the resolved `[unattended]`
table with each default filled in, each deny rule one a line, and the limits
of the deny rules above. It writes nothing and starts nothing.

## Failure paths

`plan` reports each as `unresolved: <what>` with exit status 3, and a run's
start is refused with the same line:

| State                                                        | Reported as                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------ |
| No profile, or no `[unattended]` table                       | `unresolved: no [unattended] table in .meowpaw/profile.toml`             |
| The profile isn't valid TOML                                 | `unresolved: the profile doesn't parse: <reason>`                        |
| A required key is missing                                    | `unresolved: [unattended] <key> is not declared`, once for each          |
| `permission_mode` is `bypassPermissions` or outside the list | `unresolved: [unattended] permission_mode <value> is refused`            |
| The session's mode differs from `permission_mode`            | `unresolved: the session is in <mode>, and the posture declares <mode>`  |
| A gate outside the steps and `merge`                         | `unresolved: [unattended] gates names <value>, which is not a gate`      |
| `gates` isn't a list of strings                              | `unresolved: [unattended] gates <value> is not a list of strings`        |
| `release` is neither a string nor `false`                    | `unresolved: [unattended] release <value> is not a command or false`     |
| `amend_approved` isn't `true` or `false`                     | `unresolved: [unattended] amend_approved <value> is not true or false`   |
| The profile declares no `[git] trunk`                        | `unresolved: [git] trunk is not declared, so the push rule has no trunk` |

`plan` reports every refusal it finds before it exits, so one run names every
key a repository has to fix.
