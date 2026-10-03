---
id: ADR-2360
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-3004, REQ-3654]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2360. The `meow-verbs` stub leaves the marketplace

## Decision

`meow-verbs` is no longer in the marketplace. The directory `plugins/meow-verbs/`,
its entry in `.claude-plugin/marketplace.json` and its row in `docs/README.md`
are deleted, and `meow-verbs@0.9.0` leaves the `describes` list of the
troubleshooting page. The page keeps its section "meow-verbs is now
meow-checks", because a copy installed before the removal goes on printing the
notice, and that section is where the notice sends its reader. SPC-1040 stops
saying the stub stays in the marketplace (REQ-3004, REQ-3654).

Once this is accepted, `claude plugin install meow-verbs@meowpaw` fails, and
every other unit installs as before. What still holds is the rename itself,
which ADR-2300 decided: the unit is `meow-checks`, and the profile's `[verbs]`
table and the five verb names are unchanged.

## Why

ADR-2300 kept the stub for one release, and `meow-checks` 0.9.0 is that
release: the tag `meow-checks-v0.9.0` exists, and so does `meow-verbs-v0.9.0`,
the stub's own release. The stub's README says "the release after
`meow-checks` 0.9.0 removes this stub". REQ-3004 says a deprecation is
announced in one release and removed in a later one, and REQ-3654 says the
marketplace ships no unit whose purpose the chain no longer has, beyond that
one release. A stub with no skill and no program has no purpose of its own, so
each release it stays is one the requirements don't allow.

The acceptance criterion of ADR-2300 and EPC-2200 that
`claude plugin install meow-verbs@meowpaw` still works was the condition of
that one release, and it was met when the release shipped. This decision
doesn't reword it. It ends the window the criterion described.

## Alternatives

| Option                                          | Better at                                        | Why it lost                                                                               |
| ----------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Keep the stub another release                   | Reaching an install that missed the notice       | The notice has run for a release, and a second one repeats it to the same readers         |
| Remove the unit and the troubleshooting section | A tree with no mention of the old name left over | A copy installed before the removal still prints the notice, which points at that section |
| Do nothing                                      | No work, no risk                                 | The deprecation then never ends, which REQ-3004 says it must                              |

## What it costs

An install of `meow-verbs` that hasn't moved keeps its cached copy, so its
session still prints the notice, but `claude plugin update meow-verbs@meowpaw`
finds no such unit. A script that runs `claude plugin install
meow-verbs@meowpaw` fails from the next marketplace release on, where it
installed a stub before. The release also publishes no `meow-verbs` 0.10.0.

## What would reverse it

- A report that installs still run `claude plugin install meow-verbs@meowpaw`
  from a script and nothing else tells their owners the unit was renamed.

## Consequences

`tools/test_marketplace.py` checks that the marketplace has no `meow-verbs`
entry and that git tracks no file under `plugins/meow-verbs/`, in place of the
check that the stub exists, and its check of where the old name may appear
loses the stub and the marketplace. The release notes of the change name the
removal. The unit's directory leaves `plugins/`, so the next release publishes
nothing for it.

## How I will know it was realised

1. `.claude-plugin/marketplace.json` has no entry named `meow-verbs`.
2. `git ls-files plugins/meow-verbs` prints nothing.
3. Outside frozen records, the old name appears only in
   `docs/troubleshooting.md`, in SPC-1040's sentence about the rename and in
   `tools/test_marketplace.py`.
4. `meow-checks run format lint check test build` passes on the change.

## What this does not settle

- Whether the troubleshooting section on the rename is ever removed.
