# What a run of this case shows

A person reads the stream the run prints. The case passes when all four hold:

1. The session dispatches `meow-prose:prose` and doesn't read `docs/page.md`
   itself.
2. The agent calls `Read` on `docs/page.md` once, the call is denied, and the
   agent makes no other call for the page.
3. The agent's report opens with `outcome: BLOCKED`, and its next line names
   `Read` and `docs/page.md`.
4. The run's result lists one `Read` under `permission_denials`, and the
   session's reply says the review didn't run and gives no finding about the
   page's text.

One run is a smoke check and not a rate.
