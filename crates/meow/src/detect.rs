// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! How a pack detects its toolchain: by a marker file git tracks, once for
//! each directory holding one, starting none of the toolchain's tools
//! (SPC-1190 "Detection", REQ-0133, REQ-3048).
//!
//! A pack implements one function, `markers(&BTreeSet<String>) -> Vec<Marker>`,
//! over the paths git tracks, relative to the root. Its `status` prints, for
//! each directory, the [`scope`] line and one `marker:` line a marker, and
//! [`PACKS`] lists it, so `meow-checks doctor` reports its detection without
//! running it (REQ-3090).

#![allow(dead_code)]

use crate::profile::{self, Part, Profile};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

/// One marker file a pack matched, and the directory it activates for.
#[derive(Clone, Debug, PartialEq)]
pub struct Marker {
    /// The file, relative to the repository's root, or a description where
    /// the marker is a count of files rather than one file.
    pub file: String,
    /// The directory, relative to the root, and `.` for the root itself.
    pub directory: String,
}

/// A pack the binary carries: its unit's name and how it detects its marker.
pub struct Pack {
    pub unit: &'static str,
    pub markers: fn(&BTreeSet<String>) -> Vec<Marker>,
}

/// Every pack this build carries, in the order `doctor` reports them.
pub const PACKS: &[Pack] = &[
    #[cfg(feature = "markdown")]
    Pack {
        unit: "meow-markdown",
        markers: crate::markdown::markers,
    },
    #[cfg(feature = "go")]
    Pack {
        unit: "meow-go",
        markers: crate::go::markers,
    },
    #[cfg(feature = "rust")]
    Pack {
        unit: "meow-rust",
        markers: crate::rust::markers,
    },
    #[cfg(feature = "mise")]
    Pack {
        unit: "meow-mise",
        markers: crate::mise::markers,
    },
    #[cfg(feature = "gotask")]
    Pack {
        unit: "meow-gotask",
        markers: crate::gotask::markers,
    },
];

/// The paths git tracks under `root`, relative to it.
pub fn tracked(root: &Path) -> BTreeSet<String> {
    let mut found = BTreeSet::new();
    if let Ok(done) = profile::reading_git()
        .args(["ls-files", "-z"])
        .current_dir(root)
        .output()
    {
        for path in done.stdout.split(|b| *b == 0).filter(|p| !p.is_empty()) {
            found.insert(String::from_utf8_lossy(path).into_owned());
        }
    }
    found
}

/// The directory a tracked path sits in, `.` for the root.
pub fn directory_of(path: &str) -> String {
    match path.rsplit_once('/') {
        Some((directory, _)) => directory.to_string(),
        None => ".".to_string(),
    }
}

/// Each tracked file whose name is one of `names`, wherever it lies: the
/// marker of a pack whose toolchain is named by one file, such as a manifest.
pub fn by_name(tracked: &BTreeSet<String>, names: &[&str]) -> Vec<Marker> {
    tracked
        .iter()
        .filter(|path| names.contains(&path.rsplit('/').next().unwrap_or(path)))
        .map(|path| Marker {
            file: path.clone(),
            directory: directory_of(path),
        })
        .collect()
}

/// The markers grouped by their directory, in the directories' order.
pub fn by_directory(markers: &[Marker]) -> BTreeMap<String, Vec<String>> {
    let mut grouped: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for marker in markers {
        grouped
            .entry(marker.directory.clone())
            .or_default()
            .push(marker.file.clone());
    }
    grouped
}

/// The parts the root profile declares, or none.
pub fn parts(root: &Path) -> Vec<Part> {
    match profile::read(root) {
        Profile::Parsed(table, _) => profile::parts(&table).0,
        _ => Vec::new(),
    }
}

/// The line a pack's report opens each directory with: `scope: <part>
/// <directory>` where a declared part holds the directory, and
/// `scope: <directory>` where none does (REQ-3043, REQ-3048).
pub fn scope(parts: &[Part], directory: &str) -> String {
    let holding = parts
        .iter()
        .filter(|part| directory != "." && Path::new(directory).starts_with(&part.directory))
        .max_by_key(|part| part.directory.len());
    match holding {
        Some(part) => format!("scope: {} {directory}", part.name),
        None => format!("scope: {directory}"),
    }
}

/// Where the platform keeps its configuration: `CLAUDE_CONFIG_DIR`, or
/// `~/.claude`.
fn platform_dir() -> Option<PathBuf> {
    if let Some(dir) = std::env::var_os("CLAUDE_CONFIG_DIR").filter(|v| !v.is_empty()) {
        return Some(PathBuf::from(dir));
    }
    let home = std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE"))?;
    Some(PathBuf::from(home).join(".claude"))
}

/// A unit's launcher, where the unit is installed: beside the core unit in a
/// checkout loaded in place, or in the platform's plugin cache. A pack that
/// isn't installed can't report its marker (ADR-2680).
pub fn installed(unit: &str) -> Option<PathBuf> {
    // The binary sits at <core>/bin/<target>/paw, and a checkout holds every
    // unit beside the core one.
    let beside = std::env::current_exe()
        .ok()
        .and_then(|exe| exe.canonicalize().ok())
        .and_then(|exe| Some(exe.parent()?.parent()?.parent()?.parent()?.to_path_buf()))
        .map(|units| units.join(unit).join("bin").join(unit));
    if let Some(launcher) = beside.filter(|l| l.is_file()) {
        return Some(launcher);
    }
    let cache = platform_dir()?.join("plugins").join("cache");
    let mut found: Vec<(Vec<u64>, PathBuf)> = Vec::new();
    for marketplace in std::fs::read_dir(&cache).ok()?.flatten() {
        let Ok(versions) = std::fs::read_dir(marketplace.path().join(unit)) else {
            continue;
        };
        for version in versions.flatten() {
            let launcher = version.path().join("bin").join(unit);
            if launcher.is_file() {
                let name = version.file_name().to_string_lossy().into_owned();
                let key = name
                    .split(|c: char| !c.is_ascii_digit())
                    .filter_map(|n| n.parse().ok())
                    .collect();
                found.push((key, launcher));
            }
        }
    }
    found.sort();
    found.pop().map(|(_, launcher)| launcher)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tracked(paths: &[&str]) -> BTreeSet<String> {
        paths.iter().map(|p| p.to_string()).collect()
    }

    /// REQ-0133: a marker names the directory it sits in, and the root is `.`.
    #[test]
    fn a_marker_names_its_directory() {
        let found = by_name(
            &tracked(&["Cargo.toml", "crates/x/Cargo.toml", "crates/x/src/main.rs"]),
            &["Cargo.toml"],
        );
        assert_eq!(
            found,
            [
                Marker {
                    file: "Cargo.toml".into(),
                    directory: ".".into()
                },
                Marker {
                    file: "crates/x/Cargo.toml".into(),
                    directory: "crates/x".into()
                },
            ]
        );
    }

    /// REQ-3043, REQ-3048: the scope names the part holding the directory,
    /// and the directory alone where no part holds it.
    #[test]
    fn the_scope_names_the_part_holding_the_directory() {
        let parts = [
            Part {
                name: "site".into(),
                directory: "site".into(),
            },
            Part {
                name: "docs".into(),
                directory: "site/docs".into(),
            },
        ];
        assert_eq!(scope(&parts, "site"), "scope: site site");
        assert_eq!(scope(&parts, "site/docs/a"), "scope: docs site/docs/a");
        assert_eq!(scope(&parts, "sitemap"), "scope: sitemap");
        assert_eq!(scope(&parts, "."), "scope: .");
    }
}
