# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The method runs on a repository with only the kernel and the method units installed (TSK-5020, ADR-2640).

Each fixture builds an installation under a temporary directory from the units' own files: the kernel unit, the
method unit and the unit that runs the stages, and no pack. It runs the programs the steps call, `paw ready`,
`paw check` and `meow-checks status`, and compares them with the same run beside a pack, because the claim is that
a missing pack changes nothing. A run with a model is not driven here, so what a step's prose tells a model rests
on the last test, which reads the step files for a pack's command.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
PLUGINS = UNIT.parent
sys.path.insert(0, str(HERE))
from test_record import CLEAN  # noqa: E402

VERBS = ["format", "lint", "check", "test", "build"]
PROFILE = '[record]\nroot = "project"\n'
# The units a repository with no pack has: the kernel, the method and the unit that runs the stages.
INSTALLED = ("meow-core", "meow-flow", "meow-checks")


def install(target, units):
    """Copy each unit's files beside the others, as a checkout loaded in place has them, with the kernel's
    binary linked and not copied."""
    for name in units:
        source = PLUGINS / name
        shutil.copytree(source, target / name, symlinks=True,
                        ignore=shutil.ignore_patterns("tests", "evals", "__pycache__", "bin" if name == "meow-core" else ""))
    if "meow-core" in units:
        (target / "meow-core" / "bin").symlink_to(PLUGINS / "meow-core" / "bin")


class Installation:
    def __init__(self, units):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.plugins = self.base / "plugins"
        self.plugins.mkdir()
        install(self.plugins, units)
        self.repo = self.base / "repository"
        (self.repo / ".meowpaw").mkdir(parents=True)
        (self.repo / ".meowpaw" / "profile.toml").write_text(PROFILE, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        for name, text in CLEAN.items():
            path = self.repo / "project" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        # Nothing of the machine's own reaches the fixture: its home, its data and its state sit in the fixture.
        self.env = {**os.environ, "HOME": str(self.base / "home"), "CLAUDE_PLUGIN_DATA": str(self.base / "no-data"),
                    "XDG_STATE_HOME": str(self.base / "state"), "XDG_RUNTIME_DIR": str(self.base / "state"),
                    "XDG_CONFIG_HOME": str(self.base / "state"), "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.env.pop("MEOW_LAYOUT", None)

    def run(self, unit, program, *args):
        return subprocess.run([str(self.plugins / unit / "bin" / program), *args], cwd=self.repo,
                              capture_output=True, text=True, env=self.env)

    def paw(self, *args):
        return self.run("meow-flow", "paw", *args)

    def checks(self, *args):
        return self.run("meow-checks", "meow-checks", *args)


class NoPack(unittest.TestCase):
    def installation(self, units=INSTALLED):
        installation = Installation(units)
        self.addCleanup(installation.tmp.cleanup)
        return installation

    def test_the_fixture_has_no_pack_on_any_path_the_launchers_search(self):
        """TSK-5020: the fixture is the kernel and the method alone."""
        installation = self.installation()
        self.assertEqual(sorted(p.name for p in installation.plugins.iterdir()), sorted(INSTALLED))

    def test_every_verb_is_unresolved_with_its_kind_and_none_passes(self):
        """TSK-5020 criterion 1, REQ-0086, REQ-0088: no declared verb and no pack, so nothing is passed."""
        done = self.installation().checks("status", "--json")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        verbs = json.loads(done.stdout)["verbs"]
        self.assertEqual(sorted(verbs), sorted(VERBS))
        for verb, entry in verbs.items():
            self.assertEqual(entry["state"], "unresolved", verb)
            self.assertTrue(entry.get("kind"), verb)
        self.assertNotIn("passed", done.stdout)

    def test_the_ready_gates_answer_as_they_do_beside_every_pack(self):
        """TSK-5020 criterion 2, REQ-0088: `paw ready spec` and `paw ready epic` exit as they do with packs."""
        bare = self.installation()
        packed = self.installation(INSTALLED + ("meow-git", "meow-mise", "meow-rust"))
        for step, identifier in (("spec", "ADR-0001"), ("epic", "ADR-0001"), ("implement", "TSK-0001")):
            without, beside = bare.paw("ready", step, identifier), packed.paw("ready", step, identifier)
            self.assertEqual(without.returncode, beside.returncode, (step, without.stdout, beside.stdout))
            self.assertEqual(without.stdout, beside.stdout, step)
        self.assertEqual(bare.paw("ready", "spec", "ADR-0001").returncode, 0)
        self.assertEqual(bare.paw("ready", "epic", "ADR-0001").returncode, 0)

    def test_a_task_that_changes_only_a_specification_passes_the_same_gate(self):
        """TSK-5020 criterion 3, REQ-0080: the gate reads the task's record and not the kind of work it names."""
        results = []
        for work in ("Change `specs/SPC-0001-a-part.md` and nothing else.", "Change `src/lib` and its tests."):
            installation = self.installation()
            path = installation.repo / "project" / "tasks" / "TSK-0001-a-task.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "## What to do\n\nText.", f"## What to do\n\n{work}"), encoding="utf-8")
            ready = installation.paw("ready", "implement", "TSK-0001")
            check = installation.paw("check")
            self.assertEqual(ready.returncode, 0, ready.stdout + ready.stderr)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            results.append((ready.stdout, check.stdout))
        self.assertEqual(results[0], results[1])

    def test_no_step_file_requires_a_pack_command(self):
        """TSK-5020, REQ-0088: a skill item naming a pack's command says what happens where the command is absent."""
        pack = re.compile(r"\bmeow-(git|github|mise|gotask|markdown|rust|go|python|typescript|csharp|lua|godot"
                          r"|starlark|scheme)\b")
        optional = re.compile(r"exists?\b|doesn't exist|absent|isn't installed", re.IGNORECASE)
        found = []
        for tree in (UNIT, PLUGINS.parent / "packages" / "meow-flow"):
            for path in sorted((tree / "skills").rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                for item in re.split(r"\n\s*\n|\n(?=\s*(?:- [A-Z]\d+\.|\d+\. ))", text):
                    if pack.search(item) and not optional.search(item):
                        found.append(f"{path.relative_to(tree.parent.parent)}: {' '.join(item.split())[:80]}")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
