// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The TypeScript and JavaScript pack, `meow-typescript`, on fixture
//! repositories (TSK-5080, SPC-1320).

#![cfg(feature = "typescript")]

mod packs_common;
use packs_common::{fixture, paw, profile, started};

const PACKAGE: &str = "{\"name\":\"x\",\"scripts\":{\"build\":\"vite build\"},\"devDependencies\":{\"vitest\":\"5.0.4\"}}\n";
const BARE: &str = "{\"name\":\"x\"}\n";

/// The files of a package that configures every tool the pack binds.
fn configured() -> Vec<(&'static str, &'static str)> {
    vec![
        ("package.json", PACKAGE),
        ("pnpm-lock.yaml", "lockfileVersion: 9\n"),
        (".prettierrc", "{}\n"),
        ("eslint.config.js", "export default [];\n"),
        ("tsconfig.json", "{\"compilerOptions\":{\"strict\":true}}\n"),
    ]
}

/// TSK-5080 criterion 1, REQ-2338, REQ-0133, REQ-3048: a `package.json` in
/// `web/` and none at the root makes `status` report for `web` alone, name
/// the marker, and start no tool.
#[test]
fn status_reports_for_the_directory_holding_its_marker() {
    let (dir, bin) = fixture(
        "ts-status",
        &[
            ("web/package.json", BARE),
            ("web/pnpm-lock.yaml", ""),
            ("README.md", "# r\n"),
        ],
        &["pnpm", "node", "eslint"],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "status"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert_eq!(
        lines
            .iter()
            .filter(|l| l.starts_with("scope:"))
            .collect::<Vec<_>>(),
        ["scope: web"]
    );
    assert!(
        lines.contains(&"marker: web/package.json".to_string()),
        "{lines:?}"
    );
    assert!(
        lines.contains(&"package manager: pnpm, declared by web/pnpm-lock.yaml".to_string()),
        "{lines:?}"
    );
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5080 criterion 1, REQ-2338: with no marker every command prints the
/// unresolved line and exits 3.
#[test]
fn with_no_marker_every_command_is_unresolved() {
    let (dir, bin) = fixture("ts-none", &[("README.md", "# r\n")], &["node"]);
    for command in ["status", "bind", "check"] {
        let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", command]);
        assert_eq!(done.status.code(), Some(3), "{command}: {lines:?}");
        assert!(
            lines.contains(&"unresolved: not a TypeScript and JavaScript repository".to_string()),
            "{command}: {lines:?}"
        );
    }
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5080 criterion 1, REQ-3048: markers in two directories make `status`
/// report once for each, and a declared part is named.
#[test]
fn status_reports_once_per_directory_and_names_a_part() {
    let (dir, bin) = fixture(
        "ts-two",
        &[
            ("package.json", BARE),
            ("package-lock.json", "{}\n"),
            ("web/package.json", BARE),
            ("web/yarn.lock", ""),
            (".meowpaw/profile.toml", "[parts]\nweb = \"web\"\n"),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "status"]);
    let scopes: Vec<&String> = lines.iter().filter(|l| l.starts_with("scope:")).collect();
    assert_eq!(scopes, ["scope: .", "scope: web web"], "{lines:?}");
}

/// TSK-5080 criterion 2, REQ-2338: `bind` prints all five stages for a
/// fixture that configures them, each through the declared package manager.
#[test]
fn bind_prints_all_five_stages_from_what_the_fixture_commits() {
    let (dir, bin) = fixture("ts-bind", &configured(), &["prettier", "eslint", "tsc"]);
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert_eq!(
        lines,
        [
            "# meow-typescript bind .: paste what follows into .meowpaw/profile.toml",
            "[stages]",
            "format = \"pnpm exec prettier --check .\"",
            "lint = \"pnpm exec eslint --max-warnings 0 .\"",
            "check = \"pnpm exec tsc --noEmit\"",
            "test = \"pnpm exec vitest run\"",
            "build = \"pnpm run build\"",
        ]
    );
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5080 criterion 2, REQ-2338: a stage nothing configures is printed
/// unbound with what the pack looked for, and never bound from an installed
/// tool.
#[test]
fn bind_prints_an_unconfigured_stage_as_unbound() {
    let (dir, bin) = fixture(
        "ts-unbound",
        &[("package.json", BARE), ("package-lock.json", "{}\n")],
        &["prettier", "eslint", "tsc", "vitest", "jest"],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            lines
                .iter()
                .any(|l| l.starts_with(&format!("# {stage}: unbound, looked for "))),
            "{stage}: {lines:?}"
        );
    }
    assert!(lines.iter().all(|l| !l.contains(" = ")), "{lines:?}");
}

/// TSK-5080 criterion 2, REQ-2426: with no manager declared, every stage is
/// unresolved with the reason.
#[test]
fn bind_without_a_package_manager_leaves_every_stage_unresolved() {
    let (dir, bin) = fixture("ts-nopm", &[("package.json", PACKAGE)], &["npm"]);
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            lines.contains(&format!(
                "# {stage}: unresolved, no package manager declared: commit a lockfile or set packageManager"
            )),
            "{stage}: {lines:?}"
        );
    }
}

/// TSK-5080 criterion 3, REQ-2426: the `packageManager` field names the
/// manager each tool runs through, and a lockfile does where the field is
/// absent.
#[test]
fn each_tool_runs_through_the_manager_the_project_declares() {
    for (files, prefix, source) in [
        (
            vec![
                ("package.json", "{\"packageManager\":\"yarn@4.9.0\"}\n"),
                (".prettierrc", "{}\n"),
            ],
            "yarn run prettier",
            "package.json",
        ),
        (
            vec![
                ("package.json", BARE),
                ("bun.lock", ""),
                (".prettierrc", "{}\n"),
            ],
            "bun x prettier",
            "bun.lock",
        ),
        (
            vec![
                ("package.json", BARE),
                ("package-lock.json", "{}\n"),
                (".prettierrc", "{}\n"),
            ],
            "npm exec -- prettier",
            "package-lock.json",
        ),
    ] {
        let (dir, bin) = fixture("ts-pm", &files, &[]);
        let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
        assert!(
            lines.contains(&format!("format = \"{prefix} --check .\"")),
            "{prefix}: {lines:?}"
        );
        let (_, status, _) = paw(&dir.0, &bin.0, &["typescript", "status"]);
        assert!(
            status
                .iter()
                .any(|l| l.starts_with("package manager:") && l.ends_with(source)),
            "{prefix}: {status:?}"
        );
    }
}

/// TSK-5080 criterion 3, REQ-2426: a manager the field names that no
/// lockfile agrees with, two lockfiles with no field, and an unknown manager
/// each leave the stages unresolved and name both files.
#[test]
fn a_manager_that_cannot_be_told_leaves_the_stages_unresolved() {
    for (files, reason) in [
        (
            vec![
                ("package.json", "{\"packageManager\":\"pnpm@10.0.0\"}\n"),
                ("yarn.lock", ""),
            ],
            "package.json declares pnpm, and yarn.lock locks yarn",
        ),
        (
            vec![
                ("package.json", BARE),
                ("yarn.lock", ""),
                ("pnpm-lock.yaml", ""),
            ],
            "pnpm-lock.yaml and yarn.lock both lock this package; declare packageManager",
        ),
        (
            vec![("package.json", "{\"packageManager\":\"deno@2.0.0\"}\n")],
            "packageManager names deno, which this pack doesn't know",
        ),
    ] {
        let (dir, bin) = fixture("ts-pm-bad", &files, &[]);
        let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
        assert!(
            lines.contains(&format!("# lint: unresolved, {reason}")),
            "{reason}: {lines:?}"
        );
    }
}

/// TSK-5080 criterion 3, REQ-2420: where two linters are configured, the
/// first the document lists binds and the other is named; oxlint beside
/// ESLint binds both, as the project meant; an installed tool binds nothing.
#[test]
fn the_configured_linter_binds_and_the_installed_one_never_does() {
    let (dir, bin) = fixture(
        "ts-lint",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            ("biome.json", "{}\n"),
            ("eslint.config.js", ""),
        ],
        &["eslint", "biome", "oxlint"],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert!(
        lines.contains(&"lint = \"pnpm exec biome ci --error-on-warnings .\"".to_string()),
        "{lines:?}"
    );
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with('#') && l.contains("eslint.config.js") && l.contains("eslint")),
        "{lines:?}"
    );
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("# format: unbound, biome.json configures Biome")),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "ts-oxlint",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (".oxlintrc.json", "{}\n"),
            ("eslint.config.js", ""),
        ],
        &["eslint", "oxlint"],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert!(
        lines.contains(
            &"lint = \"pnpm exec oxlint --deny-warnings && pnpm exec eslint --max-warnings 0 .\""
                .to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2420: an `.eslintrc` configures nothing for
/// ESLint 10, and the stage says so.
#[test]
fn an_eslintrc_binds_nothing_and_is_named() {
    let (dir, bin) = fixture(
        "ts-rc",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (".eslintrc.json", "{}\n"),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind"]);
    assert!(
        lines.iter().any(|l| l.starts_with("# lint: unbound")),
        "{lines:?}"
    );
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with('#') && l.contains(".eslintrc.json") && l.contains("ESLint 9")),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2426: `check` finds a stage that runs a tool by
/// its bare name, and one that runs another manager, and accepts the same
/// tool run through the declared one.
#[test]
fn check_finds_a_tool_run_outside_the_declared_manager() {
    let (dir, bin) = fixture(
        "ts-outside",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[
                    ("lint", "eslint --max-warnings 0 ."),
                    ("test", "npx vitest run"),
                    ("format", "pnpm exec prettier --check ."),
                ]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(&"lint runs eslint outside pnpm: write pnpm exec eslint".to_string()),
        "{lines:?}"
    );
    assert!(
        lines.contains(&"test runs npm, and pnpm-lock.yaml declares pnpm".to_string()),
        "{lines:?}"
    );
    assert!(!lines.iter().any(|l| l.starts_with("format ")), "{lines:?}");
}

/// TSK-5080 criterion 3, REQ-2426: two lockfiles are a finding of `check`.
#[test]
fn check_finds_two_lockfiles() {
    let (dir, bin) = fixture(
        "ts-locks",
        &[
            ("package.json", "{\"packageManager\":\"pnpm@10.0.0\"}\n"),
            ("pnpm-lock.yaml", ""),
            ("yarn.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("format", "pnpm exec prettier --check .")]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(&"pnpm-lock.yaml and yarn.lock both lock this package".to_string()),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2434: ESLint settings `check` reads from where
/// ESLint reads them: no configuration it reads, a legacy file beside a flat
/// one, and a warning that passes.
#[test]
fn check_finds_eslint_settings_that_have_no_effect() {
    let stage = &[("lint", "pnpm exec eslint .")];
    let (dir, bin) = fixture(
        "ts-eslint",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (".eslintrc.json", "{}\n"),
            (".meowpaw/profile.toml", &profile(stage)),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(
            &"eslint reads no configuration: ESLint 10 ignores .eslintrc.json".to_string()
        ),
        "{lines:?}"
    );
    assert!(
        lines.contains(&"eslint exits 0 on warnings: pass --max-warnings 0".to_string()),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "ts-eslint-both",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (".eslintrc.json", "{}\n"),
            ("eslint.config.mjs", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("lint", "pnpm exec eslint --max-warnings 0 .")]),
            ),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert!(
        lines.contains(
            &"eslint ignores .eslintrc.json: ESLint 10 reads eslint.config.mjs alone".to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2434: oxlint passes on a warning unless told
/// otherwise.
#[test]
fn check_finds_oxlint_passing_on_warnings() {
    let (dir, bin) = fixture(
        "ts-oxlint-check",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("lint", "pnpm exec oxlint .")]),
            ),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert!(
        lines.contains(&"oxlint exits 0 on warnings: pass --deny-warnings".to_string()),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2442: `tsc` writes JavaScript beside the
/// sources unless told not to, so `bind` passes `--noEmit` and `check` finds
/// a stage that doesn't, unless the project's `tsconfig.json` sets it.
#[test]
fn tsc_writes_nothing_into_the_tree() {
    let stages = &[("check", "pnpm exec tsc")];
    let (dir, bin) = fixture(
        "ts-tsc",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            ("tsconfig.json", "{\"compilerOptions\":{\"strict\":true}}\n"),
            (".meowpaw/profile.toml", &profile(stages)),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(&"tsc writes JavaScript into the tree: pass --noEmit".to_string()),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "ts-tsc-set",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            // JSONC: a comment and a trailing comma, as tsc reads it.
            (
                "tsconfig.json",
                "{\n  // no output\n  \"compilerOptions\": { \"noEmit\": true, },\n}\n",
            ),
            (".meowpaw/profile.toml", &profile(stages)),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
}

/// TSK-5080 criterion 3, REQ-2338: the preview compiler's name is a finding,
/// because the released compiler is `tsc`.
#[test]
fn check_finds_the_preview_compiler() {
    let (dir, bin) = fixture(
        "ts-tsgo",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("check", "pnpm exec tsgo --noEmit")]),
            ),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert!(
        lines.contains(
            &"check runs tsgo, the TypeScript 7 preview; the compiler is tsc".to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 3, REQ-2432: a clean `check` names what it covered, and
/// a profile that is missing or doesn't parse is unresolved.
#[test]
fn a_clean_check_names_what_it_covered() {
    let (dir, bin) = fixture(
        "ts-clean",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("format", "pnpm exec prettier --check .")]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert!(
        lines.contains(
            &"no findings; rule groups enabled: the package manager, the linter's settings, the compiler's output"
                .to_string()
        ),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "ts-noprofile",
        &[("package.json", BARE), ("package-lock.json", "")],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "check"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: no profile at")),
        "{lines:?}"
    );
}

/// TSK-5080 criterion 2: a `package.json` that doesn't parse is unresolved,
/// and `bind` takes a directory.
#[test]
fn a_broken_package_is_unresolved_and_bind_takes_a_directory() {
    let (dir, bin) = fixture(
        "ts-dir",
        &[
            ("package.json", BARE),
            ("pnpm-lock.yaml", ""),
            ("web/package.json", "{\"packageManager\": "),
            ("api/package.json", BARE),
            ("api/yarn.lock", ""),
            ("api/.prettierrc", "{}\n"),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind", "web"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: web/package.json doesn't parse as JSON:")),
        "{lines:?}"
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind", "api"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert!(
        lines.contains(&"format = \"yarn run prettier --check .\"".to_string()),
        "{lines:?}"
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["typescript", "bind", "docs"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: docs holds no package.json; one is in ")),
        "{lines:?}"
    );
    let (done, _, stderr) = paw(&dir.0, &bin.0, &["typescript", "bind", "a", "b"]);
    assert_eq!(done.status.code(), Some(2));
    assert!(stderr.starts_with("usage: meow-typescript"), "{stderr}");
}

/// TSK-5080 criterion 3, REQ-2450: the page states which generated files to
/// commit and which to ignore, in both distributions.
#[test]
fn the_page_states_the_generated_files() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    for tree in ["plugins", "packages"] {
        let page =
            std::fs::read_to_string(root.join(tree).join("meow-typescript/README.md")).unwrap();
        let section = page
            .split("## Generated files")
            .nth(1)
            .expect("no Generated files section");
        let section = section.split("\n## ").next().unwrap().to_lowercase();
        assert!(
            section.contains("commit") && section.contains("ignore"),
            "{section}"
        );
        assert!(
            section.contains("lockfile") && section.contains("node_modules"),
            "{section}"
        );
    }
}
