# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for check_workflows: a workflow starts read-only and trusts no foreign value (ADR-2520)."""

import io
import re
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_workflows import ROOT, Reader, main  # noqa: E402

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

    def test_an_npm_publish_inside_a_pipeline_fails_naming_its_line(self):
        """BUG-1590: the shell reads a pipeline's status from its last command, so
        `npm publish | tee` publishes nothing while the step stays green."""
        bad = GOOD.replace(
            '              # The target arrives through the environment.\n              build "$TARGET"',
            '              if ! (npm publish --provenance --access public) 2>&1 | tee /tmp/publish.log; then\n                :\n              fi',
        )
        status, lines = self.run_check(self.tree({"a.yml": bad}))
        self.assertEqual(status, 1, lines)
        self.assertTrue(any("npm publish inside a pipeline" in line for line in lines), lines)

    def test_an_npm_publish_whose_status_decides_passes(self):
        """BUG-1590's companion: npm's own exit status decides, and no pipe stands between it and the step."""
        good = GOOD.replace(
            '              # The target arrives through the environment.\n              build "$TARGET"',
            '              if (npm publish --provenance --access public) >"$log" 2>&1; then\n                echo published\n              fi',
        )
        status, lines = self.run_check(self.tree({"a.yml": good}))
        self.assertEqual((status, lines), (0, ["1 workflow files, 0 findings"]), lines)

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

    def governance_run(self, command):
        text = GOOD.replace('              build "$TARGET"\n', f'              build "$TARGET"\n              {command}\n')
        return self.run_check(self.tree({"gov.yml": text}))

    def test_a_step_that_changes_governance_fails_naming_its_line(self):
        """BUG-1562, REQ-2576, REQ-2712: a workflow runs no `gh` command the governance guard asks about, in any
        spelling the guard reads."""
        for command in (
            "gh api -X PUT repos/o/r/branches/main/protection",
            "gh api -X put repos/o/r/hooks/1",
            "gh api -XPUT repos/o/r/hooks/1",
            "gh api repos/o/r/hooks -f url=x",
            "gh api -X PATCH repos/o/r",
            "gh api repos/o/r/rulesets --method POST",
            "gh repo edit o/r --visibility private",
            "gh repo unarchive o/r",
            "gh secret set TOKEN",
            "gh variable remove NAME",
            "gh workflow disable ci.yml",
            "gh -R o/r api -X PUT repos/o/r/hooks/1",
            "FOO=1 gh secret set TOKEN",
        ):
            status, out = self.governance_run(command)
            self.assertEqual(status, 1, (command, out))
            self.assertIn("changes how the repository is governed", out[0], command)
            self.assertTrue(out[0].startswith(".github/workflows/gov.yml:31:"), (command, out))

    def test_a_continued_command_is_one_command(self):
        """BUG-1562: `gh api \\` with the method and the path on later lines is read as one command."""
        text = GOOD.replace(
            '              build "$TARGET"\n',
            '              build "$TARGET"\n              gh api \\\n                -X PUT \\\n                repos/o/r/branches/main/protection\n',
        )
        status, out = self.run_check(self.tree({"gov.yml": text}))
        self.assertEqual(status, 1, out)

    def test_text_that_only_mentions_a_governance_command_passes(self):
        """BUG-1562: a comment, an echo, a read and a comment on an issue are not changes."""
        for command in (
            "# never gh secret set here",
            "echo 'do not gh repo edit'",
            "gh api repos/o/r/branches/main/protection",
            "gh api -X POST repos/o/r/issues/1/comments -f body='see /hooks docs'",
            "gh api repos/o/r/hooks | jq . ; curl -X POST https://example.org/hooks",
            "gh pr view 7",
        ):
            status, out = self.governance_run(command)
            self.assertEqual(status, 0, (command, out))

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

    def test_the_gate_step_carries_the_job_token_in_its_own_environment(self):
        """The `gate` step that runs `mise run all` has `GITHUB_TOKEN` in its own `env:`, so mise installs a tool
        with the job's token and not anonymously, where 60 requests an hour fail a run (2026-10-10, PR 882)."""
        text = (ROOT / ".github/workflows/ci.yml").read_text()
        step = text.split("- run: mise run all", 1)
        self.assertEqual(len(step), 2, "the gate runs `mise run all` as one step")
        before, after = step
        block = before.rsplit("- ", 1)[-1] + "- run: mise run all" + after.split("\n  attribution:", 1)[0]
        self.assertRegex(block, r"env:\s*\n\s+GITHUB_TOKEN: \$\{\{ github\.token \}\}")
        self.assertNotRegex(before.split("jobs:", 1)[-1].split("steps:", 1)[0], r"GITHUB_TOKEN", "not on the job")

    def test_every_step_that_reads_build_target_sets_it(self):
        """Each step of `rust-tool.yml` that reads `$BUILD_TARGET` sets it in its own `env:`, because a step with
        none reads it empty, and `find plugins/*/bin/` then hands ldid every launcher (2026-10-05, PR 860)."""
        text = (ROOT / ".github/workflows/rust-tool.yml").read_text()
        steps = re.split(r"\n(?=      - )", text)
        reading = [s for s in steps if "$BUILD_TARGET" in s and "uses:" not in s.split("\n", 1)[0]]
        self.assertTrue(reading, "the workflow reads $BUILD_TARGET in some step")
        for step in reading:
            self.assertIn("BUILD_TARGET: ${{ matrix.target }}", step, step.split("\n", 1)[0])

    def test_this_repository_s_workflows_pass(self):
        """REQ-2196, REQ-2198, REQ-2200: the workflows this repository runs hold every rule."""
        status, out = self.run_check(ROOT)
        self.assertEqual(status, 0, out)
        self.assertEqual(len(out), 1, out)
        self.assertRegex(out[0], r"^[1-9]\d* workflow files, 0 findings$")


# The three workflows that publish an archive: each unit's Claude Code zip, each Pi package's zip and the
# meow-full zip. TSK-4630 names `release.yml`, which ADR-2810's build split replaced with these.
RELEASES = ("claude-release.yml", "pi-release.yml", "rust-tool.yml")
ATTEST = "actions/attest-build-provenance"
EXPRESSION = re.compile(r"\$\{\{\s*env\.(\w+)\s*\}\}")


def release_jobs(name):
    doc = Reader((ROOT / ".github/workflows" / name).read_text(encoding="utf-8")).document()
    return doc, doc["jobs"]


def publishes_archives(step):
    return isinstance(step.get("run"), str) and "gh release create" in step["run"]


def attests(step):
    return isinstance(step.get("uses"), str) and step["uses"].startswith(ATTEST + "@")


class Attestation(unittest.TestCase):
    """TSK-4630: the job that publishes a release attests each archive it publishes (REQ-2218, ADR-2520)."""

    def test_the_publishing_job_attests_every_archive_it_publishes_and_only_when_it_publishes(self):
        """TSK-4630 criterion 1, REQ-2218: a consumer checks what an archive was built from with
        `gh attestation verify`, so the job that publishes runs `actions/attest-build-provenance`, pinned to a
        released major version, after the archives exist and before any `gh release` publishes one, whose
        subject names each archive the job publishes, and which runs only when the run publishes."""
        for name in RELEASES:
            with self.subTest(workflow=name):
                _, jobs = release_jobs(name)
                publishing = {job: spec for job, spec in jobs.items() if any(map(publishes_archives, spec["steps"]))}
                self.assertTrue(publishing, "some job publishes an archive")
                for job, spec in publishing.items():
                    steps = spec["steps"]
                    attesting = [i for i, step in enumerate(steps) if attests(step)]
                    self.assertEqual(len(attesting), 1, f"{job} attests in one step")
                    at = attesting[0]
                    step = steps[at]
                    self.assertRegex(step["uses"], r"@v[1-9]\d*$", "pinned to a released major version")
                    first_publish = min(i for i, s in enumerate(steps) if publishes_archives(s))
                    self.assertLess(at, first_publish, "attests before it publishes")
                    publish_if = steps[first_publish].get("if")
                    attest_if = step.get("if")
                    if publish_if is None:
                        self.assertIsNone(attest_if, "the job's own condition is the publishing one")
                        self.assertIn("if", spec, f"{job} runs only when the run publishes")
                    else:
                        self.assertIsNotNone(attest_if, "runs only when the run publishes")
                        self.assertTrue(attest_if == publish_if or attest_if.startswith(f"({publish_if}) && "),
                                        attest_if)
                    subject = step.get("with", {})
                    if "subject-checksums" in subject:
                        # Each archive joins the list the publishing step reads beside its own checksum line.
                        listed = subject["subject-checksums"]
                        packing = [s for s in steps[:at] if isinstance(s.get("run"), str) and ">> dist/tags" in s["run"]]
                        self.assertEqual(len(packing), 1, "one step lists what the job publishes")
                        lines = packing[0]["run"].split("\n")
                        for i, line in enumerate(lines):
                            if ">> dist/tags" in line:
                                near = lines[max(i - 1, 0):i + 2]
                                self.assertTrue(any("sha256sum" in n and f">> {listed}" in n for n in near), line)
                    else:
                        self.assertIn("subject-path", subject, "the step names its subject")
                        path = EXPRESSION.sub(r"$\1", subject["subject-path"])
                        self.assertIn(path, steps[first_publish]["run"], "the subject is the archive published")

    def test_only_the_publishing_job_holds_the_attestation_permissions(self):
        """TSK-4630 criterion 2, REQ-2218, REQ-2196: the attestation needs `id-token: write` and
        `attestations: write`, so the job that publishes holds both, no other job holds either, and the top
        level still holds `contents: read` alone."""
        for name in RELEASES:
            with self.subTest(workflow=name):
                doc, jobs = release_jobs(name)
                self.assertEqual(dict(doc["permissions"]), {"contents": "read"})
                for job, spec in jobs.items():
                    granted = dict(spec.get("permissions") or {})
                    held = {key for key in ("id-token", "attestations") if granted.get(key) == "write"}
                    if any(map(publishes_archives, spec["steps"])):
                        self.assertEqual(held, {"id-token", "attestations"}, job)
                    else:
                        self.assertEqual(held, set(), job)


if __name__ == "__main__":
    unittest.main()
