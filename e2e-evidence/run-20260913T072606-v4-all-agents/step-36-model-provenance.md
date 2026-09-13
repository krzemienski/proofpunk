# step-36 — the model was never missing; the probe discarded it

## What the audit assumed

Step-26 found `ClaudeAgentOptions.model` is never set and no model id
appears in any artifact, and concluded provenance was absent. I treated the
fix as "pin the model AND widen the capture", with the second half framed as
recording something the SDK might not expose.

Wrong diagnosis of the cause. The model was in the init payload all along.

## What the payload actually carries

    init_keys (24): agents, analytics_disabled, apiKeySource, capabilities,
    claude_code_version, cwd, fast_mode_disabled_reason, fast_mode_state,
    mcp_servers, memory_paths, messaging_socket_path, MODEL, output_style,
    permissionMode, plugins, product_feedback_disabled, session_id, skills,
    slash_commands, subtype, terminal_slash_commands, tools, type, uuid

sdk_probe's SystemMessage handler read `data` and kept THREE hand-picked
fields, discarding the other 21 — including `model`. The 77KB artifact with
"zero model strings" was this probe throwing provenance away, not the SDK
withholding it.

Live confirmation:

    model : cc/claude-opus-5

## Both halves now recorded

    model               what the session resolved
    model_requested     what was asked for (None = CLI chose)
    model_pinned        whether a pin was requested
    model_pin_honoured  whether resolution matched the request
    init_keys           every field the payload carried

`model_pin_honoured` is the one that earns its place: a silently-ignored
pin would otherwise be indistinguishable from a successful one. And
init_keys means a future `model: null` is a PROVEN absence rather than an
artifact of whatever filter the probe happens to apply.

## Pinning

`--model` is opt-in. Unpinned runs still record the resolved model, so
attribution never depends on remembering the flag — the failure mode that
made every prior P6 arm unattributable.

Verified on a real arm, not by inspection:

    rc=0  pass=True
    requested cc/claude-opus-5 -> recorded cc/claude-opus-5, honoured True

## Lesson, and it is the session's lesson again

"No model id anywhere in the artifact" was a true observation with a false
implied cause. I reported it three times — steps 26, 27, 34 — each time
correctly as an absence, each time implying the SDK was the reason. One
command against the live payload would have shown the truth at any point.

Absence of evidence in an artifact says something about the CAPTURE before
it says anything about the source. That is the same error class as the
truncation reading (step-32) and the 0/6 replay (step-29), now for the
third time.

## Status
P6's gating blocker is closed: arms are attributable and pinnable. The
criterion itself still needs the full 15-arm surface (step-35), and
verification_block_run still needs a non-errored arm to be promoted.

VERDICT: provenance recorded and pinning proven live. P6 remains UNVERIFIED
at 4/6, but its central unknown is no longer unknown.
