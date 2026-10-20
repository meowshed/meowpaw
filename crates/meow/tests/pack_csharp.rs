// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-csharp` on fixture repositories (TSK-5095, SPC-1360).

#![cfg(feature = "csharp")]

mod langpack_fixture;

use langpack_fixture::{PROFILE, Repo};

const PROJECT: &str = "<Project Sdk=\"Microsoft.NET.Sdk\">\n  <PropertyGroup>\n    <TargetFramework>net10.0</TargetFramework>\n  </PropertyGroup>\n</Project>\n";
const TESTS: &str = "<Project Sdk=\"Microsoft.NET.Sdk\">\n  <ItemGroup>\n    <PackageReference Include=\"Microsoft.NET.Test.Sdk\" Version=\"18.0.0\" />\n    <PackageReference Include=\"xunit.v3\" Version=\"3.1.0\" />\n  </ItemGroup>\n</Project>\n";
const POLICY: &str = "<Project>\n  <PropertyGroup>\n    <Nullable>enable</Nullable>\n    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>\n    <AnalysisLevel>latest-recommended</AnalysisLevel>\n  </PropertyGroup>\n</Project>\n";

/// A solution with a library and a test project, the policy file setting all
/// three settings and CSharpier configured.
fn configured(name: &str) -> Repo {
    Repo::new(
        name,
        &[
            PROFILE,
            (
                "Shop.slnx",
                "<Solution>\n  <Project Path=\"src/Shop/Shop.csproj\" />\n</Solution>\n",
            ),
            ("src/Shop/Shop.csproj", PROJECT),
            ("tests/Shop.Tests/Shop.Tests.csproj", TESTS),
            ("Directory.Build.props", POLICY),
            (".csharpierrc", "printWidth: 100\n"),
        ],
    )
}

/// A fake `dotnet` root holding the SDKs named.
fn dotnet_root(repo: &Repo, versions: &[&str]) -> String {
    let root = repo.0.join(".git/fake-dotnet");
    for version in versions {
        std::fs::create_dir_all(root.join("sdk").join(version)).unwrap();
    }
    std::fs::create_dir_all(&root).unwrap();
    root.display().to_string()
}

#[test]
fn status_reports_for_the_directory_holding_the_marker() {
    // TSK-5095 criterion 1, REQ-2340, REQ-3048: a project in a subdirectory
    // is reported for that directory, naming the marker, and nothing is
    // reported for the root.
    let repo = Repo::new("csharp-sub", &[PROFILE, ("app/App.csproj", PROJECT)]);
    let run = repo.run(&["csharp", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    let lines = run.lines();
    assert!(lines.iter().any(|l| l == "scope: app"), "{}", run.out());
    assert!(
        lines.iter().any(|l| l == "marker: app/App.csproj"),
        "{}",
        run.out()
    );
    assert!(!lines.iter().any(|l| l == "scope: ."), "{}", run.out());
}

#[test]
fn a_work_tree_with_no_marker_is_not_a_c_sharp_repository() {
    // TSK-5095 criterion 1, REQ-2340: with no marker every command prints the
    // unresolved line and exits 3.
    let repo = Repo::new("csharp-none", &[PROFILE, ("README.md", "# x\n")]);
    for command in ["status", "bind", "check"] {
        let run = repo.run(&["csharp", command], &[]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out().contains("unresolved: not a C# repository"),
            "{command}: {}",
            run.out()
        );
    }
}

#[test]
fn a_project_under_a_solution_is_covered_by_the_solution() {
    // REQ-3048: the solution's directory activates, and its projects don't
    // activate again on their own.
    let repo = configured("csharp-covered");
    let run = repo.run(&["csharp", "status"], &[]);
    let lines = run.lines();
    assert!(lines.iter().any(|l| l == "scope: ."), "{}", run.out());
    assert!(
        lines.iter().any(|l| l == "marker: Shop.slnx"),
        "{}",
        run.out()
    );
    assert!(!run.out().contains("scope: src/Shop"), "{}", run.out());
    assert!(!run.out().contains("Shop.csproj"), "{}", run.out());
}

#[test]
fn bind_prints_every_stage_bound_from_the_fixture() {
    // TSK-5095 criterion 2, REQ-2340: every stage is bound from what the
    // fixture commits.
    let repo = configured("csharp-bind");
    let run = repo.run(&["csharp", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(
        run.bound("format").as_deref(),
        Some("dotnet csharpier check .")
    );
    for stage in ["lint", "check", "test", "build"] {
        assert!(
            run.bound(stage).is_some(),
            "{stage} unbound:\n{}",
            run.out()
        );
    }
    assert!(run.bound("test").unwrap().contains("dotnet test Shop.slnx"));
}

#[test]
fn bind_names_the_reason_for_each_stage_it_leaves_unbound() {
    // TSK-5095 criterion 2, REQ-2340, REQ-2422: a project that set no policy,
    // no formatter and no tests gets each of those stages commented with its
    // reason, and the pack turns on no warning as an error itself.
    let repo = Repo::new("csharp-bare", &[PROFILE, ("App.csproj", PROJECT)]);
    let run = repo.run(&["csharp", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    for stage in ["format", "lint", "test"] {
        assert!(run.bound(stage).is_none(), "{stage} bound:\n{}", run.out());
    }
    assert!(
        run.stage("lint")[0].contains("TreatWarningsAsErrors"),
        "{}",
        run.out()
    );
    assert!(
        run.stage("format")[0].contains("dotnet format"),
        "{}",
        run.out()
    );
    for line in run.lines() {
        assert!(
            !line.contains("warnaserror") && !line.contains("-p:"),
            "the pack turned on a setting itself: {line}"
        );
    }
}

#[test]
fn every_build_restores_explicitly_first() {
    // TSK-5095 criterion 3, REQ-2448: each command that builds restores in a
    // step of its own and passes --no-restore after it.
    let repo = configured("csharp-restore");
    let run = repo.run(&["csharp", "bind"], &[]);
    for stage in ["lint", "check", "test", "build"] {
        let command = run.bound(stage).unwrap();
        assert!(
            command.starts_with("dotnet restore Shop.slnx --artifacts-path "),
            "{stage}: {command}"
        );
        let (_, rest) = command.split_once(" && ").unwrap();
        assert!(rest.contains("--no-restore"), "{stage}: {command}");
    }
}

#[test]
fn output_goes_outside_the_working_tree() {
    // TSK-5095 criterion 3, REQ-2442: every dotnet command names one
    // artifacts path outside the tree, the test results go under it, and
    // the pack's own commands leave nothing behind.
    let repo = configured("csharp-out");
    let before = repo.files();
    let run = repo.run(&["csharp", "bind"], &[]);
    repo.run(&["csharp", "status"], &[]);
    repo.run(&["csharp", "check"], &[]);
    assert_eq!(repo.files(), before);
    for stage in ["lint", "check", "test", "build"] {
        let command = run.bound(stage).unwrap();
        for part in command.split(" && ") {
            let path = part
                .split_once("--artifacts-path ")
                .map(|(_, rest)| rest.split_whitespace().next().unwrap())
                .unwrap_or_else(|| panic!("{stage}: {part} names no artifacts path"));
            assert!(
                path.starts_with("\"${TMPDIR:-/tmp}/meow-csharp/"),
                "{stage}: {path}"
            );
        }
    }
    let test = run.bound("test").unwrap();
    assert!(
        test.contains("--logger trx --results-directory \"${TMPDIR:-/tmp}/meow-csharp/"),
        "{test}"
    );
}

#[test]
fn the_test_platform_global_json_selects_decides_the_report_flag() {
    // TSK-5095, REQ-2416 as SPC-1360 states it: the TRX flag follows the
    // runner global.json selects.
    let repo = configured("csharp-mtp");
    repo.write(
        "global.json",
        "{ \"test\": { \"runner\": \"Microsoft.Testing.Platform\" } }\n",
    );
    repo.git(&["add", "-A"]);
    let run = repo.run(&["csharp", "bind"], &[]);
    let test = run.bound("test").unwrap();
    assert!(test.contains("dotnet test --solution Shop.slnx "), "{test}");
    assert!(
        test.contains("--results-directory \"${TMPDIR:-/tmp}/meow-csharp/"),
        "{test}"
    );
    assert!(test.ends_with(" -- --report-trx"), "{test}");
    assert!(!test.contains("--logger trx"), "{test}");
}

#[test]
fn a_pinned_sdk_is_read_and_compared_with_the_installed_ones() {
    // TSK-5095 criterion 3, REQ-2428: the pin is printed with what is
    // installed, and an unmet pin is unresolved with both versions.
    let repo = configured("csharp-pin");
    repo.write("global.json", "{ \"sdk\": { \"version\": \"8.0.100\" } }\n");
    repo.git(&["add", "-A"]);
    let met = dotnet_root(&repo, &["8.0.105"]);
    let run = repo.run(&["csharp", "status"], &[("DOTNET_ROOT", &met)]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(
        run.out()
            .contains("sdk: 8.0.100 pinned in global.json, rollForward patch, installed: 8.0.105"),
        "{}",
        run.out()
    );
    std::fs::remove_dir_all(repo.0.join(".git/fake-dotnet")).unwrap();
    let unmet = dotnet_root(&repo, &["9.0.100"]);
    for command in ["status", "bind"] {
        let run = repo.run(&["csharp", command], &[("DOTNET_ROOT", &unmet)]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out()
                .contains("unresolved: dotnet 8.0.100 pinned, 9.0.100 installed"),
            "{command}: {}",
            run.out()
        );
    }
    repo.write(
        "global.json",
        "{ \"sdk\": { \"version\": \"8.0.100\", \"rollForward\": \"latestMajor\" } }\n",
    );
    let run = repo.run(&["csharp", "status"], &[("DOTNET_ROOT", &unmet)]);
    assert_eq!(run.code(), 0, "{}", run.out());
}

#[test]
fn the_analysis_level_it_runs_at_is_stated() {
    // TSK-5095 criterion 3, REQ-2444: lint and check name the analysis level,
    // or the SDK's default where none is set.
    let repo = configured("csharp-level");
    let run = repo.run(&["csharp", "bind"], &[]);
    assert!(
        run.out()
            .contains("# lint and check run at AnalysisLevel latest-recommended"),
        "{}",
        run.out()
    );
    let bare = Repo::new("csharp-level-bare", &[PROFILE, ("App.csproj", PROJECT)]);
    let run = bare.run(&["csharp", "bind"], &[]);
    assert!(
        run.out()
            .contains("# lint and check run at the SDK's default AnalysisLevel"),
        "{}",
        run.out()
    );
}

#[test]
fn check_reports_each_setting_that_decides_whether_lint_means_anything() {
    // TSK-5095 criterion 3, REQ-2444: a project setting none of Nullable,
    // TreatWarningsAsErrors and AnalysisLevel gets a finding for each.
    let bare = Repo::new("csharp-check", &[PROFILE, ("App.csproj", PROJECT)]);
    let run = bare.run(&["csharp", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    for setting in ["Nullable", "TreatWarningsAsErrors", "AnalysisLevel"] {
        assert!(
            run.lines()
                .iter()
                .any(|l| l.contains(".: ") && l.contains(setting)),
            "{setting}: {}",
            run.out()
        );
    }
    let repo = configured("csharp-check-clean");
    let run = repo.run(&["csharp", "check"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert!(run.out().contains("no findings"), "{}", run.out());
}

#[test]
fn two_solutions_in_one_directory_bind_no_stage() {
    // REQ-2420 as SPC-1360 states it: the pack never picks between two
    // solutions.
    let repo = configured("csharp-two");
    repo.write("Other.sln", "\n");
    repo.git(&["add", "-A"]);
    let run = repo.run(&["csharp", "bind"], &[]);
    run.every_stage_printed();
    for stage in ["lint", "check", "test", "build"] {
        assert!(run.bound(stage).is_none(), "{stage}: {}", run.out());
        assert!(run.stage(stage)[0].contains("Other.sln"), "{}", run.out());
    }
}
