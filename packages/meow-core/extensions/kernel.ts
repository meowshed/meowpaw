// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw kernel extension for Pi.
 *
 * Puts the package's bin wrappers on PATH, injects the reply shape into the
 * system prompt as the one extension that does, and holds the prose gate
 * over every publish command the model or the person runs. The gate binary
 * holds the judge itself: the extension pipes the hook JSON to it and
 * relays its verdict (SPC-1300, ADR-2790).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");
const binDir = join(packageRoot, "bin");
const promptsDir = join(packageRoot, "prompts");

/**
 * Run a guard binary with the hook JSON on standard input, which is the one
 * contract every meow guard reads: exit 0 allows, exit 2 blocks with its
 * reason on standard error.
 */
function runGuard(
  binary: string,
  args: string[],
  hookEvent: object,
  timeout: number,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
    child.stdin?.end(JSON.stringify(hookEvent));
  });
}

async function readPrompt(name: string): Promise<string> {
  try {
    return await readFile(join(promptsDir, name), "utf-8");
  } catch {
    return "";
  }
}

/** Commands whose published text the prose gate checks. */
const PROSE_GATE_PATTERN =
  /\bgit\s+(?:-C\s+\S+\s+)?(?:-c\s+\S+=\S+\s+)?commit\b|\bgh\s+(?:pr\s+(?:create|edit|comment|review)|issue\s+(?:create|edit|comment)|release\s+(?:create|edit)|-R\b|--repo\b)/;

function commandOf(event: { input?: { command?: unknown } }): string {
  const command = event.input?.command;
  return typeof command === "string" ? command : "";
}

export default async function (pi: ExtensionAPI) {
  // The skills call the bundled wrappers by name, and every other meowpaw
  // package's wrapper falls back to the meow binary itself (REQ-4144), so
  // put both the wrappers' directory and the platform binary's on PATH.
  const triple = `${process.arch === "arm64" || process.arch === "aarch64" ? "aarch64" : "x86_64"}-${
    process.platform === "darwin" ? "apple-darwin"
    : process.platform === "linux" ? "unknown-linux-musl"
    : process.platform === "win32" ? "pc-windows-msvc"
    : "unknown"}`;
  process.env.PATH = `${join(binDir, triple)}:${binDir}:${process.env.PATH ?? ""}`;

  // Load the bundled reply shape in the factory, so the first request
  // already holds it: print mode fires no session_start before its request.
  const replyShape = await readPrompt("reply-shape.md");

  if (!replyShape) {
    pi.on("session_start", (_event, ctx) => {
      ctx.ui?.notify?.(
        "meow-core: prompts/reply-shape.md is missing, so the reply shape was not injected",
        "warning",
      );
    });
  }

  pi.on("before_agent_start", async (event, _ctx) => {
    if (replyShape) {
      event.systemPromptOptions.promptGuidelines.push(replyShape);
    }
  });

  /** The prose gate's verdict for one command, or undefined to pass through. */
  async function proseGate(command: string): Promise<string | undefined> {
    if (!PROSE_GATE_PATTERN.test(command)) return undefined;

    const { exitCode, stderr, stdout } = await runGuard(
      join(binDir, "meow-prose-gate"), ["check"],
      { tool_name: "Bash", tool_input: { command } },
      120_000,
    );

    if (exitCode === 0) return undefined;
    return stderr.trim() || stdout.trim() || "Prose gate: text fails a writing rule";
  }

  // The model's publish commands.
  pi.on("tool_call", async (event, _ctx) => {
    if (event.toolName !== "bash") return undefined;

    const reason = await proseGate(commandOf(event));
    if (reason === undefined) return undefined;

    return { block: true, reason };
  });

  // A publish the person types with ! in front of it.
  pi.on("user_bash", async (event, _ctx) => {
    const reason = await proseGate(event.command);
    if (reason === undefined) return undefined;

    return {
      result: { output: reason, exitCode: 126, cancelled: false, truncated: false },
    };
  });
}
