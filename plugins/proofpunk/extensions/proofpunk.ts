// Proofpunk OMP extension — doctrine guard.
// Loaded via package.json `omp.extensions`. Registration-only at load time;
// runtime behavior runs from events (per oh-my-pi extension contract).
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

const DESTRUCTIVE_PATTERNS: RegExp[] = [
  /\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?-[a-zA-Z]*r[a-zA-Z]*\s+(\/|~|\$HOME|\.\.)/, // rm -rf at root/home/parent
  /\bgit\s+push\b[^|]*--force\b[^|]*\b(main|master)\b/, // force-push to main
  /\bgit\s+reset\s+--hard\b[^|]*&&/, // chained hard reset
  />\s*\/dev\/sd[a-z]/, // raw disk write
  /\bmkfs\b/,
  /\bdd\s+.*of=\/dev\//,
];

const SECRET_PATH = /(^|\/)(\.env($|\.)|\.env\.[a-z]+$|credentials\.json$|secrets?\.(json|ya?ml|toml)$|id_rsa$|id_ed25519$)/;

export default function proofpunk(pi: ExtensionAPI) {
  pi.setLabel("Proofpunk doctrine guard");

  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify(
      "Proofpunk loaded — end-user testing is the only PASS. Run /proofpunk:implement to start a build.",
      "info",
    );
  });

  pi.on("tool_call", async (event) => {
    const input = (event.input ?? {}) as Record<string, unknown>;

    if (event.toolName === "bash") {
      const command = String(input.command ?? "");
      for (const pattern of DESTRUCTIVE_PATTERNS) {
        if (pattern.test(command)) {
          return {
            block: true,
            reason:
              "Blocked by Proofpunk doctrine guard: destructive command pattern " +
              `(${pattern.source}). If this is intentional, ask the operator to run it manually.`,
          };
        }
      }
    }

    if (event.toolName === "read") {
      const path = String(input.path ?? input.file_path ?? "");
      if (SECRET_PATH.test(path)) {
        return {
          block: true,
          reason:
            "Blocked by Proofpunk doctrine guard: refusing to read a likely secret file " +
            `(${path}). Credentials are referenced, never inlined.`,
        };
      }
    }

    return undefined;
  });

  pi.registerCommand("proofpunk", {
    description: "Show Proofpunk doctrine status",
    handler: async (_args, ctx) => {
      ctx.ui.notify(
        "Doctrine: tasks execute to completion · validation = end-user testing that proves something · no mocks · evidence over assertion.",
        "info",
      );
    },
  });
}
