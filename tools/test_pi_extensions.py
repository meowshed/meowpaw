# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The Pi extensions load a command's skill, start a loop run from the session, run the readers as cheap nested calls, and carry the style the plugin ships (BUG-1600, BUG-1610, BUG-1630, REQ-4618, REQ-3526)."""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOW = ROOT / "packages" / "meow-flow"
LOOP = ROOT / "packages" / "meow-loop"
PROSE = ROOT / "packages" / "meow-prose"
STYLE = ROOT / "plugins" / "meow-core" / "output-styles" / "meow.md"

FLOW_COMMANDS = [
    ("meow-flow:research", "method"),
    ("meow-flow:requirements", "method"),
    ("meow-flow:design", "method"),
    ("meow-flow:spec", "method"),
    ("meow-flow:implement", "method"),
    ("meow-flow:review", "method"),
    ("meow-flow:run", "run"),
    ("meow-flow:init", "init"),
    ("meow-flow:onboard", "onboard"),
    ("meow-flow:upgrade", "upgrade"),
]

NODE_CHECK = """
import { pickModels, responseText, answerWith } from "<file>";

const assert = (ok, why) => {
  if (!ok) {
    console.error("FAIL: " + why);
    process.exit(1);
  }
};

const openrouterClaude = { provider: "openrouter", id: "anthropic/claude-sonnet-5.5" };
const glm = { provider: "openrouter", id: "z-ai/glm-5.3-flash" };
const xiaomi = { provider: "xiaomi-token-plan-ams", id: "mimo-v2.5-pro" };

const preferred = pickModels([xiaomi, openrouterClaude, glm], xiaomi, "glm-5.3-flash");
assert(preferred[0] === glm, "the model MEOW_NESTED_MODEL names is not picked first: " + JSON.stringify(preferred));

const unpref = pickModels([xiaomi, openrouterClaude, glm], xiaomi);
assert(unpref[0] === openrouterClaude, "a Claude model is not picked first without a preference: " + JSON.stringify(unpref));

assert(responseText({ content: " route " }).ok && responseText({ content: " route " }).text === "route", "a string content yields its text");
assert(responseText({ content: [{ type: "text", text: "route" }] }).text === "route", "a block list yields its text");
assert(!responseText({ stopReason: "error", errorMessage: "boom" }).ok, "an error message fails the model");
assert(!responseText(undefined).ok, "a missing message fails");

const calls = [];
const result = await answerWith([xiaomi, glm], async (m) => {
  calls.push(m.id);
  if (m === xiaomi) throw new Error("content.some is not a function");
  return "findings follow";
});
assert(result.ok && result.text === "findings follow", "a failing model is skipped and the next answers");
assert(calls.join() === "mimo-v2.5-pro,z-ai/glm-5.3-flash", "the candidates run in the picked order: " + calls.join());

const none = await answerWith([xiaomi], async () => {
  throw new Error("content.some is not a function");
});
assert(!none.ok, "a catalogue where every model throws answers not ok");
assert(none.reason.includes("xiaomi-token-plan-ams/mimo-v2.5-pro"), "the failure names its provider and model: " + none.reason);
assert(none.reason.includes("content.some is not a function"), "the failure names the reason: " + none.reason);

console.log("NODE OK");
"""


class FlowCommands(unittest.TestCase):
    def setUp(self):
        self.text = (FLOW / "extensions" / "flow.ts").read_text(encoding="utf-8")

    def test_each_command_maps_to_a_skill_that_exists(self):
        """TSK-5440 criterion 2: the skill file each command names exists."""
        for name, skill in FLOW_COMMANDS:
            with self.subTest(command=name):
                self.assertIn(
                    f'"{name}"', self.text,
                    f"/{name} is not registered",
                )
                self.assertTrue(
                    (FLOW / "skills" / skill / "SKILL.md").is_file(),
                    f"/{name} maps to skills/{skill}/SKILL.md, which is missing",
                )

    def test_each_command_sends_its_skill_into_the_session(self):
        """TSK-5440 criterion 1, REQ-4122: no handler ends at a notification."""
        handler = re.search(
            r"handler: async \(args, ctx\) => \{(.*?)\n      \},",
            self.text,
            re.S,
        )
        self.assertIsNotNone(handler, "the commands share no handler")
        body = handler.group(1)
        self.assertIn("pi.sendUserMessage(", body, "the handler sends nothing into the session")
        self.assertIn("SKILL.md", body, "the handler names no skill file")
        self.assertNotIn("Load the skill /", body, "the handler still tells the person to load a skill")

    def test_no_router_remains(self):
        """ADR-2930: the route is the session's act, and no dispatch is registered."""
        self.assertNotIn("meow-router", self.text, "the router tool is still registered")
        self.assertNotIn("route a request", self.text, "the router's description remains")

    def test_the_researcher_drafts_from_passed_material(self):
        """TSK-5480 criterion 3, REQ-3526: the nested call prefers the cheap tier."""
        self.assertIn('name: "meow-research"', self.text, "no researcher tool is registered")
        self.assertIn("MEOW_NESTED_MODEL", self.text, "the nested call reads no preference")
        self.assertIn('"glm-5.3-flash"', self.text, "the cheap tier is not the default")
        self.assertIn("templates/research.md", self.text, "the call carries no record template")


class LoopRun(unittest.TestCase):
    def setUp(self):
        self.text = (LOOP / "extensions" / "loop.ts").read_text(encoding="utf-8")

    def test_the_start_command_is_registered_and_reaches_the_runner(self):
        """TSK-5450 criterion 1: /meow-loop:run starts a run through `prompt`."""
        self.assertIn('pi.registerCommand("meow-loop:run"', self.text, "no run command is registered")
        block = self.text[self.text.index('pi.registerCommand("meow-loop:run"'):]
        self.assertIn('["prompt"]', block, "the command runs no prompt subcommand")
        self.assertIn('"UserPromptSubmit"', block, "the command names no hook event")
        self.assertIn("session_id: sessionId(ctx)", block, "the command names no session id")
        self.assertIn("cwd: ctx.cwd", block, "the command names no working directory")
        self.assertIn("pi.sendUserMessage(answer.additionalContext)", block, "the start context reaches no session")

    def test_other_input_reaches_the_runner(self):
        """TSK-5450 criterion 2: the person's next prompt ends a run `cancelled`."""
        block = self.text[self.text.index('pi.on("input"'):]
        self.assertIn('["prompt"]', block, "other input reaches no subcommand")
        self.assertIn('event.source === "extension"', block, "the extension's own messages are not excluded")
        self.assertIn('{ action: "continue" }', block, "the input is not let through")

    def test_the_settle_boundary_carries_the_frozen_prompt(self):
        """TSK-5450 criterion 3: `stop` decides, and a block continues once."""
        block = self.text[self.text.index('pi.on("agent_before_settle"'):]
        self.assertIn('["stop"]', block, "the boundary runs no stop subcommand")
        self.assertIn('event.outcome === "aborted"', block, "an escaped turn is not left alone")
        self.assertIn('answer.decision === "block"', block, "the boundary reads no block decision")
        self.assertIn('"custom_message"', block, "the frozen prompt enters as no message")
        self.assertIn("continue: true", block, "the boundary continues nothing")


class ProseReview(unittest.TestCase):
    def setUp(self):
        self.text = (PROSE / "extensions" / "prose.ts").read_text(encoding="utf-8")

    def test_the_reviewer_is_registered_with_the_bundled_standard(self):
        """TSK-5470 criterion 2, REQ-4618: the nested call inlines the standard."""
        self.assertIn('name: "meow-prose-review"', self.text, "no review tool is registered")
        self.assertIn("skills/writing/SKILL.md", self.text, "the call carries no standard")
        self.assertIn("skills/writing/patterns/en.md", self.text, "the call carries no patterns")
        self.assertIn("prompts/reply-shape.md", self.text, "the call carries no reply shape")

    def test_the_reviewer_runs_on_the_cheap_tier(self):
        """TSK-5470 criterion 2: glm 5.3 flash, or what MEOW_NESTED_MODEL names."""
        self.assertIn("MEOW_NESTED_MODEL", self.text, "the nested call reads no preference")
        self.assertIn('"glm-5.3-flash"', self.text, "the cheap tier is not the default")

    def test_the_claude_agent_runs_on_the_haiku_tier(self):
        """TSK-5470 criterion 1: the agent's model names the haiku tier."""
        front = (ROOT / "plugins" / "meow-prose" / "agents" / "prose.md").read_text(encoding="utf-8")
        self.assertRegex(front, r"(?m)^model: haiku$", "the prose agent names no haiku tier")


class Researcher(unittest.TestCase):
    def test_the_claude_agent_reads_and_writes_nothing(self):
        """TSK-5480 criterion 1: haiku, and no write tool."""
        front = (ROOT / "plugins" / "meow-flow" / "agents" / "researcher.md").read_text(encoding="utf-8")
        self.assertRegex(front, r"(?m)^model: haiku$", "the researcher names no haiku tier")
        tools = re.search(r"^tools: (.+)$", front, re.M).group(1)
        for tool in ("Write", "Edit", "NotebookEdit", "Bash"):
            self.assertNotIn(tool, tools, f"the researcher holds {tool}")

    def test_the_step_dispatches_and_writes_back(self):
        """TSK-5480 criterion 2: the step states the dispatch and the write-back."""
        step = (ROOT / "plugins" / "meow-flow" / "skills" / "method" / "steps" / "research.md").read_text(encoding="utf-8")
        self.assertIn("meow-flow:researcher", step, "the step dispatches no researcher")
        self.assertIn("meow-research", step, "the step names no Pi tool")
        self.assertIn("paw template research", step, "the step writes from no template")
        self.assertIn("paw check", step, "the step runs no check")


class StyleParity(unittest.TestCase):
    def test_every_bundled_reply_shape_carries_the_style(self):
        """TSK-5490 criterion 1, REQ-4108: the copies equal the style, modulo the path phrase."""
        style = STYLE.read_text(encoding="utf-8")
        adapted = style.replace(
            "block, from\n  `${CLAUDE_PLUGIN_ROOT}/output-styles/meow.md`, as it stands",
            "block, as it stands",
        )
        self.assertIn("R11", adapted, "the style carries no secrets rule to carry")
        for copy in sorted(ROOT.glob("packages/*/prompts/reply-shape.md")):
            with self.subTest(copy=str(copy.relative_to(ROOT))):
                self.assertEqual(
                    copy.read_text(encoding="utf-8"), adapted,
                    f"{copy.name} has drifted from the style the plugin ships",
                )


class ModelsModule(unittest.TestCase):
    def test_the_module_answers_across_providers_and_names_its_failure(self):
        """TSK-5470 criterion 3: the module's behaviour, driven by node."""
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as handle:
            handle.write(NODE_CHECK.replace("<file>", (PROSE / "lib" / "models.mjs").as_uri()))
            script = Path(handle.name)
        try:
            run = subprocess.run(
                ["node", "--input-type=module", "-e", f'await import({str(script.as_uri())!r})'],
                capture_output=True,
                text=True,
                timeout=60,
            )
        finally:
            script.unlink(missing_ok=True)
        self.assertEqual(run.returncode, 0, f"node reported: {run.stderr.strip() or run.stdout.strip()}")
        self.assertIn("NODE OK", run.stdout)


if __name__ == "__main__":
    unittest.main()