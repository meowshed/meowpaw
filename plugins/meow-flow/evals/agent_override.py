#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The hand-run case TSK-4955 criterion 1 asks for (REQ-2986): a fixture repository defines in `.claude/agents/`
an agent under the name of one this unit ships, with a body of its own, and a session with the unit loaded
dispatches the agent by the name the unit's steps use, `meow-flow:<name>`, and then by the bare name. The run
reads which agent answered from the reply, and prints, for each name, whether the repository's definition was
the one dispatched. It exits 1 on any dispatch the repository's definition didn't answer. Every run calls a
model, so no gate or workflow runs this:

    python3 plugins/meow-flow/evals/agent_override.py [model] [agent...]

The model defaults to `sonnet`, and the agents to every one under this unit's `agents/`.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent


def planted(name):
    marker = f"PLANTED-{name.upper()}"
    text = (f"---\nname: {name}\ndescription: The repository's own {name}, which answers with one word.\n"
            f"tools: []\nmaxTurns: 1\nmodel: haiku\neffort: low\nomitClaudeMd: true\nskills: []\n---\n\n"
            f"Reply with exactly the word {marker} and nothing else, whatever you are asked.\n")
    return marker, text


def answers(stream):
    """Each Agent call's input, with the text its result returned."""
    calls, results = {}, {}
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for block in event.get("message", {}).get("content", []) or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
                calls[block["id"]] = block.get("input", {})
            if block.get("type") == "tool_result":
                content = block.get("content")
                results[block.get("tool_use_id")] = json.dumps(content)
    return [(calls[k], results.get(k, "")) for k in calls]


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "sonnet"
    agents = sys.argv[2:] or [p.stem for p in sorted((UNIT / "agents").glob("*.md"))]
    misses = 0
    total = 0
    for agent in agents:
        marker, text = planted(agent)
        for name in (f"meow-flow:{agent}", agent):
            prompt = (f"Dispatch the agent named exactly `{name}` once, with the prompt `Say hello.`, and then "
                      "print its reply verbatim. Do nothing else.")
            with tempfile.TemporaryDirectory() as repository:
                Path(repository, ".claude", "agents").mkdir(parents=True)
                Path(repository, ".claude", "agents", f"{agent}.md").write_text(text)
                subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
                start = time.time()
                done = subprocess.run(
                    ["claude", "-p", prompt, "--model", model, "--plugin-dir", str(UNIT),
                     "--output-format", "stream-json", "--verbose", "--max-turns", "4"],
                    cwd=repository, capture_output=True, text=True, timeout=600)
            calls = answers(done.stdout)
            used = ", ".join(c.get("subagent_type", "?") for c, _ in calls) or "none"
            ours = any(marker in result for _, result in calls)
            total += 1
            misses += not ours
            print(f"{model} {name}: dispatched {used}, answered by "
                  f"{'the repository' if ours else 'not the repository'}, exit {done.returncode}, "
                  f"{time.time() - start:.0f}s", flush=True)
    print(f"\n{total - misses} of {total} dispatches answered by the repository's definition")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
