// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-loop extension for Pi.
 *
 * Holds a run inside its own step and its own state: denies the Bash
 * command that would start a run from a session, and the write that would
 * touch a run's files, relaying the guard binary's decision (SPC-1300).
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

function filePathOf(event: { input?: { file_path?: unknown; path?: unknown } }): string | undefined {
  const filePath = event.input?.file_path ?? event.input?.path;
  return typeof filePath === "string" ? filePath : undefined;
}

export default async function (pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  pi.on("tool_call", async (event, _ctx) => {
    let reason: string | undefined;

    if (event.toolName === "bash") {
      const command = typeof event.input?.command === "string" ? event.input.command : "";
      const { stdout } = await runGuard(
        join(binDir, "meow-loop"), ["guard"],
        { tool_name: "Bash", tool_input: { command } }, 10_000,
      );
      const denied = decision(stdout);
      if (denied?.decision === "deny") reason = denied.reason;
    } else if (event.toolName === "edit" || event.toolName === "write") {
      const filePath = filePathOf(event);
      if (filePath !== undefined) {
        const { stdout } = await runGuard(
          join(binDir, "meow-loop"), ["guard"],
          { tool_name: event.toolName, tool_input: { file_path: filePath } }, 10_000,
        );
        const denied = decision(stdout);
        if (denied?.decision === "deny") reason = denied.reason;
      }
    }

    if (reason === undefined) return undefined;
    return { block: true, reason };
  });

  pi.on("user_bash", async (event, _ctx) => {
    const { stdout } = await runGuard(
      join(binDir, "meow-loop"), ["guard"],
      { tool_name: "Bash", tool_input: { command: event.command } }, 10_000,
    );
    const denied = decision(stdout);
    if (denied?.decision !== "deny") return undefined;
    return {
      result: { output: denied.reason, exitCode: 126, cancelled: false, truncated: false },
    };
  });
}