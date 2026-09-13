# step-21 — version and count sweep across every release surface

AGENTS.md names four surfaces that drift together on a release: package.json,
README.md, tools/INSTALL.md, and the build-site.py page sources. Swept all of
them plus both marketplace manifests.

## Versions: no drift

    plugins/proofpunk/package.json              4.0.0
    plugins/proofpunk/.claude-plugin/plugin.json 4.0.0
    plugins/proofpunk/.omp-plugin/plugin.json    4.0.0
    .claude-plugin/marketplace.json  (plugin + metadata)   4.0.0
    .omp-plugin/marketplace.json     (plugin + metadata)   4.0.0

    agree: True

tools/build-site.py carries ZERO hardcoded version literals — it reads
`marketplace["metadata"]["version"]`, so the site cannot drift from the
manifests by construction.

## Counts: three genuinely stale claims, fixed

    AGENTS.md:7                      "18 skills" -> 19
    plugins/proofpunk/AGENTS.md:8    "18 skills" -> 19
    plugins/proofpunk/AGENTS.md:27   "18 skill dirs" -> 19

Live tree: 19 skills (18 delivery + 1 router), 18 references.

## Two claims I checked and did NOT change

- README.md:102 — "prompt-forge gained its surface in v1.4.0/v1.5.0". A
  historical version note, correct as written.
- plugins/proofpunk/AGENTS.md:8 — "7 commands". Measured: commands/ holds
  exactly 7 (.md) and opencode/commands/ holds 7, so 7 and 14 are both live
  readings and verify-counts accepts either. Correct as written; an advisory
  suggested this was stale and the measurement says otherwise.

## A diagnostic of mine that failed
The first sweep script died on a Python SyntaxError (an f-string with a bare
brace). It produced no output at all, so nothing was concluded from it — but
worth recording: a broken measurement is not a passing one, and the fix was
to the script, never to the files it inspects.

## Gates

    verifiers 9/9 after the three edits

VERDICT: PASS — versions agree at 4.0.0 across all five manifests with no
hardcoded literals downstream; three stale count claims corrected; two
suspected-stale claims verified correct and left alone.
