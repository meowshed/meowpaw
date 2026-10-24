// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `paw check` and `paw status --brief` answer within a second on a record of
//! about 2,200 artifacts that nothing has changed since the last call
//! (TSK-5682, REQ-2800).

#![cfg(feature = "record")]

use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{Duration, Instant};

/// A scratch directory of its own, removed when the test ends.
struct Dir(PathBuf);

impl Drop for Dir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn write(root: &Path, name: &str, text: &str) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// 40 decisions, each with an epic of 25 tasks, and 1,000 requirements the
/// tasks close, 2,080 artifacts in all.
fn large_record() -> Dir {
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let dir = Dir(std::env::temp_dir().join(format!("meow-speed-{}-{stamp}", std::process::id())));
    std::fs::create_dir_all(&dir.0).unwrap();
    write(
        &dir.0,
        ".meowpaw/profile.toml",
        "[record]\nroot = \"project\"\n",
    );
    let project = dir.0.join("project");
    write(&project, "README.md", "# Index\n");
    write(
        &project,
        "research/RES-0001-synthesis.md",
        "---\nid: RES-0001\nartifact: research\nstatus: approved\nrevised: 2026-01-01\n---\n\n# Research\n",
    );
    for kind in ["adrs", "requirements", "epics", "tasks"] {
        write(&project, &format!("{kind}/README.md"), "# Index\n");
    }
    for r in 0..1000 {
        write(
            &project,
            &format!("requirements/REQ-{:04}-need-{r}.md", 1000 + r),
            &format!(
                "---\nid: REQ-{n:04}\nartifact: requirement\ntopic: speed\nclass: functional\nstatus: approved\nrevised: 2026-01-01\nelaborates: RES-0001\nverification: behavioural\n---\n\n# REQ-{n:04}\n\nThe tool MUST do thing {r}.\n",
                n = 1000 + r
            ),
        );
    }
    for d in 0..40 {
        let adr = 2000 + d;
        let epic = 3000 + d;
        let requirements: Vec<String> = (0..25)
            .map(|t| format!("REQ-{}", 1000 + d * 25 + t))
            .collect();
        write(
            &project,
            &format!("adrs/ADR-{adr}-decision-{d}.md"),
            &format!(
                "---\nid: ADR-{adr}\nartifact: adr\nstatus: approved\nrevised: 2026-01-01\naddresses: [{}]\nsupersedes: []\n---\n\n# {adr}. Decision {d}\n\n## Decision\n\nDo it.\n",
                requirements.join(", ")
            ),
        );
        let mut entries = String::new();
        for (t, requirement) in requirements.iter().enumerate() {
            let task = 5000 + d * 25 + t;
            entries.push_str(&format!(
                "- T-{:03} TSK-{task} do it\n      closes: {}\n\n",
                t + 1,
                requirement
            ));
            write(
                &project,
                &format!("tasks/TSK-{task}-task-{task}.md"),
                &format!(
                    "---\nid: TSK-{task}\nartifact: task\nstatus: approved\nrevised: 2026-01-01\nepic: EPC-{epic}\ncloses: [{}]\nissue:\n---\n\n# Task {task}\n\n## Evidence\n\nNot yet.\n",
                    requirement
                ),
            );
        }
        write(
            &project,
            &format!("epics/EPC-{epic}-epic-{d}.md"),
            &format!(
                "---\nid: EPC-{epic}\nartifact: epic\nstatus: approved\nrevised: 2026-01-01\nrealises: ADR-{adr}\n---\n\n# Epic {d}\n\n## Tasks\n\n{entries}"
            ),
        );
    }
    dir
}

/// The release build of the tool that `mise run build` places in the core
/// unit, because the second a person waits is the second of that build and not
/// of an unoptimised test build.
fn release_binary() -> PathBuf {
    let system = match std::env::consts::OS {
        "macos" => "apple-darwin",
        "windows" => "pc-windows-msvc",
        _ => "unknown-linux-musl",
    };
    let cpu = match std::env::consts::ARCH {
        "aarch64" => "aarch64",
        _ => "x86_64",
    };
    let exe = if cfg!(windows) { "paw.exe" } else { "paw" };
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../plugins/meow-core/bin")
        .join(format!("{cpu}-{system}"))
        .join(exe);
    assert!(
        path.is_file(),
        "no release build at {}; run mise run build first",
        path.display()
    );
    path
}

fn paw(dir: &Path, args: &[&str]) -> (Output, Duration) {
    let layout =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../plugins/meow-flow/lib/layout.toml");
    let started = Instant::now();
    let output = Command::new(release_binary())
        .arg("record")
        .args(args)
        .current_dir(dir)
        .env("MEOW_LAYOUT", layout)
        .env("GIT_CONFIG_GLOBAL", "/dev/null")
        .env("GIT_CONFIG_NOSYSTEM", "1")
        .output()
        .unwrap();
    (output, started.elapsed())
}

/// Criterion 1 (REQ-2800): the second call, with no file changed, completes in
/// under a second. The best of three keeps one busy moment of the machine from
/// failing a call that is fast.
#[test]
fn a_second_call_on_an_unchanged_record_takes_under_a_second() {
    let dir = large_record();
    for args in [&["check"][..], &["status", "--brief"][..]] {
        let (first, _) = paw(&dir.0, args);
        let best = (0..3)
            .map(|_| paw(&dir.0, args))
            .map(|(second, took)| {
                assert_eq!(
                    first.stdout, second.stdout,
                    "the second call reports what the first did"
                );
                took
            })
            .min()
            .unwrap();
        assert!(
            best < Duration::from_secs(1),
            "paw {args:?} took {best:?} on 2,080 artifacts"
        );
    }
}
