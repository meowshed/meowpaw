---
id: TSK-5460
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1620
closes: []
issue:
---

# Make the Pi router answer, or name the model that failed

The router's model choice and message handling move into
`packages/meow-flow/lib/router.mjs`, where a test drives them against a
stand-in registry, and `flow.ts` calls them. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a catalogue whose Claude models name another provider, when the
   choice runs, then it returns a Claude model from that provider before any
   other. Closed by: `tools/test_pi_extensions.py`, seen failing first
   (BUG-1620).
2. Given a completed message whose `content` is a string, when the text is
   read, then it yields the string; a block list yields its text blocks. A
   message whose stop reason is `error` or that carries an error message
   fails its model, and the next candidate is tried. Closed by: the same
   test.
3. Given a registry where every candidate throws, when the router runs, then
   it returns `meow-router: no model answered: <reason>` with the last
   failure's provider and model named. Closed by: the same test.
4. Given this change's tree, when `meow-checks run format lint check test
   build` runs, then each passes. Closed by: each verb's outcome in the
   task's pull request.

## What to do

`pickModels` orders the candidates: Claude models first, whichever provider
names them, then the session's model, then the rest; `responseText` reads a
string or a block list and refuses an error message. `flow.ts` keeps the
reply shape and the router prompt and calls the two. The throw site inside
Pi's `openai-completions` adapter stays outside this repository; the router
names what failed instead of surfacing it bare.

## Depends on

Nothing.

## Left alone

The throw inside Pi's `openai-completions` adapter, which is Pi 1.1.0's code
and not this repository's; the router names what failed instead of surfacing
it bare, and a person who needs the route adds a model the adapter answers.

## Evidence

Not yet.