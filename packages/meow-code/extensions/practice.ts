// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw practice extension for Pi.
 *
 * Resolves binary paths at session start. The practice layer's behaviour is
 * carried by its skills (change, debug, write, header); the extension adds
 * only the reply shape injection for nested calls.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");

async function readPluginFile(plugin: string, ...segments: string[]): Promise<string> {
  const path = join(packageRoot, "..", "..", "plugins", plugin, ...segments);
  try {
    return await readFile(path, "utf-8");
  } catch {
    return "";
  }
}

export default function (pi: ExtensionAPI) {
  let replyShape = "";

  pi.on("session_start", async (_event, _ctx) => {
    replyShape = await readPluginFile("meow-core", "output-styles", "meow.md");
  });

  pi.on("before_agent_start", async (event, _ctx) => {
    if (replyShape) {
      event.systemPromptOptions.guidelines?.push(replyShape);
    }
  });
}
