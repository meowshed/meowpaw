// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The GitHub request layer (ADR-1810). SPC-1080 states the behaviour.

/// The wait, in seconds from when the response arrived, that `header` holding
/// `value` gives under `service`'s table, measured against the response's
/// `Date`; `None` where the value doesn't parse in the table's unit.
#[allow(dead_code)]
pub(crate) fn wait(_service: &str, _header: &str, _value: &str, _date: &str) -> Option<u64> {
    None
}

#[cfg(test)]
mod tests {
    use super::wait;
    use std::path::Path;

    /// TSK-2940 criterion 4, REQ-2578: `x-ratelimit-reset` counts UTC epoch
    /// seconds, so the pair RES-0290 observed gives 3,207 seconds. Read as
    /// milliseconds it would give about 3.2 seconds, or a reset in 1970.
    #[test]
    fn reset_is_read_in_epoch_seconds() {
        let (reset, date) = (1_790_695_444_u64, "Tue, 29 Sep 2026 14:30:37 GMT");
        assert_eq!(
            wait("github", "x-ratelimit-reset", &reset.to_string(), date),
            Some(3_207)
        );
        assert_eq!(
            wait("github", "X-Ratelimit-Reset", &reset.to_string(), date),
            Some(3_207),
            "header names compare without regard to case"
        );
        assert_eq!((reset - 1_790_692_237) / 1000, 3);
        assert!(reset / 1000 < 31_536_000, "as milliseconds it lies in 1970");
    }

    /// TSK-2940 criterion 8, REQ-2566: only `github/request.rs` starts `gh` in
    /// the `github` feature, so no call escapes the layer's reading of limits.
    #[test]
    fn only_the_layer_starts_gh() {
        let src = Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
        let mut files = vec![src.join("github.rs")];
        for entry in std::fs::read_dir(src.join("github")).expect("src/github reads") {
            let path = entry.expect("an entry reads").path();
            if path.extension().is_some_and(|e| e == "rs") {
                files.push(path);
            }
        }
        let starts = concat!("Command::", "new(");
        let mut starting = Vec::new();
        for file in &files {
            let text = std::fs::read_to_string(file).expect("a source file reads");
            let gh = text.match_indices(starts).any(|(at, _)| {
                let argument = text[at + starts.len()..].trim_start();
                argument.starts_with("\"gh\"") || !argument.starts_with('"')
            });
            if gh {
                starting.push(file.strip_prefix(&src).unwrap().display().to_string());
            }
        }
        starting.sort();
        assert_eq!(starting, vec!["github/request.rs".to_string()]);
    }
}
