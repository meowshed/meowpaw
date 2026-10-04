// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-prose-gate extension for Pi.
 *
 * Holds the prose gate over every publish command the model or the person
 * runs: the extension pipes the hook JSON to the gate binary and relays
 * its verdict, and the binary holds the judge itself (SPC-1300).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

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

/** Commands whose published text the prose gate checks. */
const PROSE_GATE_PATTERN =
  /\bgit\s+(?:-C\s+\S+\s+)?(?:-c\s+\S+=\S+\s+)?commit\b|\bgh\s+(?:pr\s+(?:create|edit|comment|review)|issue\s+(?:create|edit|comment)|release\s+(?:create|edit)|-R\b|--repo\b)/;

export default async function (pi: ExtensionAPI) {
  // The skills and this extension call the bundled wrapper by name.
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

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

    const command = typeof event.input?.command === "string" ? event.input.command : "";
    const reason = await proseGate(command);
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