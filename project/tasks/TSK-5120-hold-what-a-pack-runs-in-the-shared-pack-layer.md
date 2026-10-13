---
id: TSK-5120
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2565
closes: [REQ-2420, REQ-2422, REQ-2426, REQ-2428, REQ-2446, REQ-2448]
issue: 1001
projected: 992ab67d4c53
tracked: 41e18218c52e
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold what a pack runs in the shared pack layer

The shared pack layer runs what the repository configured and nothing it
chose, as SPC-1190 states under "What a pack runs". One task, one branch, one
pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture ecosystem where two tools serve `lint` and the repository
   configures the second, when the fixture pack binds, then it binds the
   second, and with neither configured it prints `lint` unbound (REQ-2420).
   Closed by: a crate test naming REQ-2420, seen failing first.
2. Given a fixture pack whose binding adds a lint group the repository's
   configuration doesn't name, when the layer's test runs, then it fails
   (REQ-2422). Closed by: a crate test naming REQ-2422.
3. Given a fixture project declaring a package manager, when the fixture pack
   binds, then each command runs through it (REQ-2426). Closed by: a crate
   test naming REQ-2426.
4. Given a fixture repository pinning a toolchain version that differs from
   the installed one, when the pack reports, then it names both versions
   (REQ-2428). Closed by: a crate test naming REQ-2428.
5. Given a fixture language with two hosts and no host detected, when the
   pack binds, then every verb is unresolved, naming the host it is waiting
   on (REQ-2446). Closed by: a crate test naming REQ-2446.
6. Given a fixture build with a prerequisite another form performs
   implicitly, when the pack binds `build`, then the prerequisite runs first
   in the bound command (REQ-2448). Closed by: a crate test naming REQ-2448.

## What to do

Add the rules to a shared layer in `crates/meow/` that every language pack's
feature uses, so a pack meets them by using the layer and not by restating
them. Hold each rule with a fixture pack in the crate's tests that breaks it.
Move `meow-markdown` onto the layer wherever a rule applies to Markdown, and
leave its behaviour SPC-1195 states unchanged. Document the layer's rules on
`plugins/meow-markdown/README.md` only where they change what that pack
reports.

## Depends on

Nothing.

## Evidence

The shared layer is `crates/meow/src/pack.rs`, behind the crate's `pack`
feature, which the `markdown` feature turns on. Each criterion closes with a
crate test in that file's tests, each seen failing against stubbed bodies
before the layer was written:

1. `tsk_5120_criterion_1_the_configured_tool_binds_and_none_is_unbound` and
   `tsk_5120_criterion_1_a_second_configured_tool_is_named_and_not_run`
   (REQ-2420). `meow-markdown bind` binds `format`, `lint` and `test` through
   the layer's `choose`, and `test_tsk_5120_two_configured_formatters_bind_the_first_and_name_the_other`
   in `plugins/meow-markdown/tests/test_markdown.py` holds the comment naming
   a second configured formatter.
2. `tsk_5120_criterion_2_a_lint_group_nobody_asked_for_is_refused` (REQ-2422).
3. `tsk_5120_criterion_3_each_command_runs_through_the_declared_package_manager`
   (REQ-2426).
4. `tsk_5120_criterion_4_a_pinned_version_unlike_the_installed_one_names_both`
   (REQ-2428).
5. `tsk_5120_criterion_5_with_no_host_detected_every_stage_waits_on_it` and
   `tsk_5120_criterion_5_one_host_detected_is_the_one_and_two_are_unknown`
   (REQ-2446).
6. `tsk_5120_criterion_6_the_build_runs_its_prerequisite_first` (REQ-2448).

Markdown has no package manager, pinned toolchain, host or build
prerequisite of its own, so `meow-markdown` uses `choose` alone of these
rules, and its other behaviour SPC-1195 states is unchanged.

Every stage passed in pull request #PR.

## Left alone

Which tool each language's pack binds, which each pack's own document states.
