// Proofpunk OpenCode plugin — doctrine guard.
// Install: ~/.config/opencode/plugin/proofpunk.ts (global) or
// .opencode/plugin/proofpunk.ts (project). Loaded at startup.
import type { Plugin } from "@opencode-ai/plugin";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * OpenCode 1.4.7 has NO stop hook. The whole Hooks interface (17 entries,
 * dist/index.d.ts:170-313) returns Promise<void>, and session.idle is an
 * Event reachable only through the generic `event` handler — which also
 * returns void and therefore cannot block.
 *
 * So enforcement lands where the runtime actually permits it: a throw from
 * tool.execute.before. That fires at the TOOL boundary, not at stop, which
 * means an unmet session is interrupted on its next tool call rather than
 * prevented from ending. Both seams are used:
 *   - session.idle  -> announce (observe-only, the runtime's design)
 *   - tool.execute.before -> throw (the only real block available)
 */
async function intentState(
  sessionId: string | undefined,
  cwd: string,
): Promise<{ block: boolean; reason: string } | undefined> {
  // Named once so the spawn-failure classifier compares against the exact
  // string executed, not a basename pattern.
  const INTERPRETER = "python3";
  // Fail CLOSED on an unusable check, matching the OMP guard and
  // stop-guard.sh:305-309. An earlier draft returned undefined on every
  // error path, which made the gate silently allow exactly when it was least
  // able to verify anything.
  if (!sessionId) {
    return {
      block: true,
      reason:
        "Proofpunk: this session has no sessionID, so its intent verdict " +
        "cannot be identified. Without it, one session's verdict could " +
        "authorize another's work.",
    };
  }
  const here = dirname(fileURLToPath(import.meta.url));
  const helper = join(
    here,
    "../../skills/end-user-testing/scripts/intent_verdict.py",
  );
  if (!existsSync(helper)) {
    return {
      block: true,
      reason:
        "Proofpunk: the intent verdict helper is missing " +
        `(${helper}), so the original intent cannot be verified. Reinstall ` +
        "the skills or downgrade the claim to UNVERIFIED.",
    };
  }
  const { promise, resolve } = Promise.withResolvers<
    { block: boolean; reason: string } | undefined
  >();
  const child = execFile(
    INTERPRETER,
    [helper, "--session-id", sessionId, "--cwd", cwd, "may-stop"],
    { timeout: 5000 },
    (err) => {
      if (!err) return resolve(undefined); // may stop
      const code: unknown =
        typeof err === "object" && err !== null && "code" in err
          ? err.code
          : undefined;
      // python3 absent is the ONE fail-open case, for the same reason
      // stop-guard.sh:44-46 exits early: a missing interpreter must not make
      // the tool surface unusable. Every other failure blocks.
      //
      // Spawn failure. Keying on the errno was wrong: measured on Node 22, a
      // python3 absent from PATH reports EACCES while a bogus absolute path
      // reports ENOENT — an errno test blocks the real case and allows the
      // typo. Only a spawn failure naming the exact interpreter fails open,
      // and it says so rather than going quiet. Same rule as the OMP guard.
      if (typeof code === "string") {
        const missing: unknown =
          typeof err === "object" && err !== null && "path" in err
            ? err.path
            : undefined;
        const isInterpreter =
          typeof missing === "string" && missing === INTERPRETER;
        if (isInterpreter) {
          // Fail OPEN, but never silently: a session that was never checked
          // must be distinguishable from one that passed.
          return resolve({
            block: false,
            reason:
              "Proofpunk: intent-gate enforcement OFF (python3 not found). " +
              "This session's work was NOT checked against its original intent.",
          });
        }
        return resolve({
          block: true,
          reason:
            "Proofpunk: the intent check could not run " +
            `(${code} on ${typeof missing === "string" ? missing : "an unnamed path"}), ` +
            "so intent cannot be verified against the original request.",
        });
      }
      if (typeof code === "number" && code !== 0) {
        return resolve({
          block: true,
          reason:
            "Proofpunk: the original intent for this session is not verified " +
            "as met. Re-read the request recorded at Stage 0, review the whole " +
            "session against it, and record a verdict with intent_verdict.py — " +
            "or emit the fix prompt and restart.",
        });
      }
      // Timeout, signal kill, or a non-numeric failure: the check did not
      // complete, so it did not pass.
      const signal: unknown =
        typeof err === "object" && err !== null && "signal" in err
          ? err.signal
          : undefined;
      return resolve({
        block: true,
        reason:
          "Proofpunk: the intent-verification helper could not complete " +
          `(${typeof signal === "string" ? `killed by ${signal}` : String(code ?? "unknown")}), ` +
          "so intent cannot be checked against the original request.",
      });
    },
  );
  child.on("error", () =>
    resolve({
      block: true,
      reason:
        "Proofpunk: the intent-verification helper could not be spawned, so " +
        "intent cannot be checked against the original request.",
    }),
  );
  return promise;
}

const DESTRUCTIVE_PATTERNS: RegExp[] = [
  /\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?-[a-zA-Z]*r[a-zA-Z]*\s+(\/|~|\$HOME|\.\.)/,
  /\bgit\s+push\b[^|]*--force\b[^|]*\b(main|master)\b/,
  />\s*\/dev\/sd[a-z]/,
  /\bmkfs\b/,
  /\bdd\s+.*of=\/dev\//,
];

const SECRET_PATH =
  /(^|\/)(\.env($|\.)|\.env\.[a-z]+$|credentials\.json$|secrets?\.(json|ya?ml|toml)$|id_rsa$|id_ed25519$)/;

/**
 * Read-only tools exempt from the intent gate: a blocked session must be able
 * to INSPECT in order to resolve its verdict. These cannot change anything,
 * so exempting them concedes no enforcement.
 */
const READ_ONLY_TOOLS: Record<string, true> = {
  read: true,
  grep: true,
  glob: true,
  list: true,
  todowrite: true,
  todoread: true,
};

/**
 * bash is NOT blanket-exempt. Blocking it entirely would wedge the session --
 * intent_verdict.py is invoked through bash, so the gate would make its own
 * resolution impossible. But exempting all of bash hands back an unbounded
 * bypass: a session could work indefinitely through it and never meet the
 * gate.
 *
 * So the exemption is per-command, not per-tool: only a bash command that is
 * actually resolving the verdict passes. Everything else hits the gate.
 *
 * Anchored deliberately. A bare substring test would exempt
 * `rm -rf build && echo intent_verdict.py`, because the token appears
 * ANYWHERE. The command must START with an optional interpreter followed by
 * the resolver script, and must contain no shell chaining, so a mutation
 * cannot ride along behind one.
 */
const RESOLVER_COMMAND =
  /^\s*(?:python3?\s+)?\S*(?:intent_verdict|fresh_evidence)\.py(?:\s|$)/;
const SHELL_CHAINING = /[;&|]|\$\(|`|\n/;

function isResolverCommand(command: string): boolean {
  if (SHELL_CHAINING.test(command)) return false;
  return RESOLVER_COMMAND.test(command);
}

export const Proofpunk: Plugin = async ({ client, directory }) => {
  // Announced once per session when idle finds an unmet intent, so the
  // observe-only seam does not spam every idle tick.
  const announced = new Set<string>();
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

      // Intent gate. This is the ONLY blocking seam OpenCode 1.4.7 offers.
      //
      // Exempt the tools a session needs in order to RESOLVE an unmet
      // verdict: blocking those would wedge the session permanently — it
      // could neither record a verdict nor read the fix prompt. bash is
      // exempt because intent_verdict.py is invoked through it.
      // bash is gated per-COMMAND: only a command that is actually resolving
      // the verdict is exempt, so ordinary shell work cannot evade the gate.
      const exempt =
        READ_ONLY_TOOLS[input.tool] ||
        (input.tool === "bash" &&
          isResolverCommand(String(output.args?.command ?? "")));
      if (!exempt) {
        const state = await intentState(input.sessionID, directory);
        if (state?.block) throw new Error(state.reason);
        // Fail-open is announced, never silent: a session that was never
        // checked must be distinguishable from one that passed. Logged once
        // per session so it does not repeat on every tool call.
        if (state && !state.block && !announced.has(input.sessionID)) {
          announced.add(input.sessionID);
          await client.app.log({
            body: {
              service: "proofpunk",
              level: "warn",
              message: state.reason,
            },
          });
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

      // Observe-only seam. session.idle cannot block — the event handler
      // returns void — so this announces and nothing more. Pairing it with
      // the tool-boundary throw is what makes the gate observable at the
      // moment a session goes quiet, instead of only on its next action.
      if (event.type === "session.idle") {
        const sessionID =
          typeof event.properties === "object" &&
          event.properties !== null &&
          "sessionID" in event.properties
            ? String(event.properties.sessionID)
            : undefined;
        if (sessionID && !announced.has(sessionID)) {
          const state = await intentState(sessionID, directory);
          if (state?.block) {
            announced.add(sessionID);
            await client.app.log({
              body: {
                service: "proofpunk",
                level: "warn",
                message:
                  "Proofpunk: this session is going idle with its original " +
                  "intent UNVERIFIED. " + state.reason,
              },
            });
          }
        }
      }
    },
  };
};
