# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A hook that asks a judge fires only where a command can publish text (TSK-5681, REQ-2798).

A hook asks a judge when its command is `meow-prose-gate check`. The judge reads published text, so its hook
carries an `if` matcher naming a command that publishes text, or a wrapper form such as `git -C` in which one can
hide. The gate's program then calls its judge only for a publishing command, which the gate's own fixtures hold.
"""

import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The commands that publish text, and the wrappers one can hide in.
PUBLISHING = ("git commit", "gh pr create", "gh pr edit", "gh pr comment", "gh pr review", "gh issue create",
              "gh issue edit", "gh issue comment", "gh release create", "gh release edit")
WRAPPERS = ("git -C", "git -c", "gh -R", "gh --repo")
SHAPE = re.compile(r"^Bash\((.+) \*\)$")


def judge_hooks(root):
    """Each (file, `if` matcher or None) of a hook under `root` whose command asks a judge."""
    found = []
    for path in sorted(root.glob("plugins/*/hooks/hooks.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for groups in data["hooks"].values():
            for group in groups:
                for hook in group["hooks"]:
                    if "meow-prose-gate" in hook.get("command", "") and hook["command"].rstrip().endswith("check"):
                        found.append((path.relative_to(root), hook.get("if")))
    return found


def unfit(matcher):
    """Whether a judge hook's `if` matcher names neither a publishing command nor a wrapper form."""
    shape = SHAPE.match(matcher or "")
    return not shape or shape.group(1) not in PUBLISHING + WRAPPERS


class JudgeHookMatchers(unittest.TestCase):
    def test_every_hook_that_asks_a_judge_names_a_publishing_command_or_a_wrapper(self):
        """TSK-5681 criterion 1, REQ-2798: no judge hook fires on a command outside the shapes that publish."""
        hooks = judge_hooks(ROOT)
        self.assertTrue(hooks, "no hook asks a judge, so the check read nothing")
        for path, matcher in hooks:
            with self.subTest(hook=f"{path}: {matcher}"):
                self.assertFalse(unfit(matcher), f"{path} asks a judge on {matcher!r}")

    def test_a_judge_hook_with_no_matcher_fails(self):
        """TSK-5681 criterion 1, REQ-2798: a copy of the gate's hooks with the `if` removed fails the check."""
        source = ROOT / "plugins" / "meow-prose-gate" / "hooks" / "hooks.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        for group in data["hooks"]["PreToolUse"]:
            for hook in group["hooks"]:
                hook.pop("if", None)
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / "plugins" / "meow-prose-gate" / "hooks"
            copy.mkdir(parents=True)
            (copy / "hooks.json").write_text(json.dumps(data), encoding="utf-8")
            found = judge_hooks(Path(scratch))
        self.assertTrue(found)
        self.assertTrue(all(unfit(matcher) for _, matcher in found))

    def test_a_matcher_outside_the_shapes_is_unfit(self):
        """TSK-5681 criterion 1, REQ-2798: a bare `Bash` and an unrelated command are not publishing shapes."""
        for matcher in (None, "Bash", "Bash(git status *)", "Bash(npm test *)"):
            self.assertTrue(unfit(matcher), matcher)
        for matcher in ("Bash(git commit *)", "Bash(gh -R *)"):
            self.assertFalse(unfit(matcher), matcher)


if __name__ == "__main__":
    unittest.main()
