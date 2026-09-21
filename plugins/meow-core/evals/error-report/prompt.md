---
name: error-report
description: A failing build, reported back to the person who has to fix it.
tags: [reporting]
runs: 3
max_turns: 10
expected_outcome: The reply opens with the failure, names the file and the line, and says what would fix it, with no expression of dismay in front of it.
---

I ran the build and it stopped. This is all I have:

```text
$ cargo build
   Compiling meowctl v0.4.1 (/home/me/work/meowctl)
error[E0308]: mismatched types
   --> src/profile/resolve.rs:184:29
    |
184 |         let verb = profile.verb(name)?;
    |                    ---------------- ^ expected `&str`, found `String`
    |
error: could not compile `meowctl` (bin "meowctl") due to 1 previous error
```

What happened?
