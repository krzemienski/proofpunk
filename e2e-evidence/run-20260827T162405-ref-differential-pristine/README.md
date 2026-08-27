# run-20260827T162405-ref-differential-pristine

Before/after arms for improvement 3 (`--ref` reaching commits, not just branches).

## Capture method

Both arms were invoked directly from a shell with **no pipeline**:

```
HOME=$(mktemp -d) bash <installer> --target claude-code --source github \
  --ref e890bc527e9a8a8845bfb8ec40c3927a6238c86d --only proofpunk > step-NN.txt 2>&1
echo "RC=$?"
```

`step-01-OLD-pristine.txt` and `step-02-NEW-current.txt` are the raw redirected
stdout+stderr — they carry no header block, so the exit codes live in
`verdict.json` alongside `capture_method`. Redirection is not a pipeline: `$?`
is the installer's own status, not a downstream stage's.

Each arm ran under its own fresh `mktemp -d` HOME, so neither could observe or
contaminate the other's install tree.

## Old arm provenance

`git show e890bc5:tools/proofpunk-install.sh` — the committed installer, not a
reconstruction. Verified before use:

- `sha256` matches `git show` output byte-for-byte
  (`d39b31b40811f022de6a2c66e58db2b6376ad2f9ce6fbc1532741f3a5e4f2998`)
- `bash -n` clean
- contains the defect natively (`tar.gz/refs/heads` hardcoded)

This matters because two earlier arms in the same session were *reconstructed*
by editing the current script, and both failed silently — one died with
`unbound variable`, the other with a bash syntax error. Reconstructed arms are
not accepted as evidence here.

## Result

| Arm | rc | installed |
|-----|----|-----------|
| pristine old code | 1 | no |
| current code | 0 | yes |

Supersedes `run-20260827T151935-ref-differential`, whose old arm was a
reconstruction.
