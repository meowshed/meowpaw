// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw kernel extension for Pi.
 *
 * Injects the reply shape into every model call, intercepts git and gh
 * commands for the prose gate, and resolves binary paths at session start.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");

/** Commands whose published text the prose gate checks. */
const PROSE_GATE_COMMANDS: ReadonlyArray<readonly [string, RegExp]> = [
  ["git commit", /\bgit\s+commit\b/],
  ["git commit (amend)", /\bgit\s+commit\s+--amend\b/],
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

/** Shell out to a native binary and interpret its exit code. */
function runBinary(
  binary: string,
  args: string[],
  timeout: number,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
  });
}

/** Read the reply shape from the Claude Code plugin's output style. */
async function readReplyShape(): Promise<string> {
  const path = join(packageRoot, "..", "..", "plugins", "meow-core", "output-styles", "meow.md");
  try {
    return await readFile(path, "utf-8");
  } catch {
    return "";
  }
}

/** Read the judge prompt fragment. */
async function readJudgePrompt(): Promise<string> {
  const path = join(packageRoot, "..", "..", "plugins", "meow-prose-gate", "fragments", "judge.md");
  try {
    return await readFile(path, "utf-8");
  } catch {
    return "";
  }
}

export default function (pi: ExtensionAPI) {
  let replyShape = "";
  let judgePrompt = "";
  let proseGateBinary = "";

  /** Resolve binary paths and load prompt fragments at session start. */
  pi.on("session_start", async (_event, _ctx) => {
    const platform = process.arch === "arm64" && process.platform === "darwin"
      ? "aarch64-apple-darwin"
      : `${process.arch}-${process.platform}`;

    proseGateBinary = join(packageRoot, "bin", platform, "meow-prose-gate");

    replyShape = await readReplyShape();
    judgePrompt = await readJudgePrompt();
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
   * Shells out to meow-prose-gate, which checks the text for stock idioms,
   * bold-open paragraphs and hidden text. Where the binary finds a span
   * that might be an idiom, acronym or bold-open, the extension runs the
   * two-judge model call and blocks only where both judgements agree.
   */
  pi.on("user_bash", async (event, ctx) => {
    const command = typeof event.command === "string" ? event.command : "";
    if (!matchesProseGate(command)) return undefined;

    // Shell out to the prose gate binary.
    const { exitCode, stdout, stderr } = await runBinary(proseGateBinary, ["check"], 120_000);

    // Exit 0: the text is clean. Pass through.
    if (exitCode === 0) return undefined;

    // Exit 2: the binary found a definite defect (stock idiom, hidden text).
    // Block and feed the reason to the model.
    if (exitCode === 2) {
      const reason = stderr.trim() || stdout.trim() || "Prose gate: text fails a writing rule";
      return { result: { content: reason, details: undefined } };
    }

    // Non-zero with output but not exit 2: the binary found spans for the
    // judge. Run the two-judge call and block only where both agree.
    if (exitCode !== 0 && (stdout.trim() || stderr.trim())) {
      const spans = stdout.trim() || stderr.trim();

      if (!judgePrompt || !ctx.modelRegistry) {
        // Cannot judge; report the finding as a warning and pass through.
        return undefined;
      }

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

        // Both judges report a finding on the same span: block.
        if (firstFindings && secondFindings && firstFindings === secondFindings) {
          return {
            result: {
              content: `Prose gate: both judges agree — ${firstFindings}`,
              details: undefined,
            },
          };
        }

        // Judges disagree or one finds nothing: pass through.
        return undefined;
      } catch {
        // Judge call failed; do not block on a failed check.
        return undefined;
      }
    }

    // Any other non-zero: block with the output as the reason.
    if (exitCode !== 0) {
      const reason = stderr.trim() || "Prose gate: check failed";
      return { result: { content: reason, details: undefined } };
    }

    return undefined;
  });
}
