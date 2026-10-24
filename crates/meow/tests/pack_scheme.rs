// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-scheme` on fixture repositories (TSK-5115, SPC-1390).

#![cfg(feature = "scheme")]

mod perdir_fixture;

use perdir_fixture::{PROFILE, Repo};

const INFO: &str = "#lang info\n(define collection \"shop\")\n";

/// A Racket collection that declares which paths its tests skip.
fn racket(name: &str) -> Repo {
    Repo::new(
        name,
        &[
            PROFILE,
            (
                "info.rkt",
                "#lang info\n(define collection \"shop\")\n(define test-omit-paths '(\"slow\"))\n",
            ),
            ("main.rkt", "#lang racket\n"),
            (".gitignore", "compiled/\n"),
        ],
    )
}

#[test]
fn status_reports_for_the_directory_holding_the_marker() {
    // TSK-5115 criterion 1, REQ-2350, REQ-3048: a collection in a
    // subdirectory is reported for that directory, naming the marker and the
    // implementation.
    let repo = Repo::new("scheme-sub", &[PROFILE, ("lib/info.rkt", INFO)]);
    let run = repo.run(&["scheme", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("scope: lib\n"), "{}", run.out());
    assert!(run.out().contains("marker: lib/info.rkt"), "{}", run.out());
    assert!(
        run.out()
            .contains("implementation: Racket, from lib/info.rkt"),
        "{}",
        run.out()
    );
    assert!(!run.out().contains("scope: .\n"), "{}", run.out());
}

#[test]
fn a_directory_of_scm_files_is_not_a_scheme_repository() {
    // TSK-5115 criterion 1, REQ-2350, REQ-2446: a `.scm` file names Scheme and
    // no implementation, so it activates nothing.
    let repo = Repo::new("scheme-none", &[PROFILE, ("config.scm", "(define x 1)\n")]);
    for command in ["status", "bind", "check"] {
        let run = repo.run(&["scheme", command], &[]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out().contains("unresolved: not a Scheme repository"),
            "{command}: {}",
            run.out()
        );
    }
}

#[test]
fn bind_prints_every_stage_for_a_racket_collection() {
    // TSK-5115 criterion 2, REQ-2350, REQ-2420, REQ-2442: tests bind to
    // raco test without --make, and no stage binds a command the repository
    // didn't configure or one that writes bytecode into the tree.
    let repo = racket("scheme-bind");
    let run = repo.run(&["scheme", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(run.bound("test").as_deref(), Some("raco test --table ."));
    assert!(
        run.stage("format")[0].starts_with("# format: unbound, raco fmt has no check mode"),
        "{}",
        run.out()
    );
    for stage in ["format", "lint", "check", "build"] {
        assert!(run.bound(stage).is_none(), "{stage}: {}", run.out());
    }
    assert!(run.stage("build")[0].contains("compiled/"), "{}", run.out());
    assert!(!run.out().contains("--make"), "{}", run.out());
}

#[test]
fn the_implementation_is_detected_before_any_stage_binds() {
    // TSK-5115 criterion 3, REQ-2446: a directory holding Racket's and
    // CHICKEN's markers leaves every stage unresolved.
    let repo = Repo::new(
        "scheme-both",
        &[
            PROFILE,
            ("info.rkt", INFO),
            ("shop.egg", "((author \"a\"))\n"),
        ],
    );
    let run = repo.run(&["scheme", "bind"], &[]);
    assert_eq!(run.code(), 3, "{}", run.out());
    for stage in ["format", "lint", "check", "test", "build"] {
        let lines = run.stage(stage);
        assert!(
            lines.len() == 1
                && lines[0].starts_with(&format!(
                    "# {stage}: unresolved, Racket and CHICKEN are all detected"
                )),
            "{stage}: {}",
            run.out()
        );
    }
    assert_eq!(repo.run(&["scheme", "status"], &[]).code(), 3);
}

#[test]
fn chicken_binds_no_command() {
    // TSK-5115 criterion 3, REQ-2446, REQ-2420: a CHICKEN egg has no command
    // the repository committed, so each stage is unbound naming it.
    let repo = Repo::new("scheme-egg", &[PROFILE, ("shop.egg", "((author \"a\"))\n")]);
    let run = repo.run(&["scheme", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            run.stage(stage)[0].starts_with(&format!(
                "# {stage}: unbound, no command is bound for CHICKEN"
            )),
            "{stage}: {}",
            run.out()
        );
    }
}

#[test]
fn status_names_the_generated_files_and_the_test_discovery() {
    // TSK-5115 criterion 3, REQ-2450: what to commit and what to ignore, and
    // what info.rkt declares about test discovery.
    let repo = racket("scheme-state");
    let run = repo.run(&["scheme", "status"], &[]);
    assert!(
        run.out()
            .contains("commit: info.rkt, which is project state"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("ignore: compiled/, which is bytecode written beside each source"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("test discovery: info.rkt declares test-omit-paths"),
        "{}",
        run.out()
    );
    let plain = Repo::new("scheme-plain", &[PROFILE, ("info.rkt", INFO)]);
    assert!(
        plain
            .run(&["scheme", "status"], &[])
            .out()
            .contains("test discovery: info.rkt declares none, so raco test runs every file"),
    );
}

#[test]
fn check_reports_a_stage_that_writes_bytecode_into_the_tree() {
    // TSK-5115 criterion 3, REQ-2442: raco make, and raco test with --make,
    // write compiled/ beside each source.
    let repo = Repo::new(
        "scheme-make",
        &[
            (
                ".meowpaw/profile.toml",
                "[stages]\nbuild = \"raco make main.rkt\"\ntest = \"raco test --make .\"\n",
            ),
            ("info.rkt", INFO),
            (".gitignore", "compiled/\n"),
        ],
    );
    let run = repo.run(&["scheme", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    for stage in ["build", "test"] {
        assert!(
            run.out().contains(&format!(
                "{stage} runs raco make or --make, which writes compiled/ into the tree"
            )),
            "{stage}: {}",
            run.out()
        );
    }
}

#[test]
fn check_reports_bytecode_nobody_ignores_or_a_repository_tracks() {
    // TSK-5115 criterion 3, REQ-2450.
    let repo = Repo::new(
        "scheme-compiled",
        &[PROFILE, ("info.rkt", INFO), ("compiled/main_rkt.zo", "x")],
    );
    let run = repo.run(&["scheme", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    assert!(
        run.out().contains(".: compiled/ isn't ignored"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains(".: compiled/ is tracked: compiled/main_rkt.zo"),
        "{}",
        run.out()
    );
}

#[test]
fn a_clean_check_names_what_it_checked() {
    // TSK-5115 criterion 3, REQ-2442, REQ-2450.
    let repo = racket("scheme-clean");
    let run = repo.run(&["scheme", "check"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("no findings"), "{}", run.out());
}

#[test]
fn two_collections_bind_one_command_that_runs_each_in_its_directory() {
    // TSK-5115 criterion 1, REQ-3048.
    let repo = Repo::new(
        "scheme-two",
        &[PROFILE, ("a/info.rkt", INFO), ("b/info.rkt", INFO)],
    );
    let run = repo.run(&["scheme", "bind"], &[]);
    assert_eq!(
        run.bound("test").as_deref(),
        Some("(cd a && raco test --table .) && (cd b && raco test --table .)")
    );
}

#[test]
fn the_pack_leaves_the_tree_as_it_found_it() {
    // REQ-2442 as SPC-1190 states it: status, bind and check write nothing.
    let repo = racket("scheme-writes");
    let before = repo.files();
    for command in ["status", "bind", "check"] {
        repo.run(&["scheme", command], &[]);
    }
    assert_eq!(repo.files(), before);
}
