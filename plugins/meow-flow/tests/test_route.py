# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Static checks on the router agent SPC-1090 "The route" states, and ADR-2100's allowlist.

The router's behaviour on a request is a model's, so its cases run by hand under `evals/`. What a program can
read is the definition: the tools its front matter grants and the sizes, shapes and fields its prompt names.
"""

import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
ROUTER = UNIT / "agents" / "router.md"
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


if __name__ == "__main__":
    unittest.main()
