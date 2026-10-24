// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-starlark` on fixture repositories (TSK-5110, SPC-1385).

#![cfg(feature = "starlark")]

mod perdir_fixture;

use perdir_fixture::{PROFILE, Repo};

const LINTED: &str = "{ \"lint\": \"warn\" }\n";

/// A Bazel workspace that configures buildifier with its warnings on.
fn bazel(name: &str) -> Repo {
    Repo::new(
        name,
        &[
            PROFILE,
            ("MODULE.bazel", "module(name = \"shop\")\n"),
            (".buildifier.json", LINTED),
            ("BUILD.bazel", "# targets\n"),
        ],
    )
}

fn with_stages(name: &str, stages: &str, extra: &[(&str, &str)]) -> Repo {
    let profile = format!("[stages]\n{stages}\n");
    let mut files = vec![
        (".meowpaw/profile.toml", profile.as_str()),
        ("MODULE.bazel", "module(name = \"shop\")\n"),
        (".gitignore", "bazel-*\n"),
    ];
    files.extend_from_slice(extra);
    Repo::new(name, &files)
}

#[test]
fn status_reports_for_the_directory_holding_the_marker() {
    // TSK-5110 criterion 1, REQ-2348, REQ-3048: a workspace in a subdirectory
    // is reported for that directory, naming the marker and the build system.
    let repo = Repo::new(
        "starlark-sub",
        &[PROFILE, ("tools/MODULE.bazel", "module(name = \"t\")\n")],
    );
    let run = repo.run(&["starlark", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("scope: tools\n"), "{}", run.out());
    assert!(
        run.out().contains("marker: tools/MODULE.bazel"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("build system: Bazel, from tools/MODULE.bazel"),
        "{}",
        run.out()
    );
    assert!(!run.out().contains("scope: .\n"), "{}", run.out());
}

#[test]
fn a_work_tree_with_no_marker_is_not_a_starlark_repository() {
    // TSK-5110 criterion 1, REQ-2348.
    let repo = Repo::new("starlark-none", &[PROFILE, ("rules.bzl", "x = 1\n")]);
    for command in ["status", "bind", "check"] {
        let run = repo.run(&["starlark", command], &[]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out().contains("unresolved: not a Starlark repository"),
            "{command}: {}",
            run.out()
        );
    }
}

#[test]
fn bind_prints_every_stage_bound_from_the_fixture() {
    // TSK-5110 criterion 2, REQ-2348, REQ-2416, REQ-2442: every stage prints,
    // Bazel runs without its symlinks, and the test report goes outside.
    let repo = bazel("starlark-bind");
    let run = repo.run(&["starlark", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(
        run.bound("format").as_deref(),
        Some("buildifier --mode=check -r .")
    );
    assert_eq!(
        run.bound("lint").as_deref(),
        Some("buildifier --mode=check --lint=warn -r .")
    );
    assert_eq!(
        run.stage("check"),
        ["# check: unresolved, Starlark has no static types"]
    );
    let test = run.bound("test").unwrap();
    assert!(test.contains("bazel test --symlink_prefix=/ "), "{test}");
    assert!(
        test.contains("--build_event_json_file=\"${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-starlark/root/bep.json\""),
        "{test}"
    );
    assert!(test.ends_with(" //..."), "{test}");
    assert_eq!(
        run.bound("build").as_deref(),
        Some("bazel build --symlink_prefix=/ //...")
    );
    for command in ["format", "lint"] {
        let command = run.bound(command).unwrap();
        assert!(!command.contains("--format"), "{command}");
    }
}

#[test]
fn buildifier_binds_only_where_the_repository_configured_it() {
    // TSK-5110 criterion 2, REQ-2348, REQ-2420, REQ-2422: with no
    // .buildifier.json the format stage is unbound, and one that doesn't ask
    // for lint warnings leaves lint unbound.
    let bare = Repo::new(
        "starlark-bare",
        &[PROFILE, ("MODULE.bazel", "module(name = \"s\")\n")],
    );
    let run = bare.run(&["starlark", "bind"], &[]);
    run.every_stage_printed();
    assert!(run.bound("format").is_none(), "{}", run.out());
    assert!(run.bound("lint").is_none(), "{}", run.out());
    let quiet = Repo::new(
        "starlark-quiet",
        &[
            PROFILE,
            ("MODULE.bazel", "module(name = \"s\")\n"),
            (".buildifier.json", "{}\n"),
        ],
    );
    let run = quiet.run(&["starlark", "bind"], &[]);
    assert_eq!(
        run.bound("format").as_deref(),
        Some("buildifier --mode=check -r .")
    );
    assert!(run.bound("lint").is_none(), "{}", run.out());
}

#[test]
fn the_build_system_is_detected_before_any_stage_binds() {
    // TSK-5110 criterion 3, REQ-2446: a directory holding a Bazel and a Buck
    // marker leaves every stage unresolved.
    let repo = Repo::new(
        "starlark-both",
        &[
            PROFILE,
            ("MODULE.bazel", "module(name = \"s\")\n"),
            (".buckconfig", "[cells]\n"),
            (".buildifier.json", LINTED),
        ],
    );
    let run = repo.run(&["starlark", "bind"], &[]);
    assert_eq!(run.code(), 3, "{}", run.out());
    for stage in ["format", "lint", "check", "test", "build"] {
        let lines = run.stage(stage);
        assert!(
            lines.len() == 1
                && lines[0].starts_with(&format!(
                    "# {stage}: unresolved, Bazel and Buck are all detected"
                )),
            "{stage}: {}",
            run.out()
        );
    }
    let status = repo.run(&["starlark", "status"], &[]);
    assert_eq!(status.code(), 3, "{}", status.out());
}

#[test]
fn a_buck_project_binds_no_build_or_test() {
    // TSK-5110 criterion 3, REQ-2442: buck-out lands in the tree and no
    // documented flag moves it, so build and test stay unbound and check
    // reports a buck-out nobody ignores.
    let repo = Repo::new(
        "starlark-buck",
        &[
            (".meowpaw/profile.toml", "[stages]\n"),
            (".buckconfig", "[cells]\n"),
        ],
    );
    let run = repo.run(&["starlark", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    for stage in ["test", "build"] {
        assert!(run.bound(stage).is_none(), "{stage}: {}", run.out());
        assert!(run.stage(stage)[0].contains("buck-out"), "{}", run.out());
    }
    let check = repo.run(&["starlark", "check"], &[]);
    assert_eq!(check.code(), 1, "{}", check.out());
    assert!(
        check.out().contains(".: buck-out/ isn't ignored"),
        "{}",
        check.out()
    );
    let ignored = Repo::new(
        "starlark-buck-ignored",
        &[
            (".meowpaw/profile.toml", "[stages]\n"),
            (".buckconfig", "[cells]\n"),
            (".gitignore", "buck-out/\n"),
        ],
    );
    assert_eq!(ignored.run(&["starlark", "check"], &[]).code(), 0);
}

#[test]
fn status_names_the_generated_files_to_commit_and_to_ignore() {
    // TSK-5110 criterion 3, REQ-2450.
    let repo = bazel("starlark-state");
    let run = repo.run(&["starlark", "status"], &[]);
    assert!(
        run.out().contains(
            "commit: the workspace markers and .buildifier.json, which are project state"
        ),
        "{}",
        run.out()
    );
    assert!(
        run.out().contains("ignore: bazel-*, which are Bazel's convenience symlinks, and buck-out/, which is Buck's output"),
        "{}",
        run.out()
    );
}

#[test]
fn check_reports_a_buildifier_stage_that_passes_whatever_it_finds() {
    // TSK-5110 criterion 3, REQ-2416: buildifier exits 0 whenever it is given
    // --format, and rewrites files without --mode=check.
    let repo = with_stages(
        "starlark-format",
        "format = \"buildifier --mode=check --format=json -r .\"\nlint = \"buildifier -r .\"",
        &[],
    );
    let run = repo.run(&["starlark", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    assert!(
        run.out().contains(
            "format runs buildifier with --format; its exit status is 0 whatever it finds"
        ),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("lint runs buildifier without --mode=check, which rewrites the files"),
        "{}",
        run.out()
    );
}

#[test]
fn check_reports_bazel_symlinks_written_into_the_tree() {
    // TSK-5110 criterion 3, REQ-2442: a bazel stage without
    // --symlink_prefix=/ is a finding, and so are symlinks nothing ignores.
    let repo = Repo::new(
        "starlark-symlinks",
        &[
            (
                ".meowpaw/profile.toml",
                "[stages]\ntest = \"bazel test //...\"\n",
            ),
            ("MODULE.bazel", "module(name = \"s\")\n"),
        ],
    );
    let run = repo.run(&["starlark", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    assert!(
        run.out()
            .contains("test runs bazel without --symlink_prefix=/"),
        "{}",
        run.out()
    );
    assert!(
        run.out().contains(".: bazel-* symlinks aren't ignored"),
        "{}",
        run.out()
    );
}

#[test]
fn a_clean_check_names_what_it_checked() {
    // TSK-5110 criterion 3, REQ-2442, REQ-2416: stages that follow the rules
    // have no finding.
    let repo = with_stages(
        "starlark-clean",
        "format = \"buildifier --mode=check -r .\"\ntest = \"bazel test --symlink_prefix=/ //...\"",
        &[],
    );
    let run = repo.run(&["starlark", "check"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("no findings"), "{}", run.out());
}

#[test]
fn two_workspaces_bind_one_command_that_runs_each_in_its_directory() {
    // TSK-5110 criterion 1, REQ-3048.
    let repo = Repo::new(
        "starlark-two",
        &[
            PROFILE,
            ("a/MODULE.bazel", "module(name = \"a\")\n"),
            ("b/MODULE.bazel", "module(name = \"b\")\n"),
        ],
    );
    let run = repo.run(&["starlark", "bind"], &[]);
    assert_eq!(
        run.bound("build").as_deref(),
        Some(
            "(cd a && bazel build --symlink_prefix=/ //...) && (cd b && bazel build --symlink_prefix=/ //...)"
        )
    );
}

#[test]
fn the_pack_leaves_the_tree_as_it_found_it() {
    // REQ-2442 as SPC-1190 states it: status, bind and check write nothing.
    let repo = bazel("starlark-writes");
    let before = repo.files();
    for command in ["status", "bind", "check"] {
        repo.run(&["starlark", command], &[]);
    }
    assert_eq!(repo.files(), before);
}
