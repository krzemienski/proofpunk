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

    // The write path never creates test artifacts (hard guarantee).
    if (event.toolName === "write" || event.toolName === "edit") {
      const path = String(input.path ?? input.file_path ?? "");
      const TEST_PATH =
        /(_?tests?_|__tests__|\.spec\.|\.test\.|\/tests?\/|\/test_|_test\.|\/fixtures?\/.*test|\/testing\/)/i;
      if (path && TEST_PATH.test(path)) {
        return {
          block: true,
          reason:
            "Blocked by Proofpunk doctrine guard: the write path never creates test files " +
            `(${path}). Validate by driving the real system as the end user. If the project ` +
            "has a pre-existing suite and the operator asked to extend it, let them run it manually.",
        };
      }
    }

    return undefined;
  });

  // Unproven-completion guard for the main session stop (cap 8 forced
  // continuations is the runtime's own guard against loops).
  pi.on("session_stop", async (_event, _ctx) => {
    const text = JSON.stringify(
      (_ctx as { session?: unknown }).session ?? {},
    ).slice(-6000);
    const CLAIM =
      /\b(done|complete|completed|finished|shipped|works now|fixed it)\b/i;
    const PROOF =
      /(e2e-evidence\/|evidence-inventory|step-\d+[-.]|screenshot|verdict|curl\s+\S+\s+200|validate\s+OK)/i;
    if (CLAIM.test(text) && !PROOF.test(text)) {
      return {
        continue: true,
        reason:
          "Proofpunk: a completion was claimed without a cited end-user evidence artifact. " +
          "Drive the real system as the end user, capture run-scoped evidence, cite it by full path — " +
          "or downgrade the claim to UNVERIFIED.",
      };
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
