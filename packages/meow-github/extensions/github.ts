// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-github extension for Pi.
 *
 * Asks a person before a gh command changes how the repository is
 * governed, relaying the guard binary's decision (SPC-1300). Where there
 * is no one to ask, the command is denied.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

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

/** The permission decision a guard printed, or undefined where it stayed silent. */
function decision(stdout: string): { decision: string; reason: string } | undefined {
  const match = stdout.match(/"permissionDecision":\s*"(ask|deny)"/);
  if (!match) return undefined;
  const reason = stdout.match(/"permissionDecisionReason":\s*"((?:[^"\\]|\\.)*)"/);
  return { decision: match[1], reason: reason?.[1]?.replace(/\\n/g, "\n") ?? "" };
}

export default async function (pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  async function governance(command: string, ctx: { hasUI: boolean; ui: { confirm(q: string): Promise<boolean> } }): Promise<string | undefined> {
    if (!/\bgh\s/.test(command) || /\bgh\s+(?:api|auth|help|version)\b/.test(command)) {
      return undefined;
    }

    const { stdout } = await runGuard(
      join(binDir, "meow-github"), ["governance-guard"],
      { tool_name: "Bash", tool_input: { command } }, 10_000,
    );
    const asked = decision(stdout);
    if (asked?.decision !== "ask") return undefined;

    const allow = ctx.hasUI ? await ctx.ui.confirm(`${asked.reason}\n\nAllow?`) : false;
    if (allow) return undefined;
    return asked.reason;
  }

  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return undefined;

    const command = typeof event.input?.command === "string" ? event.input.command : "";
    const reason = await governance(command, ctx);
    if (reason === undefined) return undefined;
    return { block: true, reason };
  });

  pi.on("user_bash", async (event, ctx) => {
    const reason = await governance(event.command, ctx);
    if (reason === undefined) return undefined;
    return {
      result: { output: reason, exitCode: 126, cancelled: false, truncated: false },
    };
  });
}