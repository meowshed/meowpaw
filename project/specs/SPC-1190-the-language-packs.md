---
id: SPC-1190
artifact: spec
status: live
revised: 2026-09-28
checked-at:
states: [REQ-0083, REQ-2434, REQ-2438]
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
aren't restated here. Running a bound verb is SPC-1040's.

ADR-1900 decides this part and EPC-1800 realises it.

## Boundary

A language pack is a unit holding a program and a skill that tells the model
to use it:

| Surface                                 | What it is                                                  |
| --------------------------------------- | ----------------------------------------------------------- |
| `plugins/<pack>/bin/<pack>`             | The program, with at least `status`, `bind` and `check`     |
| `plugins/<pack>/skills/<name>/SKILL.md` | The skill, which names the program and forbids guessing     |
| A supporting file beside the skill      | What a reviewer needs beyond the commands, loaded on review |
| `plugins/<pack>/README.md`              | The unit's page                                             |
| `.meowpaw/profile.toml`, `[verbs]`      | What `check` reads; the pack never writes it                |
| `.meowpaw/profile.toml`, `[<language>]` | The pack's own settings, in a table named for its language  |

The program writes no file, in the repository or outside it, and never writes
the profile or any tool's configuration. It runs one program, git, as
`git ls-files` for the tracked file list and `git check-ignore` for an ignored
path. A command that runs the language's tools on purpose, such as a link
check, is named as such in the pack's document, and `status`, `bind` and
`check` run none.

Exit status, for every command:

| Status | Means                                                                   |
| ------ | ----------------------------------------------------------------------- |
| 0      | The command reported what it was asked, and found nothing               |
| 1      | The command found at least one finding                                  |
| 2      | The command line was wrong                                              |
| 3      | Nothing was a finding, and something was unresolved, absent or unusable |

## Behaviour

### Detection

A pack detects its language from the files git tracks, by name and by the
presence of a configuration file, and starts none of the language's tools to
decide. A work tree the pack doesn't detect makes every command print
`unresolved: not a <language> repository` and exit 3.

### `bind`

`bind` prints a `[verbs]` table for the repository to paste. It binds each verb
from the configuration the repository commits, and never from what is
installed. It prints nothing for a verb the profile already declares. A verb
it doesn't bind is printed as a comment naming the reason: `# <verb>:
unresolved, <reason>` for a verb the language can't have, and `# <verb>:
unbound, <what the pack looked for>` for one it found nothing to bind. Where a
runner's configuration exists, `bind` names it and the runner's pack.

### `check`

`check` reads each verb's command in the profile. For each tool whose meaning
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

### The skill

The skill tells the model to run the program and never to guess a command. A
supporting file beside it carries what a reviewer of the language needs that no
command reports, and the skill loads that file when the language is reviewed,
not on every turn (REQ-0083). The skill names the tool versions the pack was
observed against.

## Failure paths

| State                                   | Reported as                                  | Exit |
| --------------------------------------- | -------------------------------------------- | ---- |
| The language isn't detected             | `unresolved: not a <language> repository`    | 3    |
| The profile is missing or doesn't parse | `unresolved: <what is wrong with the file>`  | 3    |
| A tool the command runs isn't on `PATH` | `tool absent: <tool>`                        | 3    |
| A tool exits on its own configuration   | `tool broken: <tool> exited <n>: <its line>` | 3    |
| A tool prints output of another shape   | `tool broken: <tool> printed <first line>`   | 3    |
| An unknown argument                     | the usage line                               | 2    |
