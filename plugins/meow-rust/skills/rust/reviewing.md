<role>
What a reviewer of Rust checks that no command reports. Read it when you review
Rust, after `meow-rust status` has named the edition and the clippy groups. A
clean `cargo clippy` says the code passes the groups that ran, and each point
here asks whether the design serves its callers.
</role>

<rules name="reviewing Rust">
- R1. Check that each signature that borrows should borrow, and each that owns
  should own, because both compile, and the choice decides who can call the
  function without cloning.
- R2. Follow an error from where it arises to where it becomes an exit code or
  a response, and check where it is wrapped and given context, because every
  arrangement compiles and only one tells the user what failed.
- R3. Flag each `unwrap` and `expect` outside a test, because a lint catches
  them only where the policy says so, and one in a library turns a caller's
  recoverable error into a panic.
- R4. Ask which feature combinations nothing builds, because the default set
  passes and a consumer enabling two features gets code no run has covered.
- R5. Check that each `unsafe` block has the invariant it relies on written
  beside it, because the compiler and `miri` check the code against that
  invariant and can't supply it.
- R6. Check what `pub` exposes, because everything public is something the
  crate will have to keep.
</rules>
