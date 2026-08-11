// truth-forge OpenCode plugin — doctrine guard.
// Install: ~/.config/opencode/plugin/truth-forge.ts (global) or
// .opencode/plugin/truth-forge.ts (project). Loaded at startup.
import type { Plugin } from "@opencode-ai/plugin";

const DESTRUCTIVE_PATTERNS: RegExp[] = [
  /\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?-[a-zA-Z]*r[a-zA-Z]*\s+(\/|~|\$HOME|\.\.)/,
  /\bgit\s+push\b[^|]*--force\b[^|]*\b(main|master)\b/,
  />\s*\/dev\/sd[a-z]/,
  /\bmkfs\b/,
  /\bdd\s+.*of=\/dev\//,
];

const SECRET_PATH =
  /(^|\/)(\.env($|\.)|\.env\.[a-z]+$|credentials\.json$|secrets?\.(json|ya?ml|toml)$|id_rsa$|id_ed25519$)/;

export const TruthForge: Plugin = async ({ client }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        const command = String(output.args.command ?? "");
        for (const pattern of DESTRUCTIVE_PATTERNS) {
          if (pattern.test(command)) {
            throw new Error(
              "Blocked by truth-forge doctrine guard: destructive command pattern " +
                `(${pattern.source}). If intentional, ask the operator to run it manually.`,
            );
          }
        }
      }
      if (input.tool === "read") {
        const path = String(output.args.filePath ?? output.args.path ?? "");
        if (SECRET_PATH.test(path)) {
          throw new Error(
            "Blocked by truth-forge doctrine guard: refusing to read a likely secret file " +
              `(${path}). Credentials are referenced, never inlined.`,
          );
        }
      }
    },

    event: async ({ event }) => {
      if (event.type === "session.created") {
        await client.app.log({
          body: {
            service: "truth-forge",
            level: "info",
            message:
              "truth-forge loaded — end-user testing is the only PASS. Skills are shared from ~/.claude/skills.",
          },
        });
      }
    },
  };
};
