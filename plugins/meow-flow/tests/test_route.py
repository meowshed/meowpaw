# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Static checks on the route skill SPC-1090 "The route" states, and ADR-2930's classification.

What a program can read is the skill: that it dispatches nothing, and that the sizes, shapes and
fields its rules name. ADR-2980 removed the case set that measured the skill's behaviour by model
runs, so the behaviour rests on review until the evaluation is redesigned."""

import os
import re
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
REPOSITORY = UNIT.parent.parent
SKILL = UNIT / "skills" / "route" / "SKILL.md"
METHOD = UNIT / "skills" / "method" / "SKILL.md"
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


class SkillRoute(unittest.TestCase):
    """ADR-2930: the skill states the route's vocabulary itself, and names no dispatch."""

    def skill(self):
        self.assertTrue(SKILL.is_file(), f"{SKILL} doesn't exist")
        return SKILL.read_text(encoding="utf-8")

    def test_the_skill_names_sizes_shapes_and_fields(self):
        """REQ-0334, REQ-0344, REQ-0338, REQ-0342: the skill names the sizes none, reduced and full, the four
        shapes including several changes, and the reply fields size, shape, reason, ambiguous and override
        words."""
        body = flat(split(self.skill())[1])
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

    def test_the_skill_dispatches_nothing(self):
        """ADR-2930: no agent is dispatched, and the session classifies the request itself."""
        text = flat(self.skill())
        self.assertNotRegex(text, r"meow-flow:router\b")
        self.assertRegex(text, r"classif(?:y|ies)")


def names_the_route_skill(text):
    """Whether the text names the `route` skill, and not only the router agent or the verb."""
    return re.search(r"meow-flow:route\b|\broute skill\b", flat(text)) is not None


class RouteSkill(unittest.TestCase):
    """SPC-1090 "The route": the skill takes four override words, and the method's
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
