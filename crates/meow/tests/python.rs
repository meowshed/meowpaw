// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The Python pack, `meow-python`, on fixture repositories (TSK-5085,
//! SPC-1330).

#![cfg(feature = "python")]

mod packs_common;
use packs_common::{fixture, paw, profile, started};

const PROJECT: &str = "[project]\nname = \"x\"\nversion = \"0.1.0\"\n";
const CACHE: &str = "--cache-dir \"${TMPDIR:-/tmp}/ruff-cache\"";

/// The files of a project that configures every tool the pack binds.
fn configured() -> Vec<(&'static str, &'static str)> {
    vec![
        (
            "pyproject.toml",
            "[project]\nname = \"x\"\n\n[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[tool.ruff]\nline-length = 100\n\n[tool.mypy]\nstrict = true\n\n[tool.pytest.ini_options]\naddopts = \"--doctest-modules\"\n",
        ),
        ("uv.lock", "version = 1\n"),
        (".python-version", "3.13\n"),
    ]
}

/// TSK-5085 criterion 1, REQ-2336, REQ-0133, REQ-3048: a `pyproject.toml` in
/// `api/` and none at the root makes `status` report for `api` alone, name
/// the marker, and start no tool.
#[test]
fn status_reports_for_the_directory_holding_its_marker() {
    let (dir, bin) = fixture(
        "py-status",
        &[
            ("api/pyproject.toml", PROJECT),
            ("api/uv.lock", ""),
            ("api/.python-version", "3.12\n"),
            ("api/setup.py", ""),
            ("README.md", "# r\n"),
        ],
        &["uv", "python", "ruff"],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "status"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert_eq!(
        lines
            .iter()
            .filter(|l| l.starts_with("scope:"))
            .collect::<Vec<_>>(),
        ["scope: api"]
    );
    for expected in [
        "marker: api/pyproject.toml",
        "older layout: api/setup.py",
        "environment: uv, declared by api/uv.lock",
        "pinned: python 3.12 in api/.python-version",
    ] {
        assert!(
            lines.contains(&expected.to_string()),
            "{expected}: {lines:?}"
        );
    }
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5085 criterion 1, REQ-2336: with no marker every command prints the
/// unresolved line and exits 3, and a lone `setup.py` makes no project.
#[test]
fn with_no_marker_every_command_is_unresolved() {
    let (dir, bin) = fixture(
        "py-none",
        &[
            ("README.md", "# r\n"),
            ("setup.py", ""),
            ("requirements.txt", ""),
        ],
        &["python"],
    );
    for command in ["status", "bind", "check"] {
        let (done, lines, _) = paw(&dir.0, &bin.0, &["python", command]);
        assert_eq!(done.status.code(), Some(3), "{command}: {lines:?}");
        assert!(
            lines.contains(&"unresolved: not a Python repository".to_string()),
            "{command}: {lines:?}"
        );
    }
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5085 criterion 1, REQ-3048: two projects make `status` report once for
/// each, and a declared part is named.
#[test]
fn status_reports_once_per_directory_and_names_a_part() {
    let (dir, bin) = fixture(
        "py-two",
        &[
            ("pyproject.toml", PROJECT),
            ("services/api/pyproject.toml", PROJECT),
            (".meowpaw/profile.toml", "[parts]\napi = \"services/api\"\n"),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "status"]);
    let scopes: Vec<&String> = lines.iter().filter(|l| l.starts_with("scope:")).collect();
    assert_eq!(scopes, ["scope: .", "scope: api services/api"], "{lines:?}");
}

/// TSK-5085 criterion 2, REQ-2336: `bind` prints the stages the fixture
/// configures, each through the declared environment, and the build stage
/// unbound with the build backend.
#[test]
fn bind_prints_all_five_stages_from_what_the_fixture_commits() {
    let (dir, bin) = fixture("py-bind", &configured(), &["ruff", "mypy", "pytest"]);
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    let text = lines.join("\n");
    for expected in [
        "# meow-python bind .: paste what follows into .meowpaw/profile.toml".to_string(),
        "[stages]".to_string(),
        format!("format = \"uv run ruff format --check {} .\"", CACHE.replace('"', "\\\"")),
        format!("lint = \"uv run ruff check {} .\"", CACHE.replace('"', "\\\"")),
        "check = \"uv run mypy --cache-dir=/dev/null\"".to_string(),
        "test = \"uv run python -B -m pytest -p no:cacheprovider\"".to_string(),
        "# build: unbound, pyproject.toml names the build backend hatchling.build, and this pack binds no build".to_string(),
    ] {
        assert!(lines.contains(&expected), "{expected}\n{text}");
    }
    assert!(!started(&bin.0), "a tool started");
}

/// TSK-5085 criterion 2, REQ-2336: a stage nothing configures is printed
/// unbound with what the pack looked for, and never bound from an installed
/// tool.
#[test]
fn bind_prints_an_unconfigured_stage_as_unbound() {
    let (dir, bin) = fixture(
        "py-unbound",
        &[("pyproject.toml", PROJECT), ("uv.lock", "")],
        &["ruff", "mypy", "pyright", "pytest"],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            lines
                .iter()
                .any(|l| l.starts_with(&format!("# {stage}: unbound, "))),
            "{stage}: {lines:?}"
        );
    }
    assert!(lines.iter().all(|l| !l.contains(" = ")), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("# check: unbound, looked for mypy.ini")),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2426: each environment tool prefixes every
/// bound command, and with none declared the commands run bare with a
/// comment naming the consequence.
#[test]
fn each_tool_runs_through_the_environment_the_project_declares() {
    let ruff = "[project]\nname = \"x\"\n\n[tool.ruff]\nline-length = 100\n";
    for (lock, prefix) in [
        ("uv.lock", "uv run"),
        ("poetry.lock", "poetry run"),
        ("pdm.lock", "pdm run"),
    ] {
        let (dir, bin) = fixture("py-env", &[("pyproject.toml", ruff), (lock, "")], &[]);
        let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
        assert!(
            lines
                .iter()
                .any(|l| l.starts_with(&format!("lint = \"{prefix} ruff check "))),
            "{prefix}: {lines:?}"
        );
        let (_, status, _) = paw(&dir.0, &bin.0, &["python", "status"]);
        assert!(
            status
                .iter()
                .any(|l| l.starts_with("environment:") && l.ends_with(lock)),
            "{lock}: {status:?}"
        );
    }
    let (dir, bin) = fixture(
        "py-env-table",
        &[(
            "pyproject.toml",
            "[tool.poetry]\nname = \"x\"\n\n[tool.ruff]\nline-length = 1\n",
        )],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("lint = \"poetry run ruff check ")),
        "{lines:?}"
    );

    let (dir, bin) = fixture("py-env-none", &[("pyproject.toml", ruff)], &["ruff"]);
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines.iter().any(|l| l.starts_with("lint = \"ruff check ")),
        "{lines:?}"
    );
    assert!(
        lines.contains(
            &"# no environment declared: the interpreter that runs ruff is whatever the shell finds"
                .to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2426: two environment tools leave every stage
/// unresolved and name both files.
#[test]
fn two_environments_leave_the_stages_unresolved() {
    let (dir, bin) = fixture(
        "py-env-two",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            ("poetry.lock", ""),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    for stage in ["format", "lint", "check", "test", "build"] {
        assert!(
            lines.contains(&format!(
                "# {stage}: unresolved, poetry.lock and uv.lock both declare an environment"
            )),
            "{stage}: {lines:?}"
        );
    }
}

/// TSK-5085 criterion 3, REQ-2420: where two type checkers are configured the
/// first in the document binds and the other is named, and an installed one
/// binds nothing.
#[test]
fn the_configured_type_checker_binds_and_the_other_is_named() {
    let (dir, bin) = fixture(
        "py-checker",
        &[
            (
                "pyproject.toml",
                "[tool.pyright]\nstrict = [\"a\"]\n\n[tool.ty]\n",
            ),
            ("uv.lock", ""),
            ("mypy.ini", "[mypy]\n"),
        ],
        &["mypy", "pyright", "ty", "pyrefly"],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines.contains(&"check = \"uv run mypy --cache-dir=/dev/null\"".to_string()),
        "{lines:?}"
    );
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with('#') && l.contains("pyproject.toml") && l.contains("pyright")),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "py-ty",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            ("ty.toml", ""),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines.contains(&"check = \"uv run ty check\"".to_string()),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2422: `bind` selects no Ruff rule group of its
/// own and passes no fix flag.
#[test]
fn bind_turns_on_no_rule_group_and_applies_no_fix() {
    let (dir, bin) = fixture("py-ruff", &configured(), &[]);
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    for line in lines
        .iter()
        .filter(|l| l.starts_with("lint =") || l.starts_with("format ="))
    {
        for word in [
            "--select",
            "--extend-select",
            "--fix",
            "--unsafe-fixes",
            "--preview",
        ] {
            assert!(!line.contains(word), "{word} in {line}");
        }
    }
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with('#') && l.contains("security rules")),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2412: the test stage runs documentation tests
/// where the project's pytest configuration asks for them, and says it
/// doesn't where the configuration does not.
#[test]
fn the_test_stage_says_whether_it_runs_documentation_examples() {
    let (dir, bin) = fixture("py-doctest", &configured(), &[]);
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines
            .iter()
            .all(|l| !l.contains("doesn't run the examples")),
        "{lines:?}"
    );

    let (dir, bin) = fixture(
        "py-nodoctest",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            ("pytest.ini", "[pytest]\naddopts = -q\n"),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "bind"]);
    assert!(
        lines.contains(
            &"# the test stage doesn't run the examples in your documentation; add --doctest-modules to addopts if your docstrings hold examples"
                .to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2426: `check` finds a stage that runs a tool by
/// its bare name, `python -m` included, and accepts the same tool run
/// through the declared environment.
#[test]
fn check_finds_a_tool_run_outside_the_declared_environment() {
    let (dir, bin) = fixture(
        "py-outside",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[
                    ("check", "mypy --cache-dir=/dev/null ."),
                    ("test", "python -B -m pytest -p no:cacheprovider"),
                    ("lint", "uv run ruff check --cache-dir /tmp/c ."),
                ]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(&"check runs mypy outside uv: write uv run mypy".to_string()),
        "{lines:?}"
    );
    assert!(
        lines.contains(&"test runs pytest outside uv: write uv run pytest".to_string()),
        "{lines:?}"
    );
    assert!(!lines.iter().any(|l| l.starts_with("lint ")), "{lines:?}");
}

/// TSK-5085 criterion 3, REQ-2426: two environments are a finding.
#[test]
fn check_finds_two_environments() {
    let (dir, bin) = fixture(
        "py-two-env",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            ("pdm.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("lint", "uv run ruff check --cache-dir /tmp/c .")]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(&"pdm.lock and uv.lock both declare an environment".to_string()),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2434: a fix flag in a check stage is a finding.
#[test]
fn check_finds_ruff_applying_fixes() {
    let (dir, bin) = fixture(
        "py-fix",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[
                    (
                        "lint",
                        "uv run ruff check --fix --unsafe-fixes --cache-dir /tmp/c .",
                    ),
                    ("format", "uv run ruff format --cache-dir /tmp/c ."),
                ]),
            ),
        ],
        &[],
    );
    let (_, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    for expected in [
        "ruff would apply unsafe fixes: remove --unsafe-fixes",
        "ruff applies fixes in a check: remove --fix",
        "ruff format rewrites the tree: pass --check",
    ] {
        assert!(
            lines.contains(&expected.to_string()),
            "{expected}: {lines:?}"
        );
    }
}

/// TSK-5085 criterion 3, REQ-2442: a stage whose tool writes a cache into the
/// tree is a finding unless an ignore file the repository commits covers it,
/// and a stage that points the cache elsewhere is not.
#[test]
fn check_finds_a_tool_writing_its_cache_into_the_tree() {
    let stages = profile(&[
        ("lint", "uv run ruff check ."),
        ("check", "uv run mypy"),
        ("test", "uv run pytest"),
    ]);
    let (dir, bin) = fixture(
        "py-cache",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            (".meowpaw/profile.toml", &stages),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    for expected in [
        "ruff writes .ruff_cache into the tree: pass --cache-dir",
        "mypy writes .mypy_cache into the tree: pass --cache-dir=/dev/null",
        "pytest writes .pytest_cache into the tree: pass -p no:cacheprovider",
    ] {
        assert!(
            lines.contains(&expected.to_string()),
            "{expected}: {lines:?}"
        );
    }

    let (dir, bin) = fixture(
        "py-cache-ignored",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            (".gitignore", ".ruff_cache/\n.mypy_cache/\n.pytest_cache/\n"),
            (".meowpaw/profile.toml", &stages),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
}

/// TSK-5085 criterion 3, REQ-2434: two files configuring one tool are a
/// finding that names the one the tool reads.
#[test]
fn check_finds_two_files_configuring_one_tool() {
    let (dir, bin) = fixture(
        "py-two-config",
        &[
            ("pyproject.toml", "[tool.ruff]\nline-length = 88\n"),
            ("ruff.toml", "line-length = 100\n"),
            ("uv.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("lint", "uv run ruff check --cache-dir /tmp/c .")]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(1), "{lines:?}");
    assert!(
        lines.contains(
            &"pyproject.toml configures ruff and ruff.toml does too: ruff reads ruff.toml alone"
                .to_string()
        ),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2432: a clean `check` names what it covered, a
/// missing profile is unresolved, and an unknown argument is a usage error.
#[test]
fn a_clean_check_names_what_it_covered() {
    let (dir, bin) = fixture(
        "py-clean",
        &[
            ("pyproject.toml", PROJECT),
            ("uv.lock", ""),
            (
                ".meowpaw/profile.toml",
                &profile(&[("lint", "uv run ruff check --cache-dir /tmp/c .")]),
            ),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert!(
        lines.contains(
            &"no findings; rule groups enabled: the environment, the fixes, the caches, the configuration files"
                .to_string()
        ),
        "{lines:?}"
    );

    let (dir, bin) = fixture("py-noprofile", &[("pyproject.toml", PROJECT)], &[]);
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "check"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: no profile at")),
        "{lines:?}"
    );
    let (done, _, stderr) = paw(&dir.0, &bin.0, &["python", "bind", "a", "b"]);
    assert_eq!(done.status.code(), Some(2));
    assert!(stderr.starts_with("usage: meow-python"), "{stderr}");
}

/// TSK-5085 criterion 2: a `pyproject.toml` that doesn't parse is unresolved,
/// and `bind` takes a directory.
#[test]
fn a_broken_project_is_unresolved_and_bind_takes_a_directory() {
    let (dir, bin) = fixture(
        "py-dir",
        &[
            ("pyproject.toml", PROJECT),
            ("web/pyproject.toml", "[project\n"),
            ("api/pyproject.toml", "[tool.ruff]\nline-length = 1\n"),
            ("api/poetry.lock", ""),
        ],
        &[],
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "bind", "web"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: web/pyproject.toml doesn't parse as TOML:")),
        "{lines:?}"
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "bind", "api"]);
    assert_eq!(done.status.code(), Some(0), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("lint = \"poetry run ruff check ")),
        "{lines:?}"
    );
    let (done, lines, _) = paw(&dir.0, &bin.0, &["python", "bind", "docs"]);
    assert_eq!(done.status.code(), Some(3), "{lines:?}");
    assert!(
        lines
            .iter()
            .any(|l| l.starts_with("unresolved: docs holds no pyproject.toml; one is in ")),
        "{lines:?}"
    );
}

/// TSK-5085 criterion 3, REQ-2450: the page states which generated files to
/// commit and which to ignore, in both distributions.
#[test]
fn the_page_states_the_generated_files() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    for tree in ["plugins", "packages"] {
        let page = std::fs::read_to_string(root.join(tree).join("meow-python/README.md")).unwrap();
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
            section.contains("uv.lock") && section.contains(".venv"),
            "{section}"
        );
    }
}
