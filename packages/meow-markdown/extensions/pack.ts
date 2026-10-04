// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw pack extension for Pi.
 *
 * Puts the package's bin wrapper on PATH so the skill can call it by name,
 * the way Claude Code does natively for a plugin's bin/. The pack's
 * behaviour is carried by its skill; the kernel carries the reply shape.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

export default function (_pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;
}
