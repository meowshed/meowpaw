<role>
What a reviewer of Go checks that no command reports. Read it when you review
Go, after `meow-go status` has named the module and the linter configuration. A
clean `go vet` says the code passes the analyses that ran, and each point here
asks whether the design serves its callers.
</role>

<rules name="reviewing Go">
- R1. Check that an error is wrapped with `%w` where a caller may need to
  recover its cause with `errors.Is` or `errors.As`, because every arrangement
  compiles and only one lets the caller act.
- R2. Check that a long operation takes a context and stops when it is
  cancelled, because no stage asks whether it can be cancelled at all.
- R3. Ask of each goroutine who stops it and what happens when nobody does,
  because a goroutine that outlives its work leaks until the process ends.
- R4. Check that an interface is defined by its consumer and not exported
  beside its implementation, because the consumer needs only the methods it
  calls, and no linter holds this convention.
- R5. Prefer table-driven tests with named subtests, because a failing case
  must be nameable to be found.
- R6. Check that the code uses no standard-library function newer than the
  `go` line declares, because a consumer on the declared version fails to
  build where the author's newer toolchain didn't.
</rules>
