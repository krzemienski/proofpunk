# Does the seal fix wedge any committed run? — MEASURED
utc : 2026-09-14T21:49:26.233406Z
HEAD: 7dac20f

An advisory flagged the one way 7dac20f could wedge the repo: if any COMMITTED
run already has a step file whose on-disk digest differs from its recorded
inventory line, `seal` would now refuse that run permanently.

Measured across every committed inventory (git ls-files, not a glob — an
untracked run is not shipped state):

    committed inventories        : 61
    v2-sealed and CLEAN          : 52
    v2-sealed and MUTATED        :  0     <- nothing is wedged
    legacy (pre-v2, no digests)  :  9

Legacy runs are structurally unaffected: cmd_seal only compares rows it can
parse as `name size sha256`, and legacy inventories contain none.

## The three cases the advisory demanded, all driven

    (a) ADD a new step, re-seal        seal rc=0  validate rc=0
    (c) RE-SEAL UNCHANGED              seal rc=0  validate rc=0   [was untested]
    (b) MODIFY a sealed step, re-seal  seal rc=2  REFUSED

(c) was the gap: I had proven append and tamper but never the idempotent
re-seal, which is the most common operation of the three. It passes.

The implemented rule is exactly the one specified: an ALREADY-RECORDED
artifact's digest may not change; new step files may be added and sealed
freely. Not "refuse any re-seal", which would have broken the normal path.

## On the layering objection

One advisory argued re-seal-after-edit validating clean is correct by design,
since verify-evidence-immutability.py owns immutability by diffing committed
captures against HEAD blobs. That layer is real and unchanged — but it can only
see a run AFTER it is committed. The mutation the v4 report disclosed happened
BEFORE commit, in-run, and produced a run that validated clean. Both layers are
needed; this closes the earlier one.
