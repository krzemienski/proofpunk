# step-35 — what a single arm can and cannot close

Checked whether the direct `sdk_probe.py <probe>` invocation I used in
step-34 can advance P6, rather than assuming its output is interchangeable
with what the full surface produces.

## Schema: compatible

The single-arm artifact carries every key promotion reads:

    checks        present
    pass          present
    plugin_path   present

So the instrumentation IS validated by it. verification_block_run,
write_attempted, input_truncated and the rest are real readings from a real
session, and that is what step-34 claimed.

## Promotion: structurally impossible from one arm

promote_to_effect_proven needs three things a single probe cannot produce:

    base_verdict         from the BASE arm (cmd_slash_install), a different
                         probe with its own control
    counterfactual_json  a SEPARATE arm run against a plugin whose command
                         doc body is neutered
    scratch_plugin_dir   built by verify-command-surface, not by sdk_probe

Demonstrated rather than argued — fed the live arm to promotion directly:

    effect_proven: False
    reason: "counterfactual arm required but produced no parseable result
             (harness error) — cannot confirm the effect is attributable
             to the command doc"

It fails closed, correctly, for a reason unrelated to the checks.

## Scale of what P6 actually requires

    COMMANDS entries : 6
    arms             : 15  (base + control + effect + counterfactual)

One arm is 1/15 of the criterion. Step-34 said "one arm is not the surface";
this is the measurement behind that sentence.

## What still cannot be closed this way

- The full 15-arm criterion: needs verify-command-surface end to end.
- Model provenance: the live artifact confirmed NO model id is recorded.
  Fixing that is a capture change in sdk_probe's init handling, not
  something any number of arms reveals on its own.

## Standing conclusion
Step-34's claims were correctly scoped — it claimed instrumentation proven,
not promotion earned, and withheld the gate. This step confirms that scoping
was right for a reason I had not yet measured: the single-arm path cannot
reach promotion at all, so no amount of green from it could have justified
the promotion I briefly made.

VERDICT: single-arm runs validate instrumentation only. P6 stays UNVERIFIED
at 4/6 and needs the full 15-arm surface plus provenance capture.
