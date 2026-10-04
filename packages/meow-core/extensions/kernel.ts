// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw kernel extension for Pi.
 *
 * Injects the reply shape into every model call, intercepts git and gh
 * commands for the prose gate, and resolves binary paths at session start.
 * Shells out to the meow-prose-gate wrapper, which resolves the
 * platform-specific meow binary at runtime.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");
const binDir = join(packageRoot, "bin");

/** Shell out to a binary and interpret its exit code. */
function runBinary(
  binary: string,
  args: string[],
  stdinInput?: string,
  timeout = 30_000,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
    if (stdinInput !== undefined) {
      child.stdin?.end(stdinInput);
    } else {
      child.stdin?.end();
    }
  });
}

/** Read a file relative to the Claude Code plugins directory. */
async function readPluginFile(plugin: string, ...segments: string[]): Promise<string> {
  const path = join(packageRoot, "..", "..", "plugins", plugin, ...segments);
  try {
    return await readFile(path, "utf-8");
  } catch {
    return "";
  }
}

/** Commands whose published text the prose gate checks. */
const PROSE_GATE_COMMANDS: ReadonlyArray<readonly [string, RegExp]> = [
  ["git commit", /\bgit\s+commit\b/],
  ["git -C", /\bgit\s+-C\b/],
  ["git -c", /\bgit\s+-c\b/],
  ["gh pr create", /\bgh\s+pr\s+create\b/],
  ["gh pr edit", /\bgh\s+pr\s+edit\b/],
  ["gh pr comment", /\bgh\s+pr\s+comment\b/],
  ["gh pr review", /\bgh\s+pr\s+review\b/],
  ["gh issue create", /\bgh\s+issue\s+create\b/],
  ["gh issue edit", /\bgh\s+issue\s+edit\b/],
  ["gh issue comment", /\bgh\s+issue\s+comment\b/],
  ["gh release create", /\bgh\s+release\s+create\b/],
  ["gh release edit", /\bgh\s+release\s+edit\b/],
  ["gh -R", /\bgh\s+-R\b/],
  ["gh --repo", /\bgh\s+--repo\b/],
];

function matchesProseGate(command: string): boolean {
  return PROSE_GATE_COMMANDS.some(([, pattern]) => pattern.test(command));
}

export default function (pi: ExtensionAPI) {
  let replyShape = "";
  let judgePrompt = "";

  /** Load prompt fragments at session start. */
  pi.on("session_start", async (_event, _ctx) => {
    replyShape = await readPluginFile("meow-core", "output-styles", "meow.md");
    judgePrompt = await readPluginFile("meow-prose-gate", "fragments", "judge.md");
  });

  /** Inject the reply shape into every model call. */
  pi.on("before_agent_start", async (event, _ctx) => {
    if (replyShape) {
      event.systemPromptOptions.guidelines?.push(replyShape);
    }
  });

  /**
   * Intercept git and gh commands for the prose gate.
   *
   * Shells out to the meow-prose-gate wrapper, which resolves the
   * platform-specific meow binary and runs `meow prose check`. The wrapper
   * handles the missing-binary case gracefully (reports unrun, exits 0).
   * Where the binary finds spans for the judge, the extension runs the
   * two-judge model call and blocks only where both judgements agree.
   */
  pi.on("user_bash", async (event, ctx) => {
    const command = typeof event.command === "string" ? event.command : "";
    if (!matchesProseGate(command)) return undefined;

    const { exitCode, stdout, stderr } = await runBinary(
      join(binDir, "meow-prose-gate"), ["check"], undefined, 120_000,
    );

    // Exit 0: the text is clean, or the binary was missing (unrun).
    if (exitCode === 0) return undefined;

    // Exit 2: a definite defect (stock idiom, hidden text).
    if (exitCode === 2) {
      const reason = stderr.trim() || stdout.trim() || "Prose gate: text fails a writing rule";
      return { result: { content: reason, details: undefined } };
    }

    // Non-zero with output: spans for the judge.
    if (stdout.trim() || stderr.trim()) {
      const spans = stdout.trim() || stderr.trim();

      if (!judgePrompt || !ctx.modelRegistry) return undefined;

      try {
        const [first, second] = await Promise.all([
          ctx.modelRegistry.streamSimple({
            messages: [
              { role: "system", content: replyShape },
              { role: "user", content: `${judgePrompt}\n\n<input>\n${spans}\n</input>` },
            ],
          }),
          ctx.modelRegistry.streamSimple({
            messages: [
              { role: "system", content: replyShape },
              { role: "user", content: `${judgePrompt}\n\n<input>\n${spans}\n</input>` },
            ],
          }),
        ]);

        const firstFindings = first.text.trim();
        const secondFindings = second.text.trim();

        if (firstFindings && secondFindings && firstFindings === secondFindings) {
          return {
            result: {
              content: `Prose gate: both judges agree — ${firstFindings}`,
              details: undefined,
            },
          };
        }

        return undefined;
      } catch {
        return undefined;
      }
    }

    // Any other non-zero: block.
    if (exitCode !== 0) {
      const reason = stderr.trim() || "Prose gate: check failed";
      return { result: { content: reason, details: undefined } };
    }

    return undefined;
  });
}
