// Proofpunk OMP extension — doctrine guard.
// Loaded via package.json `omp.extensions`. Registration-only at load time;
// runtime behavior runs from events (per oh-my-pi extension contract).
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Ask intent_verdict.py whether this session may stop, and return the block
 * reason if it may not. Returns undefined when the stop is allowed.
 *
 * The same procedure the shell stop guard runs (hooks/stop-guard.sh:284-302):
 * identity is session_id + cwd, and BOTH halves must match or one session's
 * verdict could authorize another's stop. An empty session_id fails CLOSED --
 * here the guard IS the check, so an unverifiable check is a failed check.
 */
async function intentBlockReason(
  sessionId: string | undefined,
  cwd: string | undefined,
): Promise<{ block: boolean; reason: string } | undefined> {
  // The interpreter this guard spawns. Named once so the spawn-failure
  // classifier can compare against the exact string that was executed,
  // rather than pattern-matching a basename and hoping.
  const INTERPRETER = "python3";
  if (!sessionId) {
    return { block: true, reason:
      "Proofpunk: a completion was claimed but this session has no session_id, " +
      "so its intent verdict cannot be identified. Without it, one session's " +
      "verdict could authorize another's stop. Record the verdict explicitly " +
      "with intent_verdict.py." };
  }
  const here = dirname(fileURLToPath(import.meta.url));
  const helper = join(
    here,
    "../skills/end-user-testing/scripts/intent_verdict.py",
  );
  if (!existsSync(helper)) {
    // Cannot verify, so cannot allow: same fail-closed posture as the shell
    // guard. Distinct from the python3-missing case, which fails OPEN there
    // because a stop must not hang on a missing interpreter.
    return { block: true, reason:
      "Proofpunk: a completion was claimed but the intent verdict helper is " +
      `missing (${helper}), so the original intent cannot be verified.` };
  }
  // Tagged outcome, not a bare number. Node puts a STRING in err.code for
  // spawn failures (ENOENT) and a NUMBER for a non-zero exit, so a
  // `typeof === "number"` test silently conflates "python3 is missing" with
  // "the helper said no". Those need opposite policies, so they are
  // classified explicitly.
  type Outcome =
    | { kind: "allow" }
    | { kind: "unmet" }
    | { kind: "missing-interpreter" }
    | { kind: "unrunnable"; detail: string };
  const { promise, resolve } = Promise.withResolvers<Outcome>();
  const child = execFile(
    INTERPRETER,
    // --consume: this guard re-fires on every settle pass, so each block must
    // spend an attempt or the session is held until the runtime's own
    // continuation cap (8) instead of reaching proofpunk's escalation at 3.
    [helper, "--session-id", sessionId, "--cwd", cwd ?? process.cwd(),
     "may-stop", "--consume"],
    { timeout: 5000 },
    (err) => {
      if (!err) return resolve({ kind: "allow" });
      // Narrow instead of asserting a shape: execFile's error carries `code`
      // as a string for spawn failures and a number for a non-zero exit, and
      // those need opposite policies.
      const code: unknown =
        typeof err === "object" && err !== null && "code" in err
          ? err.code
          : undefined;
      // Spawn failure. Keying the fail-open case on the ERRNO was wrong:
      // measured on Node 22, a python3 absent from PATH reports EACCES, not
      // ENOENT, while a bogus absolute path reports ENOENT. So an errno test
      // blocks the real "no interpreter" case and allows a typo'd one —
      // exactly backwards.
      //
      // The reliable signal is WHICH executable failed to spawn. Only a
      // spawn failure naming the interpreter may fail open; a failure naming
      // anything else, or naming nothing, blocks.
      if (typeof code === "string") {
        const missing: unknown =
          typeof err === "object" && err !== null && "path" in err
            ? err.path
            : undefined;
        const isInterpreter =
          typeof missing === "string" && missing === INTERPRETER;
        return resolve(
          isInterpreter
            ? { kind: "missing-interpreter" }
            : {
                kind: "unrunnable",
                detail: `${code} on ${typeof missing === "string" ? missing : "an unnamed path"}`,
              },
        );
      }
      if (typeof code === "number") {
        // The helper ran and answered. Exit 2 is its "may not stop".
        return resolve(code === 0 ? { kind: "allow" } : { kind: "unmet" });
      }
      // Timeout and signal kills land here: killed is set, code is not a
      // number. The check did not complete, so it did not pass.
      const signal: unknown =
        typeof err === "object" && err !== null && "signal" in err
          ? err.signal
          : undefined;
      const message: unknown =
        typeof err === "object" && err !== null && "message" in err
          ? err.message
          : undefined;
      return resolve({
        kind: "unrunnable",
        detail:
          typeof signal === "string"
            ? `killed by ${signal}`
            : typeof message === "string"
              ? message
              : String(code ?? "unknown failure"),
      });
    },
  );
  child.on("error", () =>
    resolve({ kind: "unrunnable", detail: "spawn error" }),
  );
  const outcome = await promise;

  // ONLY a verified exit 0 authorizes the stop.
  if (outcome.kind === "allow") return undefined;
  if (outcome.kind === "missing-interpreter") {
    // Same posture as stop-guard.sh:44-46: a stop must not hang because
    // python3 is absent, so this does NOT block. But that guard never fails
    // open silently — it emits "enforcement OFF" so an unchecked stop is
    // distinguishable from a clean one. Returning bare undefined here would
    // be exactly the silent fail-open the shell guard refuses.
    return { block: false, reason:
      "Proofpunk: intent-gate enforcement OFF (python3 not found). This stop " +
      "was NOT checked against the original intent." };
  }
  if (outcome.kind === "unrunnable") {
    return { block: true, reason:
      "Proofpunk: the intent-verification helper could not complete " +
      `(${outcome.detail}), so the completion claim cannot be checked against ` +
      "the original request. Fix the helper or downgrade the claim to UNVERIFIED." };
  }
  return { block: true, reason:
    "Proofpunk: the original intent for this session is not verified as met. " +
    "Re-read the request recorded at Stage 0, review the whole session against " +
    "it, and record a verdict with intent_verdict.py — or emit the fix prompt " +
    "and restart." };
}

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
  //
  // Reads event.messages, NOT ctx.session. ExtensionContext has no `session`
  // property (pi-coding-agent 18.1.18, extensibility/extensions/types.d.ts
  // :297-389 — ui, mode, cwd, sessionManager, model, isIdle(), never
  // session). The previous `(_ctx as { session?: unknown }).session ?? {}`
  // therefore evaluated to {} on every stop, JSON.stringify'd to "{}", and
  // matched no claim: the guard had never blocked anything. The session
  // transcript lives on SessionStopEvent.messages (shared-events.d.ts:83-86).
  pi.on("session_stop", async (event, ctx) => {
    const text = JSON.stringify(event?.messages ?? []).slice(-6000);
    const CLAIM =
      /\b(done|complete|completed|finished|shipped|works now|fixed it)\b/i;
    const PROOF =
      /(e2e-evidence\/|evidence-inventory|step-\d+[-.]|screenshot|verdict|curl\s+\S+\s+200|validate\s+OK)/i;
    const claimed = CLAIM.test(text);

    // The evidence guard does NOT re-fire on a continuation pass. Its
    // question ("is there a cited artifact?") is answered by the same
    // transcript, so re-asking would loop on an unchanged input until the
    // runtime's cap.
    if (claimed && !PROOF.test(text) && !event?.stop_hook_active) {
      return {
        continue: true,
        reason:
          "Proofpunk: a completion was claimed without a cited end-user evidence artifact. " +
          "Drive the real system as the end user, capture run-scoped evidence, cite it by full path — " +
          "or downgrade the claim to UNVERIFIED.",
      };
    }

    // Intent gate: even a fully evidenced claim may have proven the wrong
    // thing. The verdict is the model's judgment, recorded by
    // intent_verdict.py; this only enforces that one exists and says MET.
    // Procedure, never judgment quality.
    //
    // Scoped to the claim path on purpose. A turn that never claimed
    // completion has nothing to verify intent against, and gating it would
    // force a continuation on every ordinary stop.
    // The intent gate DOES re-fire. Its question ("was the original request
    // met?") has a changing answer: the continuation exists precisely so the
    // session can go meet it. Escaping on stop_hook_active would let an
    // UNMET session settle one turn later, which is not "keep working until
    // it actually implements" — it is one interruption and then silence.
    //
    // This does not loop: intent_verdict.py caps attempts at 3 and then
    // returns may-stop, so the gate stops blocking on its own. That bound
    // (3) is well inside the runtime's SESSION_STOP_CONTINUATION_CAP of 8
    // (agent-session.ts:385), so the escalation is reached before the
    // runtime ever intervenes.
    if (claimed) {
      const intent = await intentBlockReason(event.session_id, ctx?.cwd);
      if (intent?.block) return { continue: true, reason: intent.reason };
      if (intent && !intent.block) {
        // Enforcement is off, not passed. Say so where the operator sees it,
        // then allow the stop.
        ctx?.ui?.notify?.(intent.reason, "warning");
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
