---
id: ADR-2330
artifact: adr
status: done
revised: 2026-09-30
addresses: [REQ-3324, REQ-3326]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2330. A refusal line quotes GitHub's reason, and a rejected credential ends the run

## Decision

Every `refused:` and `unauthenticated:` line `meow-github` prints ends with
`; GitHub said "<message>"` where GitHub's answer carries a message the line
doesn't already quote (REQ-3324). A 403 naming `issues=write` then reads
`refused: POST repos/o/r/issues needs issues=write; GitHub said "Resource not accessible by personal access token"`,
and a 401 reads `unauthenticated: POST repos/o/r/issues; GitHub said "Bad credentials"`.
The line with neither permission header, which already quotes the message,
is unchanged, and an answer with no message adds nothing.

After a 401, the request layer sends no further request in that run
(REQ-3326). `project` stops as it does at a throttle: it sends no read-back
listing, prints the `partial:` line and exits 3. `history` reports the
listing unread and exits 3, as it does for any refusal.

This amends two sentences of ADR-1810's decision on refusals: the line's
form, and nothing having said what a run does after a 401.

Once this is accepted, a 403 whose cause is single sign-on or an archived
repository shows GitHub's words for it, and a run whose token is bad sends
one request with it and not one per task. What still doesn't work: a 403
caused by the lockout GitHub applies after rejected requests from another
process reads as an ordinary refusal, because GitHub's answer doesn't say it
is one.

## Why

A permission header says what an endpoint accepts and not why this credential
was refused, and GitHub documents single sign-on refusals that carry a
permission-shaped answer (RES-0312). Several rejected requests in a short
time make GitHub reject the account's valid credentials too (RES-0312), and
`project` today goes on to every remaining mapped task after a 401, sending
one rejected request each (RES-0312).

## Alternatives

| Option                                                              | Better at                                                       | Why it lost                                                                                                             |
| ------------------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                          | Short lines, and the permission is named as REQ-2574 asks       | A single sign-on refusal reads as a missing permission, and a bad token sends a request per task                        |
| Quote the message only where the credential holds an accepted scope | Shorter where the header tells the whole story                  | Only classic tokens send scopes, so a fine-grained token's single sign-on refusal goes unexplained                      |
| Stop after a number of 401s, not the first                          | Rides out a token replaced during the run                       | GitHub states neither the number nor the period of its lockout, so any number is a guess against a limit nobody can see |
| Quote always, stop at the first 401 (chosen)                        | GitHub's reason on every line, and one rejected request per run | Longer lines, and a run that met a passing 401 has to be run again                                                      |

## What it costs

Refusal lines get longer, and they now carry text GitHub writes and can
change. A run that met a 401 caused by something passing has to be run again.
The request layer holds one more piece of state for the run.

## What would reverse it

- GitHub documenting that its refusal messages can carry secret material, or
  one observed doing so.
- GitHub documenting that rejected requests no longer count towards a
  lockout, which would leave only the noise argument for stopping.

## Consequences

- SPC-1080's section "The GitHub request layer" states the line's new ending
  and the stop after a 401.
- ADR-1810's Decision gains a line naming this decision as its amendment.
- `meow-github`'s README shows the lines with GitHub's reason.
- TSK-4030 realises this decision with no epic.

## How I will know it was realised

1. A check sends a 403 carrying `X-Accepted-GitHub-Permissions: issues=write`
   and a message, and the line reads
   `refused: POST repos/o/r/issues needs issues=write; GitHub said "<message>"`.
2. A check answers a create with 401 `Bad credentials`, and the line reads
   `unauthenticated: POST repos/o/r/issues; GitHub said "Bad credentials"`.
3. A check answers the read of the first of two mapped tasks with 401, and the
   stand-in records no request after it: no read of the second task, no
   create and no read-back listing. The run prints the `partial:` line and
   exits 3.

## What this does not settle

- Whether to print the `X-GitHub-SSO` authorisation URL, which expires after
  an hour and names the organisation.
- What a run does after a 403 that is GitHub's lockout, which GitHub's
  answer doesn't mark as one.
