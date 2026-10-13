// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! Whether a person attends the session a hook runs in, and the answer that
//! asks them about one irreversible action (ADR-2750, REQ-1420, REQ-1422).
//!
//! A session in `dontAsk` has nobody to answer a prompt, and a session a
//! `meow-loop` run holds decides its gates by the authority ADR-2380 declares
//! before the run starts, so neither is attended. Every other session is.

use serde_json::{Value, json};

/// Whether a person attends the session `event` comes from.
pub fn attended(event: &Value) -> bool {
    if event.get("permission_mode").and_then(Value::as_str) == Some("dontAsk") {
        return false;
    }
    #[cfg(feature = "loop")]
    if crate::runloop::run_is_active(event) {
        return false;
    }
    true
}

/// Prints the `PreToolUse` answer that asks the person about this one
/// invocation, with `reason`. The answer grants nothing beyond the call, so
/// approving it approves no later one.
pub fn ask(reason: &str) {
    let answer = json!({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    });
    println!("{answer}");
}
