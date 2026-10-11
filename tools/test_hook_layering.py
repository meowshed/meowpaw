# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Each hook that stops a call names the gate check that holds its rule and the skill that says why, and a hook
that crashes or times out abstains (TSK-4905, SPC-1240 "How a rule is layered" and "How a hook answers").

A rule held three times is held by a hook, by a check in the gate and by an instruction (REQ-2710). Where a rule
has no gate check or no skill today, its sentence names the defect that records the gap (REQ-2712).
"""

import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"

# Each hook that stops a call, from SPC-1240's table: the unit and the subcommand.
BLOCKING = [
    ("meow-git", "commit-guard"),
    ("meow-git", "push-guard"),
    ("meow-github", "governance-guard"),
    ("meow-loop", "guard"),
    ("meow-loop", "stop"),
    ("meow-prose-gate", "check"),
]


def readme_sentence(unit, subcommand):
    """The sentence under the unit's `## Hooks` that names `subcommand` in code font."""
    text = (PLUGINS / unit / "README.md").read_text(encoding="utf-8")
    section = re.search(r"^## Hooks\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert section, f"{unit}: README has no ## Hooks section"
    flat = " ".join(section.group(1).split())
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z`])", flat):
        if any(subcommand in span.split() for span in sentence.split("`")[1::2]):
            return sentence
    raise AssertionError(f"{unit}: no sentence under ## Hooks names `{subcommand}`")


def gate_checks():
    """The names a sentence may give for a check: mise tasks and the CI workflow's jobs."""
    mise = (ROOT / "mise.toml").read_text(encoding="utf-8")
    tasks = set(re.findall(r"^\[tasks\.([A-Za-z0-9_-]+)\]", mise, re.M))
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    jobs = set(re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", ci, re.M))
    return tasks, jobs


def skills():
    """Every skill in the repository, as `unit:skill`."""
    return {f"{path.parts[-4]}:{path.parts[-2]}" for path in PLUGINS.glob("*/skills/*/SKILL.md")}


def defects():
    return {path.name.split("-")[0] + "-" + path.name.split("-")[1] for path in (ROOT / "project" / "bugs").glob("BUG-*.md")}


class Layering(unittest.TestCase):
    def test_each_blocking_hook_names_an_existing_check_and_skill_or_says_there_is_none(self):
        """TSK-4905 criteria 1 and 2, REQ-2710, REQ-2712. A shipped page cites no record, so a hook without a
        check says so in plain words, and a defect in the record names the hook and the missing check."""
        tasks, jobs = gate_checks()
        known_skills = skills()
        for unit, subcommand in BLOCKING:
            sentence = readme_sentence(unit, subcommand)
            where = f"{unit} `{subcommand}`"
            self.assertNotRegex(sentence, r"\b(BUG|REQ|ADR)-\d{4}\b", f"{where} cites a record on a shipped page")
            checks = re.findall(r"`mise run ([A-Za-z0-9_-]+)`", sentence) + re.findall(r"`CI job ([A-Za-z0-9_-]+)`", sentence)
            if not checks:
                self.assertRegex(sentence, r"no gate check", f"{where} names no gate check and doesn't say there is none")
            for check in checks:
                self.assertTrue(check in tasks or check in jobs, f"{where} names a gate check that doesn't exist: {check}")
            named_skills = re.findall(r"`([a-z0-9-]+:[a-z0-9-]+)` skill", sentence)
            if not named_skills:
                self.assertRegex(sentence, r"no skill", f"{where} names no skill and doesn't say there is none")
            for skill in named_skills:
                self.assertIn(skill, known_skills, f"{where} names a skill that doesn't exist")

    def test_a_hook_whose_rule_has_no_gate_check_has_a_defect_naming_it(self):
        """TSK-4905 criterion 2, REQ-2712: the defect names the hook and the missing check."""
        bugs = [p.read_text(encoding="utf-8") for p in (ROOT / "project" / "bugs").glob("BUG-*.md")]
        for unit, subcommand in BLOCKING:
            sentence = readme_sentence(unit, subcommand)
            if re.findall(r"`mise run ([A-Za-z0-9_-]+)`", sentence):
                continue
            found = [t for t in bugs if "violates: REQ-2712" in t and f"`{subcommand}`" in t and unit in t]
            self.assertTrue(found, f"{unit} `{subcommand}` has no gate check and no defect against REQ-2712 names it")


# The gate check each hook's sentence names, where one exists (BUG-1560 to BUG-1564). The loop's `stop` has none:
# nothing in a tree or a history shows a turn that ended with work left.
CHECKS = {
    ("meow-git", "commit-guard"): "layers",
    ("meow-git", "push-guard"): "layers",
    ("meow-github", "governance-guard"): "test-tools",
    ("meow-prose-gate", "check"): "layers",
}


class Named(unittest.TestCase):
    def test_each_hook_with_a_gate_check_names_it(self):
        """REQ-2712: the sentence names the check, and the check is a task of the gate."""
        mise = (ROOT / "mise.toml").read_text(encoding="utf-8")
        def depends(task):
            found = re.search(rf"^\[tasks\.{task}\].*?^depends = \[(.*?)\]", mise, re.M | re.S)
            return re.findall(r'"([^"]+)"', found.group(1)) if found else []

        members = set(depends("all"))
        for task in list(members):
            members.update(depends(task))
        for (unit, subcommand), task in CHECKS.items():
            sentence = readme_sentence(unit, subcommand)
            self.assertIn(f"`mise run {task}`", sentence, f"{unit} `{subcommand}` doesn't name `mise run {task}`")
            self.assertNotIn("no gate check", sentence, f"{unit} `{subcommand}` still says there is none")
            self.assertIn(task, members, f"`{task}` isn't a member of the gate")

    def test_the_governance_guard_names_a_skill_in_its_unit(self):
        """BUG-1562, REQ-2712: the rule has an instruction beside its hook and its check."""
        sentence = readme_sentence("meow-github", "governance-guard")
        self.assertIn("`meow-github:governance` skill", sentence)
        self.assertIn("meow-github:governance", skills())


class Abstention(unittest.TestCase):
    """TSK-4905 criterion 3, REQ-2714: a crash or a timeout reads as abstention, never as an answer."""

    def machine(self):
        system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}[os.uname().sysname]
        cpu = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}[os.uname().machine]
        return f"{cpu}-{system}"

    def run_launcher(self, unit, subcommand, body, timeout):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            (bin_dir / self.machine()).mkdir(parents=True)
            launcher = bin_dir / unit
            launcher.write_text((PLUGINS / unit / "bin" / unit).read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            fake = bin_dir / self.machine() / "meow"
            fake.write_text(body, encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env = {"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/none"}
            return subprocess.run(["sh", str(launcher), subcommand], cwd=tmp, env=env, input="{}",
                                  capture_output=True, text=True, timeout=timeout)

    def test_a_binary_that_exits_one_prints_no_decision_and_exits_other_than_two(self):
        for unit, subcommand in BLOCKING:
            done = self.run_launcher(unit, subcommand, "#!/bin/sh\nexit 1\n", 20)
            self.assertNotEqual(done.returncode, 2, f"{unit} {subcommand}: a crash read as a denial")
            self.assertNotIn("permissionDecision", done.stdout, f"{unit} {subcommand}")
            self.assertNotIn('"decision"', done.stdout, f"{unit} {subcommand}")

    def test_a_binary_killed_by_its_timeout_prints_no_decision(self):
        for unit, subcommand in BLOCKING:
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                self.run_launcher(unit, subcommand, "#!/bin/sh\nsleep 30\n", 1)
            printed = caught.exception.stdout or b""
            printed = printed.decode() if isinstance(printed, bytes) else printed
            self.assertNotIn("permissionDecision", printed, f"{unit} {subcommand}")


if __name__ == "__main__":
    unittest.main()
