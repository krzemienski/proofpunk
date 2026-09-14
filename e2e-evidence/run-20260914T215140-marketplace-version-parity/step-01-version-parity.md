# Marketplace version parity is now guarded
utc : 2026-09-14T21:51:40.825048Z
HEAD: 15cc983

## Measured state BEFORE writing the check

    plugins/proofpunk/package.json   : 4.0.0
    .claude-plugin/marketplace.json  : ['4.0.0', '4.0.0']
    .omp-plugin/marketplace.json     : ['4.0.0', '4.0.0']
    .claude-plugin/plugin.json       : absent
    .omp-plugin/plugin.json          : absent

No drift today. This is NOT a bug fix — it is a guard against a recurrence,
and the distinction is stated rather than blurred: AGENTS.md names
version-string drift across package.json/README/INSTALL.md as a RECURRING
release defect, and these four fields were unguarded. That is exactly the
shape of the skill-count bug fixed in 15cc983, where every prose source was
correct and the only wrong copy was the one no gate could see.

Note the earlier advisory said marketplace.json declares its version "in two
places"; measured, it is two per catalog across two catalogs — four fields.
The check walks the JSON recursively rather than reading two known keys, so a
third declaration added later is covered without another edit.

## Fix

check_marketplace_counts() now also compares every `version` field found
anywhere in either catalog against plugins/proofpunk/package.json.

## Mutation test — BOTH fields, independently

    metadata.version   -> 3.9.9   gate rc=1
        ".claude-plugin/marketplace.json: declares version 3.9.9
         but package.json is 4.0.0"
    plugins[0].version -> 3.9.9   gate rc=1   (same message)
    restored                      gate rc=0

Each field was mutated ALONE, because a check that only caught one of them
would pass a test that mutated both. Catalogs confirmed byte-identical to HEAD
afterwards via `git diff --stat` (empty).

All 14 gates rc=0, captured unpiped.
