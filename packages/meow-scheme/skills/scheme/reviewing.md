<role>
What a reviewer of Scheme checks that no command reports. Read it when you
review Scheme code, after `status` has named the implementation. A passing
`raco test` says the tests it found passed, and each point here asks what it
can't see.
</role>

<rules name="reviewing Scheme">
- R1. Check tail position, because recursion in tail position is safe and
  elsewhere it overflows the stack on a larger input, and the code looks the
  same either way.
- R2. Check macros for hygiene and for what `syntax-rules` can't express,
  because `syntax-case` or an explicit renamer breaks portability where not
  every implementation has it.
- R3. Check `call/cc` against `dynamic-wind`, because continuations change when
  resource cleanup runs.
- R4. Look for mutation, because the default is a value nobody changes, and
  that convention is the reviewer's to enforce.
- R5. List the SRFIs the file assumes, because they are the real dependency
  list and are usually written nowhere.
- R6. Check whether the file is a library, a module or a script under the
  implementation that runs it, because a script under one implementation is a
  library under another and never runs its body.
</rules>
