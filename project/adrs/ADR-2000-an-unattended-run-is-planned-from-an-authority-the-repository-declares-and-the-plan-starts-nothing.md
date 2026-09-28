---
id: ADR-2000
artifact: adr
status: approved
revised: 2026-09-28
addresses: [REQ-2388, REQ-2392]
postpones: [REQ-2372, REQ-2376, REQ-2390, REQ-2406]
supersedes: []
---

# 2000. An unattended run is planned from an authority the repository declares, and the plan starts nothing

## Decision

A new method-layer unit, `meow-unattended`, ships one command, `plan`. It
reads what a repository declares an unattended run may do, records that
authority in a settings file outside the working tree, and prints the exact
command that would start the run. It starts nothing. Starting a run belongs to
the runner that REQ-0870 and REQ-0894 ask for, and a later decision gives it
that command to run.

The authority is a new `[unattended]` table in `.meowpaw/profile.toml`, read
by the profile reader in `crates/meow`:

| Key               | Holds                                                                                                                | Where it's absent  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `permission_mode` | One of `manual`, `plan`, `dontAsk`, `acceptEdits` or `auto`                                                          | unresolved, exit 3 |
| `budget_usd`      | The spend ceiling, a positive number                                                                                 | unresolved, exit 3 |
| `gates`           | The gates the run may cross, each one of `research`, `requirements`, `design`, `epic`, `verify`, `review` or `merge` | unresolved, exit 3 |
| `units`           | Each unit the run loads, as the path of that unit's own directory                                                    | unresolved, exit 3 |
| `merge_protected` | Whether the run may push to the profile's `[git] trunk`                                                              | `false`            |
| `amend_approved`  | Whether the run may amend an approved requirement or withdraw an approved decision                                   | `false`            |

A missing table, a missing required key and a value outside its list each
report `unresolved` with the key named and exit status 3, because a guessed
posture or budget is authority nobody gave. An empty `gates` list is a valid
declaration, meaning the run crosses no gate, because a repository that wants
a run to stop at every gate has to be able to say so and still get a plan,
while a missing key says nothing and stays `unresolved`. `merge` means merging
into a branch other than the trunk. `plan` refuses `merge_protected = true`
without `merge` in `gates` as `unresolved` with exit status 3, because a push
to the trunk lands work on it just as a merge does, and a repository that bars
the run from merging into any other branch can't mean to let it land on the
trunk. A repository declares `manual` to have every call that would prompt
denied, so the run does only what its allow rules name, and `plan` to have the
run read and propose without editing anything. `bypassPermissions` is refused
as a posture, because it skips the protection Claude Code gives `.claude`
and `.git` (RES-0299), where a run could write an `env` block or rules that the
next unattended run applies. The gate names are the steps whose artifact
waits for approval, plus `merge`, so a gate RES-0074 marks as never crossed, such as publishing or release, has no name to declare.

`plan` builds the run's command line (REQ-2388, REQ-2390, REQ-2392):

```text
claude -p --bare
  --plugin-dir <unit>            once for each declared unit
  --permission-mode <declared>
  --permission-prompts none
  --disallowed-tools AskUserQuestion
  --output-format stream-json --verbose
  --max-budget-usd <declared>
  --settings <snapshot>
```

`--bare` loads no installed plugin, hook, MCP server or `CLAUDE.md` by
discovery, so the run loads exactly the units named (RES-0299). Each entry in
`units` must be a directory holding `.claude-plugin/plugin.json`. A folder of
units is refused, because `--plugin-dir` loads each child of a folder, and that
is discovery again. A URL is refused, because the archive behind it can change
between the plan and the start, and the snapshot can't fix it.
`--permission-prompts none` removes the tools that need a person, and the
explicit `--disallowed-tools AskUserQuestion` keeps the one RES-0074 names
removed if a later version changes what `none` removes.
`--output-format stream-json --verbose` makes each denial arrive as a
`permission_denied` message, and the documentation's streaming example needs
`--verbose` with `stream-json` (RES-0299), so whatever reads the run's denials
depends on both flags.

The snapshot is the `--settings` file, and it is the run's authority.
`plan` writes it under the harness's state directory, in
`meowpaw/unattended/<work tree key>/<sha256 of its content>.json`, keyed as
the evidence ledger keys a work tree and honouring `MEOWPAW_STATE_DIR` and
`MEOWPAW_STATE=off`. Naming the file by its hash lets whatever starts the run
check that the file is the one planned. With state writing off, `plan` prints
the snapshot and writes nothing, and says no snapshot was kept. `plan --purge`
removes the work tree's snapshots. The snapshot holds the resolved table, each
unit's name and version from its `plugin.json`, and these deny rules, each
path written as an absolute `//` path, because a single leading `/` resolves
against the settings source, which here is the state directory and not the
work tree (RES-0299):

- `Edit` on `.meowpaw/**`, `.claude/**` and the folder that holds the
  snapshot, so the run can't rewrite what it was planned from. The rule names
  the folder and not the file, because the file's name is the hash of content
  that holds the rule, and no content can hold its own hash.
- Where `merge_protected` is false, three rules:
  `Bash(git push *<trunk>*)`, `Bash(git push)` and `Bash(git push *HEAD*)`.
  The first denies a push that names the trunk, and the other two deny the
  bare form and the `HEAD` form, which push the trunk whenever it's checked
  out. A run therefore pushes its own branch by naming it. The first rule
  also denies a push to any branch whose name contains the trunk's, which a
  denial reports rather than hides. These rules deny only the forms they
  match (RES-0299), so they are a step towards REQ-2376 and don't meet it, as
  the limits below say.
- Where `amend_approved` is false, `Edit` on each requirement and decision the
  record holds as `approved` when `plan` runs, found from the `[record]` the
  profile declares. With no `[record]`, `plan` reports no record to protect.
  A record approved after `plan` runs isn't in the snapshot, so `plan`'s
  output tells the person to plan again after approving one.

A deny rule passed in `--settings` holds against an allow rule from any other
settings scope (RES-0299), so nothing the repository or the user allows can
lift it.

The snapshot carries no credential and no `apiKeyHelper`. A bare run reads
only `ANTHROPIC_API_KEY` from its environment or an `apiKeyHelper` from
`--settings` (RES-0299), so the person who starts the printed command supplies
the key. I chose that because a helper in the snapshot is a credential path the
harness would own, and removing credentials from what a run executes is
REQ-2400's.

`plan` refuses, as `unresolved` with exit status 3, a repository whose
`.claude/settings.json` or `.claude/settings.local.json` carries an `env`
block, naming the file and each key. `--bare` still applies that block
(RES-0299), so it's authority the snapshot wouldn't hold.

`plan` prints the resolved table, each unit with its version, the command line
one argument per line, the snapshot's path and its deny rules, the limits
below, and that the command needs `ANTHROPIC_API_KEY` in its environment, and
exits 0.

Four limits of the deny rules are stated in `plan`'s output and in the unit's
README. RES-0299 found the first three in the documentation, and the fourth
follows from relations being authored upward:

- A Bash deny rule stops only the forms it matches, so
  `git -C . push origin main` isn't denied. Neither is a push that names only
  the remote or gives only flags while the trunk is checked out, such as
  `git push origin` or `git push --force-with-lease`.
- An `Edit` deny rule reaches the file tools and the file commands Claude Code
  recognises, and not a script that opens the file itself. So the rules stop a
  run widening its own authority, or amending an approved record, only
  through those tools and commands.
- A merge through the code host's interface isn't denied at all.
- A new record whose front matter supersedes or withdraws an approved one
  retires that record without touching its file, so no `Edit` deny rule stops
  it. No check catches this yet, so the review of the run's work has to.

The sandbox that REQ-2396 asks for is what enforces the first two at the
operating system, and a run's merge through a code host's interface is closed
only by removing its credentials, which REQ-2400 asks for.

This decision addresses only the two requirements a static check can close:
REQ-2388, because the printed command declares its posture, and REQ-2392,
because it loads each unit by name. It postpones the four whose check needs a
run, since `plan` starts none, and partial cover by deny rules no more meets a
behavioural requirement than it meets REQ-2376. The decision that starts a run
closes each one with this evidence:

- REQ-2372: a started run's stream shows a `permission_denied` message for an
  attempt to edit the profile, `.claude` and the snapshot, and, once the
  sandbox exists, the same attempt from a script fails too.
- REQ-2390: the run's `system/init` event lists no `AskUserQuestion` among its
  tools.
- REQ-2406: a started run's stream shows a denial for an attempt to edit an
  approved requirement, a new record that supersedes an approved decision is
  caught before it lands, and a script's edit fails under the sandbox.
- REQ-2376: a started run is denied a push and a merge to the trunk in every
  form, which needs the sandbox and REQ-2400's credential removal.

After this decision a repository can declare what an unattended run may do and
read, before anything runs, exactly what would start and under what authority.
What still doesn't work:

- Nothing starts a run. The runner that repeats a prompt until a condition or
  the budget stops it is REQ-0870's, and only a person may start it
  (REQ-0894).
- The declared gates are fixed and printed, and nothing crosses one yet. The
  route that approves a gate on the run's behalf is REQ-2370's.
- The deny rules on pushing, on the profile and the snapshot, and on approved
  records hold only for the forms RES-0299 names, until the sandbox and the
  credential removal exist.
- A new record that supersedes or withdraws an approved one isn't denied.
- A merge to the trunk through the code host's interface isn't denied, and no
  branch other than the trunk is protected.
- REQ-2372, REQ-2376, REQ-2390 and REQ-2406 aren't met, because no run has
  shown their behaviour.
- The printed command fails without `ANTHROPIC_API_KEY` in its environment,
  and it can't use a subscription login. A key in the environment is visible
  to every command the run executes until REQ-2400's credential removal
  exists.
- A unit can't be loaded from a URL.

## Why

RES-0074 found that a non-interactive session without `--bare` runs a
repository's hooks and connects its MCP servers with no trust prompt, that
`--bare` loads no plugins, and that the run's authority must be fixed while a
person is awake. RES-0299 read Claude Code 2.1.280 and its documentation on
2026-09-28. It found every flag above, that deny rules win across scopes, that
a folder given to `--plugin-dir` loads each child, that `--bare` still applies
a project's `env` block, and where Bash and Edit deny rules stop. RES-0299
read version 2.1.280, older than the 2.1.283 most units require, and
`meow-unattended`'s `requires.toml` declares 2.1.283, so a flag that changed
between the two wouldn't show in its findings. RES-0299 is approved with this
record or before it, because a decision can't rest on research nobody has
agreed to.

Planning without starting is the smallest increment that works: a person can
run `plan`, read the authority, and change the profile, and nothing crosses a
gate unattended. Starting belongs with the runner, the judge and the sandbox,
and a start without them would run unconfined.

The snapshot lives outside the working tree because REQ-3072 puts run state
there and REQ-0752 keys it by the work tree, and the evidence ledger already
does both.

## Alternatives

| Option                                                                   | Better at                                              | Why it lost                                                                                                                        |
| ------------------------------------------------------------------------ | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Plan and start the run in one increment                                  | A run exists sooner                                    | A start without the runner's budget, the judge and the sandbox runs unconfined, and a deny rule alone isn't a boundary (RES-0299)  |
| `--restricted` in place of `--bare`                                      | Ignores user, project and local settings files as well | Two descriptions read on the same day disagree, and what `--tools` must name for the run to keep its shell is unobserved           |
| Leave `project` out of `--setting-sources` in place of the `env` refusal | Plans a run for a repository with an `env` block       | The installed help doesn't say whether it keeps the `env` block out of a bare run, and no run was observed (RES-0299)              |
| A `PreToolUse` hook that checks each call against the authority          | Sees the whole command text                            | `--bare` skips settings hooks and installed plugins' hooks, and whether it runs a hook from a `--plugin-dir` unit is unobserved    |
| The run reads its authority from the profile, with no snapshot           | No file outside the tree                               | The run can edit the profile, so it could widen its own authority, which REQ-2372 forbids                                          |
| Allow a unit from a URL, fetched at plan time into the state folder      | Loads a released unit without an install               | Moves the harness into supply-chain handling nobody asked for yet, and a directory already covers every unit this repository ships |
| Deny `Edit` on each record directory in place of each approved file      | A handful of rules in place of one per approved record | It also denies the drafts a run must be able to write, so a run couldn't record its own work                                       |
| Do nothing                                                               | No new unit                                            | Two static requirements stay unmet, and whatever starts a run later has no declared authority to start from                        |

## What it costs

A repository that wants an unattended run writes a table with four required
keys, and one without it gets `unresolved`, which is this repository's own
state after this decision. A repository with an `env` block in its committed
`.claude/settings.json` can't plan a run until it moves the block out, and
neither can a person with an `env` block in their own uncommitted
`.claude/settings.local.json`.

Whoever maintains `crates/meow` takes on a feature `unattended`, built by
`build-units`, which reads the profile, the record and the units' manifests.
The deny rule on pushes also denies pushing to a branch whose name contains
the trunk's, such as `feat/maintain` where the trunk is `main`; the run reports
the denial and a person pushes.

Every plan with state writing on leaves a snapshot of a few kilobytes in the
state directory until `plan --purge` removes it. A repository with a thousand
approved records gets a thousand deny rules in its snapshot, and the person
reading `plan`'s output reads each one, since `plan` prints every deny rule.

A run under `--bare` is billed through an API key, never a subscription login,
so the person who starts one pays for it by the token and keeps that key.

## What would reverse it

- If a run started by a person shows `--restricted` ignoring every settings
  file while keeping the shell the run needs, I would pass it and drop the
  `env` refusal.
- If a run shows a bare session applying the user's own `permissions.allow`
  rules or the user's own `env` block, I would add whichever flag stops that,
  and until one exists report them in `plan`'s output as part of the
  authority.
- If a run shows that leaving `project` out of `--setting-sources` keeps the
  project's `env` block out of a bare run, I would pass it and drop the `env`
  refusal.
- If Claude Code takes a checksum with `--plugin-url`, I would accept a URL
  with its checksum in `units`.
- If `--permission-prompts none` stopped removing the tools that need a person,
  I would name each one in `--disallowed-tools`.

## Consequences

- A unit `meow-unattended` in the method layer, with a program, a README, a
  budget of no characters on every turn, since it ships no skill, a
  `requires.toml` naming Claude Code 2.1.283 and a marketplace entry. The
  task that builds it reads `claude --help` from that version and confirms
  each flag `plan` prints.
- A native feature `unattended` in `crates/meow`, built by `build-units`, and
  an `[unattended]` table in the profile reader.
- A new specification of the unattended run, and a line in SPC-1090 naming
  it.
- The decision that starts a run takes `plan`'s command line and snapshot as
  its input and cites the limits above. It also checks the `system/init`
  event's `plugins` against the units the snapshot names and stops the run on
  a difference, because a unit that fails to load doesn't stop the run
  (RES-0299). Before it starts, it checks that the snapshot's content still
  hashes to its file name, because the name is the only proof the file is the
  one planned, and it repeats the `env` refusal, because a block added after
  `plan` would still reach the bare run.
- That decision closes REQ-2372, REQ-2390 and REQ-2406 with the evidence
  named above, and REQ-2376 once the sandbox and the credential removal exist.

## How I will know it was realised

1. Fixture repositories with no `[unattended]` table, and with a table lacking
   each required key in turn, each give `unresolved` naming what's missing and
   exit status 3. A table naming `bypassPermissions`, a gate outside the list,
   a folder of units, a URL, and `merge_protected = true` without `merge` in
   `gates` is each refused the same way.
2. A fixture declaring `dontAsk` prints `--permission-mode dontAsk`, and the
   printed command line holds `--bare`, `--permission-prompts none`,
   `--disallowed-tools AskUserQuestion`, `--max-budget-usd` with the declared
   value, and exactly one `--plugin-dir` for each of three declared units.
3. A fixture repository with a `.mcp.json` server and a hook in
   `.claude/settings.json` gets a command line and snapshot naming neither,
   and one with an `env` block gets `unresolved` naming the file and its keys.
4. The snapshot denies `Edit` on `.meowpaw/**`, `.claude/**` and the folder
   that holds it.
   Changing the profile after `plan` leaves the snapshot's content and its
   hash unchanged.
5. With `merge_protected` absent, the snapshot holds the three push rules for
   the declared trunk. With it `true`, it holds none.
6. With `amend_approved` absent, a fixture record of two approved and one draft
   requirement and one approved and one draft decision gives exactly three
   deny rules on record files, one for each approved file. With it `true`, it
   gives none. A fixture profile with no `[record]` gets output saying there
   is no record to protect.
7. With `MEOWPAW_STATE=off`, `plan` writes no file and says so, and
   `plan --purge` removes every snapshot of the work tree.
8. `plan`'s output states each of the four limits of the deny rules, that
   the command needs `ANTHROPIC_API_KEY`, and that a record approved later
   needs a new plan.
9. Each check above counts what it matched, and a count of zero where one was
   expected fails it.
10. Every requirement ADR-2000 addresses lands in exactly one closed task.

## What this does not settle

- Starting a run, repeating it and stopping it, which REQ-0870, REQ-0872,
  REQ-0876 and REQ-0894 ask for.
- Crossing a declared gate, the judge and the escalation list, which REQ-2370,
  REQ-2382, REQ-2384 and REQ-2386 ask for.
- The sandbox, the host list and the credential removal, which REQ-2396,
  REQ-2398 and REQ-2400 ask for, and so a push or a merge in a form the deny
  rules don't match.
- Whether a bare run applies the user's own `permissions.allow` rules or the
  user's own `env` block, which RES-0299 couldn't observe.
- REQ-2376 as a whole: a merge through the code host's interface, and
  protecting a branch other than the trunk.
- REQ-2372, REQ-2390 and REQ-2406, whose behavioural checks need a started
  run.
- A new record whose front matter supersedes or withdraws an approved one,
  which no deny rule and no check catches yet.

## Open review findings

- Round 1, finding 12, specification-level detail in the Decision: I kept the
  output contents, the state path and the exit statuses here because the
  realisation criteria test them, and a reader approving the decision should
  see what the criteria hold it to. The specification that the Consequences
  plan takes this detail over, and this record freezes on approval, so the
  specification then rules.
- The decisions index, round 2, preference 2: its Amended line lists
  "ADR-1100 by EPC-1070", an epic amending a decision. `paw index` generates
  that line from EPC-1070's front matter, so the fix, if one is due, belongs
  there or in `paw index`, and this change touches neither.
