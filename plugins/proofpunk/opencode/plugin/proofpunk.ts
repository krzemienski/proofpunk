// Proofpunk OpenCode plugin — doctrine guard.
// Install: ~/.config/opencode/plugin/proofpunk.ts (global) or
// .opencode/plugin/proofpunk.ts (project). Loaded at startup.
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

export const Proofpunk: Plugin = async ({ client }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        const command = String(output.args.command ?? "");
        for (const pattern of DESTRUCTIVE_PATTERNS) {
          if (pattern.test(command)) {
            throw new Error(
              "Blocked by Proofpunk doctrine guard: destructive command pattern " +
                `(${pattern.source}). If intentional, ask the operator to run it manually.`,
            );
          }
        }
      }
      if (input.tool === "read") {
        const path = String(output.args.filePath ?? output.args.path ?? "");
        if (SECRET_PATH.test(path)) {
          throw new Error(
            "Blocked by Proofpunk doctrine guard: refusing to read a likely secret file " +
              `(${path}). Credentials are referenced, never inlined.`,
          );
        }
      }

      // The write path never creates test artifacts (hard guarantee).
      if (input.tool === "write" || input.tool === "edit") {
        const wpath = String(output.args?.path ?? output.args?.file_path ?? "");
        const TEST_PATH =
          /(_?tests?_|__tests__|\.spec\.|\.test\.|\/tests?\/|\/test_|_test\.|\/fixtures?\/.*test|\/testing\/)/i;
        if (wpath && TEST_PATH.test(wpath)) {
          throw new Error(
            "Blocked by Proofpunk doctrine guard: the write path never creates test files " +
              `(${wpath}). Validate by driving the real system as the end user.`,
          );
        }
      }
    },

    event: async ({ event }) => {
      if (event.type === "session.created") {
        await client.app.log({
          body: {
            service: "proofpunk",
            level: "info",
            message:
              "Proofpunk loaded — end-user testing is the only PASS. Skills are shared from ~/.claude/skills.",
          },
        });
      }
    },
  };
};
