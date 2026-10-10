# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for check_workflows: a workflow starts read-only and trusts no foreign value (ADR-2520)."""

import io
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_workflows import ROOT, main  # noqa: E402

GOOD = """\
    name: Good

    on:
      pull_request:
        paths:
          - crates/**
      push:
        branches: [main]

    permissions:
      contents: read

    jobs:
      build:
        name: build ${{ matrix.target }}
        strategy:
          matrix:
            include:
              - { target: aarch64-apple-darwin, os: macos-15 }
        runs-on: ${{ matrix.os }}
        permissions:
          contents: write
        steps:
          - uses: actions/checkout@v7
          - name: Build
            env:
              TARGET: ${{ matrix.target }}
            run: |
              # The target arrives through the environment.
              build "$TARGET"
    """


class Workflows(unittest.TestCase):
    def tree(self, workflows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        directory = root / ".github" / "workflows"
        directory.mkdir(parents=True)
        for name, text in workflows.items():
            (directory / name).write_text(textwrap.dedent(text), encoding="utf-8")
        return root

    def run_check(self, root):
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(root)
        return status, out.getvalue().splitlines()

    def test_a_read_only_workflow_passes(self):
        """REQ-2196, REQ-2198, REQ-2200: a read-only top, a checkout under pull_request and env passes."""
        status, out = self.run_check(self.tree({"good.yml": GOOD}))
        self.assertEqual(status, 0, out)
        self.assertEqual(out, ["1 workflow files, 0 findings"])

    def test_no_top_level_permissions_fails_naming_the_file(self):
        """REQ-2196: a workflow with no top-level permissions takes the default token."""
        text = GOOD.replace("    permissions:\n      contents: read\n\n", "")
        status, out = self.run_check(self.tree({"bare.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out, [".github/workflows/bare.yml: no top-level permissions", "1 workflow files, 1 findings"]
        )

    def test_a_top_level_write_fails_naming_the_permission(self):
        """REQ-2196: write access at the top reaches every job."""
        text = GOOD.replace("      contents: read\n\n", "      contents: write\n\n")
        status, out = self.run_check(self.tree({"wide.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/wide.yml:11: top-level permission contents: write, where only contents: read is allowed",
                "1 workflow files, 1 findings",
            ],
        )

    def test_a_top_level_write_all_fails_naming_it(self):
        """REQ-2196: permissions: write-all at the top is the widest token there is."""
        text = GOOD.replace("    permissions:\n      contents: read\n", "    permissions: write-all\n")
        status, out = self.run_check(self.tree({"all.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/all.yml:10: top-level permission write-all, where only contents: read is allowed",
                "1 workflow files, 1 findings",
            ],
        )

    def test_pull_request_target_with_a_checkout_fails_naming_the_trigger(self):
        """REQ-2198: pull_request_target runs with a write token, so it checks out no code."""
        text = GOOD.replace("      pull_request:\n", "      pull_request_target:\n")
        status, out = self.run_check(self.tree({"target.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/target.yml:4: trigger pull_request_target in a workflow that runs actions/checkout",
                "1 workflow files, 1 findings",
            ],
        )

    def test_workflow_run_with_a_checkout_fails_naming_the_trigger(self):
        """REQ-2198: workflow_run runs with a write token, in the list form of on: too."""
        text = GOOD.replace(
            "    on:\n      pull_request:\n        paths:\n          - crates/**\n      push:\n        branches: [main]\n",
            "    on: [push, workflow_run]\n",
        )
        status, out = self.run_check(self.tree({"run.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/run.yml:3: trigger workflow_run in a workflow that runs actions/checkout",
                "1 workflow files, 1 findings",
            ],
        )

    def test_a_forbidden_trigger_without_a_checkout_passes(self):
        """REQ-2198: pull_request_target that checks out nothing runs no untrusted code."""
        text = GOOD.replace("      pull_request:\n", "      pull_request_target:\n").replace(
            "          - uses: actions/checkout@v7\n", ""
        )
        status, out = self.run_check(self.tree({"label.yml": text}))
        self.assertEqual(status, 0, out)
        self.assertEqual(out, ["1 workflow files, 0 findings"])

    def test_an_expression_in_a_run_block_fails_naming_its_line(self):
        """REQ-2200: an issue's title in a run: block is a value the workflow doesn't control."""
        text = GOOD.replace(
            '              build "$TARGET"\n',
            '              build "$TARGET"\n              echo "${{ github.event.issue.title }}"\n',
        )
        status, out = self.run_check(self.tree({"title.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out, [".github/workflows/title.yml:31: ${{ in a run: line", "1 workflow files, 1 findings"]
        )

    def test_an_expression_in_a_one_line_run_fails_naming_its_line(self):
        """REQ-2200: a one-line run: value is read the same way."""
        text = GOOD.replace(
            '            run: |\n              # The target arrives through the environment.\n              build "$TARGET"\n',
            "            run: build ${{ matrix.target }}\n",
        )
        status, out = self.run_check(self.tree({"inline.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out, [".github/workflows/inline.yml:28: ${{ in a run: line", "1 workflow files, 1 findings"]
        )

    def test_the_same_value_through_env_passes(self):
        """REQ-2200: the issue's title passed through env: reaches the script as data."""
        text = GOOD.replace(
            "              TARGET: ${{ matrix.target }}\n",
            "              TARGET: ${{ matrix.target }}\n              TITLE: ${{ github.event.issue.title }}\n",
        ).replace('              build "$TARGET"\n', '              build "$TARGET"\n              echo "$TITLE"\n')
        status, out = self.run_check(self.tree({"env.yml": text}))
        self.assertEqual(status, 0, out)
        self.assertEqual(out, ["1 workflow files, 0 findings"])

    def test_a_step_that_runs_the_suite_fails_naming_its_line(self):
        """TSK-5250 criterion 1, REQ-3035: a run: block that starts the suite makes a model call in CI."""
        text = GOOD.replace('              build "$TARGET"\n', '              build "$TARGET"\n              mise run eval\n')
        status, out = self.run_check(self.tree({"eval.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/eval.yml:31: names mise run eval, and no workflow makes a model call",
                "1 workflow files, 1 findings",
            ],
        )

    def test_a_model_credential_as_an_env_key_fails_naming_its_line(self):
        """TSK-5250 criterion 2, REQ-3035: a credential name under env: gives the job a way to call a model."""
        text = GOOD.replace(
            "              TARGET: ${{ matrix.target }}\n",
            "              TARGET: ${{ matrix.target }}\n              ANTHROPIC_API_KEY: x\n",
        )
        status, out = self.run_check(self.tree({"key.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/key.yml:28: names ANTHROPIC_API_KEY, and no workflow makes a model call",
                "1 workflow files, 1 findings",
            ],
        )

    def test_a_model_credential_inside_a_value_fails_naming_its_line(self):
        """TSK-5250 criterion 2, REQ-3035: a secret read by name is a credential wherever it lands."""
        text = GOOD.replace(
            "              TARGET: ${{ matrix.target }}\n",
            "              TARGET: ${{ matrix.target }}\n              TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}\n",
        )
        status, out = self.run_check(self.tree({"value.yml": text}))
        self.assertEqual(status, 1, out)
        self.assertEqual(
            out,
            [
                ".github/workflows/value.yml:28: names CLAUDE_CODE_OAUTH_TOKEN, and no workflow makes a model call",
                "1 workflow files, 1 findings",
            ],
        )

    def test_a_file_that_does_not_parse_fails_naming_it(self):
        """REQ-2196: a workflow the check can't read is one it can't hold to the rules."""
        status, out = self.run_check(self.tree({"broken.yaml": "on: [push\npermissions:\n  contents: read\n"}))
        self.assertEqual(status, 1, out)
        self.assertEqual(len(out), 2, out)
        self.assertTrue(out[0].startswith(".github/workflows/broken.yaml: doesn't parse: "), out)
        self.assertEqual(out[1], "1 workflow files, 1 findings")

    def test_no_workflow_files_fails(self):
        """REQ-2196: a check that read nothing has held nothing to the rules."""
        status, out = self.run_check(self.tree({}))
        self.assertEqual(status, 1, out)
        self.assertEqual(out, ["no workflow files under .github/workflows/", "0 workflow files, 1 findings"])

    def test_this_repository_s_workflows_pass(self):
        """REQ-2196, REQ-2198, REQ-2200: the workflows this repository runs hold every rule."""
        status, out = self.run_check(ROOT)
        self.assertEqual(status, 0, out)
        self.assertEqual(len(out), 1, out)
        self.assertRegex(out[0], r"^[1-9]\d* workflow files, 0 findings$")


if __name__ == "__main__":
    unittest.main()
