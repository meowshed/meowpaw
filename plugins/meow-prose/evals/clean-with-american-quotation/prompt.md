---
name: clean-with-american-quotation
description: A text the standard accepts.
tags: [clean, named]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
The worker waits two seconds between retries, because the upstream application programming interface (API) allows one retry per second per client and the extra second covers clock drift between our hosts and theirs. The vendor's guide puts it plainly:

> Clients should not reconnect more than once per second, or the gateway will throttle their color-coded session for the rest of the day.

I kept the wait fixed rather than adding backoff, since five retries two seconds apart wait eight seconds in all, inside the ten-second window the scheduler allows.
</text>
