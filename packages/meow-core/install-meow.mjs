// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * Downloads the meow binary from the meow-full release.
 *
 * The meow binary is built once with every subcommand for six platforms and
 * published as the meow-full release; every meowpaw Pi package's installer
 * downloads the same archive, because a package bundles several units and
 * one unit's own release carries only its unit's feature (ADR-2790). This
 * script extracts the binary for the current machine and places it at
 * bin/<cpu>-<system>/meow, which is where the shell wrappers look for it.
 * Where the download fails, the wrappers report each check as unrun and
 * let the command through, so a failed download breaks nothing.
 */

import { createWriteStream, existsSync, mkdirSync, unlinkSync } from "node:fs";
import { chmod } from "node:fs/promises";
import { get } from "node:https";
import { arch, platform } from "node:os";
import { dirname, join } from "node:path";
import { execFileSync } from "node:child_process";

const RELEASE_BASE = "https://github.com/meowshed/meowpaw/releases/download";
const VERSION = "0.1.0";

function targetTriple() {
  const os = platform();
  const cpu = arch() === "arm64" || arch() === "aarch64" ? "aarch64" : "x86_64";
  const system =
    os === "darwin" ? "apple-darwin"
    : os === "linux" ? "unknown-linux-musl"
    : os === "win32" ? "pc-windows-msvc"
    : null;
  if (!system) {
    console.warn(`meowpaw: unsupported platform ${os}/${arch()}; skipping binary download`);
    process.exit(0);
  }
  return { triple: `${cpu}-${system}`, isWindows: os === "win32" };
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    mkdirSync(dirname(dest), { recursive: true });
    const file = createWriteStream(dest);
    const follow = (u) => {
      get(u, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          follow(res.headers.location);
          return;
        }
        if (res.statusCode !== 200) {
          file.end();
          reject(new Error(`HTTP ${res.statusCode} for ${url}`));
          return;
        }
        res.pipe(file);
        file.on("finish", () => file.close(resolve));
      }).on("error", reject);
    };
    follow(url);
  });
}

async function main() {
  const { triple, isWindows } = targetTriple();
  const scriptDir = dirname(new URL(import.meta.url).pathname);
  const binDir = join(scriptDir, "bin", triple);
  const exe = isWindows ? "meow.exe" : "meow";
  const dest = join(binDir, exe);

  if (existsSync(dest)) process.exit(0);

  const archiveUrl = `${RELEASE_BASE}/meow-full-v${VERSION}/meow-full-${VERSION}.zip`;
  const tmp = join(scriptDir, "bin", `.tmp-${triple}.zip`);
  console.log(`meowpaw: downloading the meow binary for ${triple} from meow-full v${VERSION}`);

  try {
    await download(archiveUrl, tmp);
    mkdirSync(binDir, { recursive: true });
    if (isWindows) {
      const inner = join(binDir, "extract");
      execFileSync("powershell", [
        "-NoProfile", "-Command",
        `Expand-Archive -Path '${tmp}' -DestinationPath '${inner}' -Force`,
      ], { stdio: "pipe" });
      const { renameSync, rmSync } = await import("node:fs");
      renameSync(join(inner, `meow-${triple}.exe`), dest);
      rmSync(inner, { recursive: true, force: true });
    } else {
      execFileSync("unzip", ["-jo", tmp, `meow-${triple}`, "-d", binDir], { stdio: "pipe" });
      // The archive names each binary with its target triple; the wrappers
      // look for a plain meow.
      const { renameSync } = await import("node:fs");
      renameSync(join(binDir, `meow-${triple}`), dest);
      await chmod(dest, 0o755);
    }
  } finally {
    try { unlinkSync(tmp); } catch { /* the download may have failed */ }
  }
}

main().catch((e) => {
  console.warn(`meowpaw: binary download failed (${e.message}); the shell wrappers will report unrun`);
  process.exit(0);
});
