# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit's launcher and Pi extension equal what its generator writes (TSK-5683, REQ-4624)."""

import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_launchers as gen  # noqa: E402

ROOT = gen.ROOT


class Generated(unittest.TestCase):
    def scratch(self):
        """A scratch root holding what the generator writes."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for path, text in gen.expected(root).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def test_committed_files_equal_the_generator(self):
        """TSK-5683 criterion 1, REQ-4624: no committed launcher or extension differs from what is written."""
        self.assertEqual([], [str(p.relative_to(ROOT)) for p in gen.differing()])

    def test_an_edited_launcher_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: the check names the unit whose launcher was edited and no other."""
        root = self.scratch()
        edited = root / "plugins" / "meow-go" / "bin" / "meow-go"
        edited.write_text(edited.read_text(encoding="utf-8") + "# hand-written\n", encoding="utf-8")
        self.assertEqual([edited], gen.differing(root))

    def test_an_edited_extension_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: the check names a Pi extension that was edited."""
        root = self.scratch()
        edited = root / "packages" / "meow-lua" / "extensions" / "bin.ts"
        edited.write_text("// edited\n", encoding="utf-8")
        self.assertEqual([edited], gen.differing(root))

    def test_a_missing_file_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: a launcher that was deleted differs."""
        root = self.scratch()
        gone = root / "packages" / "meow-scm" / "bin" / "meow-scm"
        gone.unlink()
        self.assertEqual([gone], gen.differing(root))

    def test_every_launcher_and_launcher_only_extension_is_declared(self):
        """TSK-5683 criterion 1, REQ-4624: a hand-written launcher no fact table declares cannot hide."""
        written = set(gen.expected())
        found = set()
        for tree in ("plugins", "packages"):
            for launcher in (ROOT / tree).glob("*/bin/*"):
                if launcher.is_file():
                    found.add(launcher)
        found |= set((ROOT / "packages").glob("*/extensions/bin.ts"))
        self.assertEqual([], sorted(str(p.relative_to(ROOT)) for p in found - written))

    def test_the_launcher_of_one_unit_is_unchanged_by_the_template(self):
        """TSK-5683 criterion 4, REQ-4624: the generated launcher of meow-go keeps the guard a missing binary hits."""
        text = gen.expected()[ROOT / "plugins" / "meow-go" / "bin" / "meow-go"]
        self.assertIn('exec "$binary" go "$@"', text)
        self.assertIn("status | bind | check | toolchain)", text)


class CheckoutBuild(unittest.TestCase):
    """BUG-1700: a launcher in a checkout runs that checkout's build, so nothing has to pin the data directory."""

    def fake_paw(self, directory, says):
        target = subprocess.run(["uname", "-m"], capture_output=True, text=True).stdout.strip().replace("arm64", "aarch64")
        system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}[os.uname().sysname]
        binary = directory / "bin" / f"{target}-{system}" / "paw"
        binary.parent.mkdir(parents=True)
        binary.write_text(f"#!/bin/sh\necho {says}\n", encoding="utf-8")
        binary.chmod(0o755)

    def test_the_build_beside_the_launcher_wins_over_an_installed_core(self):
        """REQ-2928: with a release installed, a launcher in a checkout still measures the checkout."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launcher = root / "plugins" / "meow-git" / "bin" / "meow-git"
            launcher.parent.mkdir(parents=True)
            launcher.write_text(gen.expected()[ROOT / "plugins" / "meow-git" / "bin" / "meow-git"], encoding="utf-8")
            self.fake_paw(root / "plugins" / "meow-core", "checkout")
            self.fake_paw(root / "installed", "installed")
            core_data = root / "data" / "meow-core-meowpaw"
            core_data.mkdir(parents=True)
            (core_data / "meow-root").write_text(str(root / "installed"), encoding="utf-8")
            env = {**os.environ, "CLAUDE_PLUGIN_DATA": str(root / "data" / "meow-git-meowpaw"), "HOME": tmp}
            done = subprocess.run(["sh", str(launcher), "commit-guard"], capture_output=True, text=True, env=env, cwd=root)
        self.assertEqual("checkout\n", done.stdout, done.stderr)

    def test_the_repository_sets_no_data_directory_for_every_process(self):
        """REQ-4504: a pin under `[env]` reaches a mise-activated shell and hides the installed core's data directory."""
        config = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))
        self.assertNotIn("CLAUDE_PLUGIN_DATA", config.get("env", {}))


class Denial(unittest.TestCase):
    """TSK-5700, REQ-5200, ADR-3080: the unresolved-binary message names the cause."""

    def scratch_launcher(self, unit="meow-git"):
        """A scratch copy of `unit`'s generated launcher, with a sibling meow-core whose
        `bin/` the caller populates, and a `meow-root` pointer to it."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        launcher = root / "plugins" / unit / "bin" / unit
        launcher.parent.mkdir(parents=True)
        launcher.write_text(gen.expected()[ROOT / "plugins" / unit / "bin" / unit], encoding="utf-8")
        launcher.chmod(0o755)
        core_root = root / "plugins" / "meow-core"
        core_root.mkdir(parents=True)
        core_data = root / "data" / "meow-core-meowpaw"
        core_data.mkdir(parents=True)
        (core_data / "meow-root").write_text(str(core_root), encoding="utf-8")
        return root, launcher, core_root

    def run_launcher(self, root, launcher, *args):
        data = root / "data" / f"{launcher.parent.parent.name}-meowpaw"
        env = {**os.environ, "CLAUDE_PLUGIN_DATA": str(data), "HOME": str(root)}
        return subprocess.run(["sh", str(launcher), *args], capture_output=True, text=True, env=env, cwd=root)

    def test_meow_core_with_no_target_at_all_names_the_github_cause_and_the_address(self):
        """TSK-5700 criterion 1: meow-core's own bin/ carries no <cpu>-<system>/ directory for any platform."""
        root, launcher, core_root = self.scratch_launcher()
        done = self.run_launcher(root, launcher, "commit-guard")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("a marketplace added with source github ships none", done.stderr)
        self.assertIn("meow.retran.me", done.stderr)
        self.assertNotIn("claude plugin install meow-core@meowpaw", done.stderr)

    def test_meow_core_with_another_target_names_the_install_command_unchanged(self):
        """TSK-5700 criterion 2: meow-core's bin/ carries another platform's target, not this machine's."""
        root, launcher, core_root = self.scratch_launcher()
        (core_root / "bin" / "x86_64-pc-windows-msvc").mkdir(parents=True)
        done = self.run_launcher(root, launcher, "commit-guard")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("claude plugin install meow-core@meowpaw", done.stderr)
        self.assertNotIn("meow.retran.me", done.stderr)

    def test_no_meow_core_installed_at_all_names_the_install_command_unchanged(self):
        """TSK-5700 criterion 2: no meow-root pointer at all reads as meow-core simply not installed."""
        root, launcher, core_root = self.scratch_launcher()
        (root / "data" / "meow-core-meowpaw" / "meow-root").unlink()
        done = self.run_launcher(root, launcher, "commit-guard")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("claude plugin install meow-core@meowpaw", done.stderr)
        self.assertNotIn("meow.retran.me", done.stderr)


class Unresolved(unittest.TestCase):
    """BUG-1710, REQ-4506: with no binary, a meow-github command reports itself unresolved and not as misused."""

    def test_each_command_exits_3_naming_the_core_unit(self):
        for tree, reason in (("plugins", "install meow-core"), ("packages", "reinstall the unit")):
            for command in ("project", "sync", "upgrade"):
                with self.subTest(tree=tree, command=command), tempfile.TemporaryDirectory() as tmp:
                    launcher = Path(tmp) / "meow-github"
                    launcher.write_text(gen.expected()[ROOT / tree / "meow-github" / "bin" / "meow-github"], encoding="utf-8")
                    env = {**os.environ, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit", "HOME": tmp}
                    env.pop("MEOWPAW_BINARY", None)
                    done = subprocess.run(["sh", str(launcher), command, "--check"], capture_output=True, text=True, env=env)
                    self.assertEqual(3, done.returncode, done.stdout + done.stderr)
                    self.assertIn(f"meow-github {command}: unresolved", done.stdout)
                    self.assertIn(reason, done.stdout)


if __name__ == "__main__":
    unittest.main()
