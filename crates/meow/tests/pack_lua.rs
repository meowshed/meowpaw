// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! `meow-lua` on fixture repositories (TSK-5100, SPC-1370).

#![cfg(feature = "lua")]

mod langpack_fixture;

use langpack_fixture::{PROFILE, Repo};

const ROCKSPEC: &str = "package = \"shop\"\nversion = \"1.0-1\"\nsource = { url = \"git+https://example.org/shop\" }\nbuild = { type = \"builtin\", modules = { shop = \"src/shop.lua\" } }\n";
const LUARC: &str = "{\n  // the runtime the code runs on\n  \"runtime.version\": \"Lua 5.4\"\n}\n";

/// A Lua library with its runtime, formatter, linter and tests configured.
fn library(name: &str) -> Repo {
    Repo::new(
        name,
        &[
            PROFILE,
            ("shop-1.0-1.rockspec", ROCKSPEC),
            (".luarc.json", LUARC),
            ("stylua.toml", "column_width = 100\n"),
            ("selene.toml", "std = \"lua54\"\n"),
            (".busted", "return { default = { ROOT = { \"spec\" } } }\n"),
            ("src/shop.lua", "return {}\n"),
        ],
    )
}

/// A Neovim plugin laid out for the editor.
fn plugin(name: &str, extra: &[(&str, &str)]) -> Repo {
    let mut files = vec![
        PROFILE,
        ("lua/shop/init.lua", "return {}\n"),
        ("plugin/shop.lua", "require('shop')\n"),
        ("doc/shop.txt", "*shop.txt*\n"),
        (
            ".luarc.json",
            "{ \"runtime\": { \"version\": \"LuaJIT\" } }\n",
        ),
    ];
    files.extend_from_slice(extra);
    Repo::new(name, &files)
}

#[test]
fn status_reports_for_the_directory_holding_the_marker() {
    // TSK-5100 criterion 1, REQ-2342, REQ-3048: a .luarc.json in a
    // subdirectory is reported for that directory, naming the marker.
    let repo = Repo::new(
        "lua-sub",
        &[PROFILE, ("tools/.luarc.json", LUARC), ("tools/a.lua", "\n")],
    );
    let run = repo.run(&["lua", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    let lines = run.lines();
    assert!(lines.iter().any(|l| l == "scope: tools"), "{}", run.out());
    assert!(
        lines.iter().any(|l| l == "marker: tools/.luarc.json"),
        "{}",
        run.out()
    );
    assert!(
        run.out().contains("host: Lua 5.4, from tools/.luarc.json"),
        "{}",
        run.out()
    );
    assert!(!lines.iter().any(|l| l == "scope: ."), "{}", run.out());
}

#[test]
fn a_neovim_plugin_is_detected_from_its_layout() {
    // TSK-5100 criterion 1, REQ-2344: lua/ beside plugin/ marks a Neovim
    // plugin, reported for its directory with Neovim as the host.
    let repo = Repo::new(
        "lua-nvim-sub",
        &[
            PROFILE,
            ("nvim/lua/shop/init.lua", "return {}\n"),
            ("nvim/plugin/shop.lua", "\n"),
        ],
    );
    let run = repo.run(&["lua", "status"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    let lines = run.lines();
    assert!(lines.iter().any(|l| l == "scope: nvim"), "{}", run.out());
    assert!(
        lines.iter().any(|l| l == "marker: nvim/lua/, nvim/plugin/"),
        "{}",
        run.out()
    );
    assert!(run.out().contains("host: Neovim"), "{}", run.out());
}

#[test]
fn a_work_tree_with_no_marker_is_not_a_lua_repository() {
    // TSK-5100 criterion 1, REQ-2342, REQ-2344: with no marker every command
    // prints the unresolved line and exits 3, and a lone lua/ isn't a plugin.
    let repo = Repo::new(
        "lua-none",
        &[PROFILE, ("lua/a.lua", "\n"), ("README.md", "# x\n")],
    );
    for command in ["status", "bind", "check"] {
        let run = repo.run(&["lua", command], &[]);
        assert_eq!(run.code(), 3, "{command}: {}", run.out());
        assert!(
            run.out()
                .contains("unresolved: not a Lua and Neovim plugins repository"),
            "{command}: {}",
            run.out()
        );
    }
}

#[test]
fn bind_prints_every_stage_for_a_library() {
    // TSK-5100 criterion 2, REQ-2342: every stage is bound from what the
    // library commits, or printed with its reason.
    let repo = library("lua-bind");
    let run = repo.run(&["lua", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(run.bound("format").as_deref(), Some("stylua --check ."));
    assert_eq!(run.bound("lint").as_deref(), Some("selene ."));
    assert_eq!(run.bound("test").as_deref(), Some("busted"));
    assert_eq!(
        run.bound("build").as_deref(),
        Some("luarocks make shop-1.0-1.rockspec")
    );
    assert!(
        run.stage("check")[0].contains("lua-language-server"),
        "{}",
        run.out()
    );
}

#[test]
fn bind_prints_every_stage_for_a_neovim_plugin() {
    // TSK-5100 criterion 2, REQ-2344: a plugin's tests run inside the editor,
    // so test names the harness question, and the plugin has no build.
    let repo = plugin("lua-nvim-bind", &[("stylua.toml", "\n")]);
    let run = repo.run(&["lua", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    run.every_stage_printed();
    assert_eq!(run.bound("format").as_deref(), Some("stylua --check ."));
    assert!(
        run.stage("test")[0].contains("nvim --headless"),
        "{}",
        run.out()
    );
    assert!(
        run.stage("build")[0].starts_with("# build: unresolved, "),
        "{}",
        run.out()
    );
}

#[test]
fn the_runtime_is_detected_before_any_stage_binds() {
    // TSK-5100 criterion 3, REQ-2446: a rockspec with no runtime declared
    // leaves every stage unresolved, and declaring one binds them.
    let repo = Repo::new(
        "lua-host",
        &[
            PROFILE,
            ("shop-1.0-1.rockspec", ROCKSPEC),
            ("selene.toml", "\n"),
        ],
    );
    let run = repo.run(&["lua", "bind"], &[]);
    assert_eq!(run.code(), 3, "{}", run.out());
    for stage in ["format", "lint", "check", "test", "build"] {
        let lines = run.stage(stage);
        assert!(
            lines.len() == 1
                && lines[0]
                    .starts_with(&format!("# {stage}: unresolved, Lua runtime not detected")),
            "{stage}: {}",
            run.out()
        );
    }
    let status = repo.run(&["lua", "status"], &[]);
    assert_eq!(status.code(), 3, "{}", status.out());
    assert!(
        status
            .out()
            .contains("unresolved: Lua runtime not detected"),
        "{}",
        status.out()
    );
    repo.write(
        ".meowpaw/profile.toml",
        "[stages]\n\n[lua]\nruntime = \"LuaJIT\"\n",
    );
    let run = repo.run(&["lua", "bind"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
    assert_eq!(run.bound("lint").as_deref(), Some("selene ."));
}

#[test]
fn the_linter_the_repository_configured_is_the_one_bound() {
    // TSK-5100 criterion 3, REQ-2420: selene and luacheck serve one stage,
    // and the pack binds the one configured and never the other.
    let selene = library("lua-selene");
    let run = selene.run(&["lua", "bind"], &[]);
    assert!(!run.out().contains("luacheck ."), "{}", run.out());
    let luacheck = Repo::new(
        "lua-luacheck",
        &[
            PROFILE,
            (".luarc.json", LUARC),
            (".luacheckrc", "std = \"lua54\"\n"),
        ],
    );
    let run = luacheck.run(&["lua", "bind"], &[]);
    assert_eq!(run.bound("lint").as_deref(), Some("luacheck ."));
    assert!(!run.out().contains("selene ."), "{}", run.out());
    let neither = Repo::new("lua-neither", &[PROFILE, (".luarc.json", LUARC)]);
    let run = neither.run(&["lua", "bind"], &[]);
    assert!(run.bound("lint").is_none(), "{}", run.out());
    assert!(
        run.stage("lint")[0].starts_with("# lint: unbound, "),
        "{}",
        run.out()
    );
}

#[test]
fn check_reports_what_a_plugin_lacks() {
    // TSK-5100, REQ-2344 as SPC-1370 states it: a plugin with no
    // .luarc.json and no doc/ gets a finding for each.
    let repo = Repo::new(
        "lua-nvim-check",
        &[
            PROFILE,
            ("lua/shop/init.lua", "return {}\n"),
            ("plugin/shop.lua", "\n"),
        ],
    );
    let run = repo.run(&["lua", "check"], &[]);
    assert_eq!(run.code(), 1, "{}", run.out());
    assert!(run.out().contains(".: no .luarc.json"), "{}", run.out());
    assert!(run.out().contains(".: no doc/"), "{}", run.out());
    let clean = plugin("lua-nvim-clean", &[]);
    let run = clean.run(&["lua", "check"], &[]);
    assert_eq!(run.code(), 0, "{}", run.out());
}

#[test]
fn the_pack_leaves_the_tree_as_it_found_it() {
    // REQ-2442 as SPC-1190 states it: status, bind and check write nothing.
    let repo = library("lua-writes");
    let before = repo.files();
    for command in ["status", "bind", "check"] {
        repo.run(&["lua", command], &[]);
    }
    assert_eq!(repo.files(), before);
}
