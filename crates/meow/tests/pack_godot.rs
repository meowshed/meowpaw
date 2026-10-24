// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-godot` on fixture repositories (TSK-5105, SPC-1380).

#![cfg(feature = "godot")]

mod perdir_fixture;

use perdir_fixture::{PROFILE, Repo};

fn project(version: &str) -> String {
    format!(
        "; Engine configuration file.\nconfig_version=5\n\n[application]\n\nconfig/name=\"Shop\"\nconfig/features=PackedStringArray(\"{version}\", \"Forward Plus\")\n"
    )
}

const PRESETS: &str = "[preset.0]\n\nname=\"Linux\"\nplatform=\"Linux\"\nexport_path=\"build/shop.x86_64\"\n\n[preset.0.options]\n\nbinary_format/embed_pck=true\n\n[preset.1]\n\nname=\"Web\"\nplatform=\"Web\"\nexport_path=\"build/index.html\"\n";

/// A Godot project with gdtoolkit, GUT and export presets configured.
fn game(name: &str, version: &str) -> Repo {
    let text = project(version);
    Repo::new(
        name,
        &[
            PROFILE,
            ("project.godot", &text),
            ("gdformatrc", "line_length: 100\n"),
            ("gdlintrc", "max-line-length: 100\n"),
            (".gutconfig.json", "{ \"dirs\": [\"res://test/\"] }\n"),
            ("addons/gut/gut_cmdln.gd", "extends SceneTree\n"),
            ("export_presets.cfg", PRESETS),
            (".gitignore", ".godot/\n"),
            ("player.gd", "extends Node\n"),
            ("player.gd.uid", "uid://b1\n"),
        ],
    )
}

#[test]
fn status_reports_for_the_directory_holding_the_marker() {
    // TSK-5105 criterion 1, REQ-2346, REQ-3048: a project in a subdirectory is
    // reported for that directory, naming the marker and the engine.
    let text = project("4.3");
    let repo = Repo::new("godot-sub", &[PROFILE, ("game/project.godot", &text)]);
    let run = repo.run(&["godot", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("scope: game\n"), "{}", run.out());
    assert!(
        run.out().contains("marker: game/project.godot"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("engine: Godot 4.3, from game/project.godot"),
        "{}",
        run.out()
    );
    assert!(!run.out().contains("scope: .\n"), "{}", run.out());
}

#[test]
fn a_work_tree_with_no_marker_is_not_a_godot_repository() {
    // TSK-5105 criterion 1, REQ-2346.
    let repo = Repo::new("godot-none", &[PROFILE, ("player.gd", "extends Node\n")]);
    for command in ["status", "bind", "check"] {
        let run = repo.run(&["godot", command], &[]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out()
                .contains("unresolved: not a Godot and GDScript repository"),
            "{command}: {}",
            run.out()
        );
    }
}

#[test]
fn bind_prints_every_stage_bound_from_the_fixture() {
    // TSK-5105 criterion 2, REQ-2346, REQ-2416, REQ-2442: every stage is
    // bound from what the fixture commits, and the output goes outside.
    let repo = game("godot-bind", "4.3");
    let run = repo.run(&["godot", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(run.bound("format").as_deref(), Some("gdformat --check ."));
    assert_eq!(run.bound("lint").as_deref(), Some("gdlint ."));
    assert!(
        run.stage("check")[0].starts_with("# check: unbound, "),
        "{}",
        run.out()
    );
    let test = run.bound("test").unwrap();
    assert!(test.contains("-s addons/gut/gut_cmdln.gd -gexit"), "{test}");
    assert!(
        test.contains("-gjunit_xml_file=\"${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-godot/root/junit.xml\""),
        "{test}"
    );
    assert!(test.contains("mkdir -p"), "{test}");
    let build = run.bound("build").unwrap();
    assert!(
        build.contains("--export-release Linux \"${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-godot/root/shop.x86_64\"")
            || build.contains("--export-release \"Linux\" \"${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-godot/root/shop.x86_64\""),
        "{build}"
    );
    assert!(
        run.out().contains("# export_presets.cfg also defines Web"),
        "a second preset is named: {}",
        run.out()
    );
}

#[test]
fn a_bare_project_names_the_reason_for_each_stage() {
    // TSK-5105 criterion 2, REQ-2346, REQ-2420: a project that configured
    // nothing gets every stage commented with what the pack looked for, and
    // the pack picks no tool the repository didn't configure.
    let text = project("4.3");
    let repo = Repo::new("godot-bare", &[PROFILE, ("project.godot", &text)]);
    let run = repo.run(&["godot", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(run.bound(stage).is_none(), "{stage}: {}", run.out());
    }
}

#[test]
fn the_engine_version_is_detected_before_any_stage_binds() {
    // TSK-5105 criterion 3, REQ-2446: a project file naming no version leaves
    // every stage unresolved.
    let repo = Repo::new(
        "godot-host",
        &[
            PROFILE,
            (
                "project.godot",
                "config_version=5\n\n[application]\n\nconfig/name=\"Shop\"\n",
            ),
            ("gdformatrc", "\n"),
        ],
    );
    let run = repo.run(&["godot", "bind"], &[]);
    assert_eq!(run.code(), 3, "{}", run.out());
    for stage in ["format", "lint", "check", "test", "build"] {
        let lines = run.stage(stage);
        assert!(
            lines.len() == 1
                && lines[0].starts_with(&format!(
                    "# {stage}: unresolved, Godot engine version not detected"
                )),
            "{stage}: {}",
            run.out()
        );
    }
    let status = repo.run(&["godot", "status"], &[]);
    assert_eq!(status.code(), 3, "{}", status.out());
    assert!(
        status
            .out()
            .contains("unresolved: Godot engine version not detected"),
        "{}",
        status.out()
    );
}

#[test]
fn every_run_of_the_engine_imports_first() {
    // TSK-5105 criterion 3, REQ-2448: --export-release imports nothing, so the
    // build and a test run that loads scenes import explicitly first.
    let repo = game("godot-import", "4.3");
    let run = repo.run(&["godot", "bind"], &[]);
    for stage in ["test", "build"] {
        let command = run.bound(stage).unwrap();
        assert!(
            command.starts_with("godot --headless --path . --import && "),
            "{stage}: {command}"
        );
    }
}

#[test]
fn status_names_the_generated_files_to_commit_and_to_ignore() {
    // TSK-5105 criterion 3, REQ-2450: the files to commit and to ignore are
    // stated, and the fixture, which follows them, has no finding.
    let repo = game("godot-state", "4.4");
    let run = repo.run(&["godot", "status"], &[]);
    assert!(
        run.out()
            .contains("commit: *.import and *.uid, which are project state"),
        "{}",
        run.out()
    );
    assert!(
        run.out()
            .contains("ignore: .godot/, which is the engine's cache"),
        "{}",
        run.out()
    );
    let clean = repo.run(&["godot", "check"], &[]);
    assert_eq!(clean.code(), 0, "{}", clean.out());
    assert!(clean.out().contains("no findings"), "{}", clean.out());
}

#[test]
fn check_reports_generated_files_committed_or_ignored_wrongly() {
    // TSK-5105 criterion 3, REQ-2450: an ignored .uid, an ignored .import, a
    // .godot/ nobody ignores and a tracked cache file are each a finding.
    let text = project("4.4");
    let repo = Repo::new(
        "godot-wrong",
        &[
            PROFILE,
            ("project.godot", &text),
            (".gitignore", "*.uid\n*.import\n"),
            (".godot/uid_cache.bin", "x"),
        ],
    );
    let run = repo.run(&["godot", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    for needle in [
        ".: *.uid files are ignored",
        ".: *.import files are ignored",
        ".: .godot/ isn't ignored",
        ".: .godot/ is tracked: .godot/uid_cache.bin",
    ] {
        assert!(run.out().contains(needle), "{needle}: {}", run.out());
    }
}

#[test]
fn check_reports_an_export_that_imports_nothing() {
    // TSK-5105 criterion 3, REQ-2448: a declared stage that exports a release
    // with no import is a finding.
    let text = project("4.3");
    let repo = Repo::new(
        "godot-noimport",
        &[
            (
                ".meowpaw/profile.toml",
                "[stages]\nbuild = \"godot --headless --export-release Linux out/shop\"\n",
            ),
            ("project.godot", &text),
            (".gitignore", ".godot/\n"),
        ],
    );
    let run = repo.run(&["godot", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    assert!(
        run.out()
            .contains("build exports with --export-release and imports nothing first"),
        "{}",
        run.out()
    );
}

#[test]
fn an_older_engine_s_export_presets_are_never_read() {
    // RES-0108 as SPC-1380 states it: before 4.1 the presets may hold
    // credentials, so build stays unbound and names why, and check reports a
    // tracked file.
    let repo = game("godot-old", "4.0");
    let run = repo.run(&["godot", "bind"], &[]);
    assert!(run.bound("build").is_none(), "{}", run.out());
    assert!(
        run.stage("build")[0].contains("credentials"),
        "{}",
        run.out()
    );
    assert!(!run.out().contains("Linux"), "{}", run.out());
    let check = repo.run(&["godot", "check"], &[]);
    assert_eq!(check.code(), 1, "{}", check.out());
    assert!(
        check
            .out()
            .contains(".: export_presets.cfg is tracked, and Godot 4.0 may store credentials"),
        "{}",
        check.out()
    );
}

#[test]
fn two_projects_bind_one_command_that_runs_each_in_its_directory() {
    // TSK-5105 criterion 1, REQ-3048: each directory's command runs in that
    // directory, and the stage joins them.
    let text = project("4.3");
    let repo = Repo::new(
        "godot-two",
        &[
            PROFILE,
            ("a/project.godot", &text),
            ("a/gdformatrc", "\n"),
            ("b/project.godot", &text),
            ("b/gdformatrc", "\n"),
        ],
    );
    let run = repo.run(&["godot", "bind"], &[]);
    assert_eq!(
        run.bound("format").as_deref(),
        Some("(cd a && gdformat --check .) && (cd b && gdformat --check .)")
    );
}

#[test]
fn the_pack_leaves_the_tree_as_it_found_it() {
    // REQ-2442 as SPC-1190 states it: status, bind and check write nothing.
    let repo = game("godot-writes", "4.3");
    let before = repo.files();
    for command in ["status", "bind", "check"] {
        repo.run(&["godot", command], &[]);
    }
    assert_eq!(repo.files(), before);
}
