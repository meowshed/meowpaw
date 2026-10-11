---
id: BUG-1620
artifact: bug
status: withdrawn
severity: major
violates: REQ-4110
enters: implement
found: 2026-10-11
revised: 2026-10-11
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi router answers a raw adapter error and never picks a Claude model

Withdrawn by ADR-2930: the `meow-router` tool this defect reports is deleted
with the dispatch behind it, so the route is the session's own act and the
defect has no subject to fix.

The `meow-router` tool returns `content.some is not a function` as its whole
result, because its model choice matches the provider name `anthropic`
exactly and the session's catalogue holds Claude models only under another
provider, so the call falls back to the first model in the list and a failed
nested call surfaces as a bare internal error.

## Reproduction

Seen with Pi 1.1.0, `@meowshed/meow-flow` 0.51.0, at revision `a42e16d2` on
macOS (arm64), where the session's catalogue holds Anthropic models under the
`openrouter` provider and the default model is `mimo-v2.5-pro` under the
`xiaomi-token-plan-ams` provider.

1. Invoke the `meow-router` tool with any request.

## What the system does

The tool's result reads `content.some is not a function`, with no model,
provider or reason beside it. The choice in
`packages/meow-flow/extensions/flow.ts` is
`models.find((m) => m.provider === "anthropic" && /sonnet/i.test(m.id))`,
which matches nothing when the catalogue names `openrouter` as the provider,
and the fallback takes the first model in the list. The nested call's throw
travels to the tool result unguarded. The throw site itself is the
`openai-completions` adapter of Pi 1.1.0, outside this repository.

## What it should do, and why

REQ-4110 says the tool makes a nested model call and returns the nested
call's output as its result. A result that is a bare internal error is
neither the output nor something a person can act on.

## Triage

It enters at implement, because REQ-4110 covers the tool and the extension
does something else. Severity is major: routing is the harness's first act,
so every request starts with a tool that fails on this catalogue.

## Closed by

The router's model choice and message handling move into
`packages/meow-flow/lib/router.mjs`, where
`tools/test_pi_extensions.py` runs them against a stand-in registry: a
catalogue whose Claude models sit under another provider still picks one,
a message whose content is a string yields its text, a model that throws
fails alone and the next is tried, and a catalogue where every model throws
returns the last failure with its provider and model named.

## Tasks

- [ ] T-001 TSK-5460 pick a Claude model across providers, answer from a
      string or a block list, and name the model that failed, in
      `packages/meow-flow/extensions/flow.ts` and
      `packages/meow-flow/lib/router.mjs`
