# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Static checks on the router agent SPC-1090 "The route" states, and ADR-2100's allowlist.

The router's behaviour on a request is a model's, so its cases run by hand under `evals/`. What a program can
read is the definition: the tools its front matter grants and the sizes, shapes and fields its prompt names.
"""

import os
import re
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
REPOSITORY = UNIT.parent.parent
ROUTER = UNIT / "agents" / "router.md"
SKILL = UNIT / "skills" / "route" / "SKILL.md"
METHOD = UNIT / "skills" / "method" / "SKILL.md"
EVALS = UNIT / "evals"
ROUTER_CASES = ("route-plain-words", "route-a-tiny-fix", "route-both-ways", "route-three-changes")
SKILL_CASES = {
    "route-a-typo": "criterion 4, REQ-0330, REQ-0332",
    "route-reported-ambiguous": "criterion 5, REQ-0340",
    "route-given": "criterion 6, REQ-0336",
    "route-overridden": "criterion 6, REQ-0336",
    "route-reduced-unauthorised": "criterion 6, REQ-0336",
    "route-list-overridden": "criterion 6, REQ-0336",
    "route-a-question": "criterion 8, REQ-0330",
}
WRITING_TOOLS = ("Write", "Edit", "NotebookEdit", "Bash")
READ_ONLY = {"Read", "Grep", "Glob"}


def split(text):
    """The front matter's lines and the body, or no lines where the file opens with no front matter."""
    if not text.startswith("---\n"):
        return [], text
    front, _, body = text[4:].partition("\n---\n")
    return front.splitlines(), body


def tools(text):
    """The tools the front matter grants, or None where it names no `tools` field."""
    front, _ = split(text)
    line = next((line for line in front if line.startswith("tools:")), None)
    if line is None:
        return None
    value = line.split(":", 1)[1].strip().strip("[]")
    return {name.strip().strip("'\"") for name in value.split(",") if name.strip()}


def flat(text):
    """Lower case, no backticks, and every run of white space one space, so a wrapped line reads as one."""
    return re.sub(r"\s+", " ", text.replace("`", "")).lower().strip()


class RouterAgent(unittest.TestCase):
    """ADR-2100: the router holds Read, Grep and Glob only, and its prompt states the route's vocabulary."""

    def router(self):
        self.assertTrue(ROUTER.is_file(), f"{ROUTER} doesn't exist")
        return ROUTER.read_text(encoding="utf-8")

    def assertReadOnly(self, text):
        granted = tools(text)
        self.assertIsNotNone(granted, "the front matter names no tools, so the agent inherits every tool")
        self.assertEqual(granted, READ_ONLY)

    def test_tools_are_read_grep_glob(self):
        """TSK-3500 criterion 1, REQ-0346: the router's front matter names exactly Read, Grep and Glob."""
        self.assertReadOnly(self.router())

    def test_a_writing_copy_fails(self):
        """TSK-3500 criterion 1, REQ-0346: a copy of the router that adds Write, Edit or Bash, or drops `tools`,
        fails the same assertion the shipped router passes."""
        text = self.router()
        line = next(line for line in split(text)[0] if line.startswith("tools:"))
        copies = {name: text.replace(line, f"{line}, {name}", 1) for name in ("Write", "Edit", "Bash")}
        copies["no tools"] = text.replace(line + "\n", "", 1)
        for name, copy in copies.items():
            with self.subTest(copy=name):
                self.assertNotEqual(copy, text)
                with self.assertRaises(AssertionError):
                    self.assertReadOnly(copy)

    def test_the_prompt_names_sizes_shapes_and_fields(self):
        """TSK-3500 criterion 2, REQ-0334, REQ-0344, REQ-0338, REQ-0342: the prompt names the sizes none,
        reduced and full, the four shapes including several changes, and the reply fields size, shape, reason,
        ambiguous and override words."""
        body = flat(split(self.router())[1])
        for size in ("none", "reduced", "full"):
            with self.subTest(size=size):
                self.assertRegex(body, rf"\b{size}\b")
        for shape in ("new work", "extends records", "a defect", "several changes"):
            with self.subTest(shape=shape):
                self.assertIn(shape, body)
        for field in ("size", "shape", "reason", "ambiguous", "override words"):
            with self.subTest(field=field):
                self.assertRegex(body, rf"\b{field}\b")
        with self.subTest(rule="the larger size where the evidence points to two"):
            self.assertRegex(body, r"\blarger\b")
        with self.subTest(rule="it reads the profile"):
            self.assertIn(".meowpaw/profile.toml", body)


def names_the_route_skill(text):
    """Whether the text names the `route` skill, and not only the router agent or the verb."""
    return re.search(r"meow-flow:route\b|\broute skill\b", flat(text)) is not None


def route_cases():
    """Every route case: TSK-3500's, TSK-3510's and any other directory under `evals/` named `route-*`."""
    found = {path.name for path in EVALS.glob("route-*") if path.is_dir()}
    return sorted(found | set(ROUTER_CASES) | set(SKILL_CASES))


class RouteSkill(unittest.TestCase):
    """SPC-1090 "The route": the skill dispatches the router, takes four override words, and the method's
    entry points name it."""

    def skill(self):
        self.assertTrue(SKILL.is_file(), f"{SKILL} doesn't exist")
        return SKILL.read_text(encoding="utf-8")

    def test_the_skill_names_four_override_words(self):
        """TSK-3510 criterion 1, REQ-0336: the skill names route none, route reduced, route full and route
        one."""
        text = flat(self.skill())
        for word in ("route none", "route reduced", "route full", "route one"):
            with self.subTest(word=word):
                self.assertRegex(text, rf"\b{word}\b")

    def test_the_skill_dispatches_the_router(self):
        """TSK-3510 criterion 1, REQ-0330, REQ-0332: the skill names meow-flow:router as the agent it
        dispatches."""
        self.assertRegex(flat(self.skill()), r"meow-flow:router\b")

    def test_the_method_and_constitution_name_the_route(self):
        """TSK-3510 criterion 2, REQ-0330: the method skill and CLAUDE.md's own_method_first, where it names
        trivial work, each name the route skill."""
        with self.subTest(file="the method skill"):
            self.assertTrue(names_the_route_skill(METHOD.read_text(encoding="utf-8")))
        with self.subTest(file="CLAUDE.md own_method_first"):
            constitution = (REPOSITORY / "CLAUDE.md").read_text(encoding="utf-8")
            principle = re.search(r'<principle name="own_method_first">(.*?)</principle>', constitution, re.DOTALL)
            self.assertIsNotNone(principle, "CLAUDE.md has no own_method_first principle")
            self.assertRegex(flat(principle.group(1)), r"\btrivial\b")
            self.assertTrue(names_the_route_skill(principle.group(1)))


class RouteCases(unittest.TestCase):
    """The static half of TSK-3510's cases: each exists with its threshold before its first run (REQ-0159),
    every route case carries the shared grader for writes before the route, and every route case scaffolds a
    clean repository. Whether a model passes a case is measured by hand, never here."""

    def test_each_skill_case_has_a_threshold(self):
        """TSK-3510 criteria 4, 5, 6 and 8, REQ-0330, REQ-0332, REQ-0336, REQ-0340: each case the criteria
        name exists under evals/, names itself and carries a threshold in thresholds.toml before its first
        run."""
        thresholds = tomllib.loads((EVALS / "thresholds.toml").read_text(encoding="utf-8"))["cases"]
        for name, criterion in SKILL_CASES.items():
            with self.subTest(case=name, covers=criterion):
                case = EVALS / name / "case.yaml"
                self.assertTrue(case.is_file(), f"{case} doesn't exist")
                self.assertRegex(case.read_text(encoding="utf-8"), rf"(?m)^name: {re.escape(name)}$")
                self.assertIn(name, thresholds)

    def test_every_route_case_shares_the_write_grader(self):
        """TSK-3510 criterion 7, REQ-0332: every route case, TSK-3500's included, carries one grader, the same
        in each, that names Write, Edit, NotebookEdit and Bash as the calls that must not come before the
        route is reported."""
        shared = set()
        for name in route_cases():
            with self.subTest(case=name):
                graders = EVALS / name / "graders"
                paths = sorted(graders.glob("*")) if graders.is_dir() else []
                texts = [path.read_text(encoding="utf-8") for path in paths]
                matching = [text for text in texts if all(re.search(rf"\b{tool}\b", text) for tool in WRITING_TOOLS)]
                self.assertEqual(len(matching), 1, f"{name} has {len(matching)} graders naming every writing tool")
                shared.add(matching[0])
        self.assertEqual(len(shared), 1, "the route cases' write graders differ, so no one grader is shared")

    def test_every_route_case_starts_in_a_clean_repository(self):
        """TSK-3510 criterion 7, REQ-0332: every route case's scaffold, run in an empty directory, leaves a git
        repository where git status --porcelain prints nothing."""
        for name in route_cases():
            with self.subTest(case=name):
                scaffold = EVALS / name / "scaffold.sh"
                self.assertTrue(scaffold.is_file(), f"{scaffold} doesn't exist")
                with tempfile.TemporaryDirectory() as scratch:
                    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(Path(scratch).resolve().parent))
                    ran = subprocess.run(["sh", str(scaffold)], cwd=scratch, env=env, capture_output=True, text=True)
                    self.assertEqual(ran.returncode, 0, ran.stderr)
                    status = subprocess.run(
                        ["git", "status", "--porcelain"], cwd=scratch, env=env, capture_output=True, text=True
                    )
                    self.assertEqual(status.returncode, 0, f"no git repository after the scaffold: {status.stderr}")
                    self.assertEqual(status.stdout, "")


if __name__ == "__main__":
    unittest.main()
