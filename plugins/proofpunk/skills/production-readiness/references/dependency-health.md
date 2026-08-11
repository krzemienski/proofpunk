> Incorporated from the `dependency-health` skill (skills-ref.zip).

# Dependency Health

## When to Use

- Running periodic dependency security audits
- Evaluating whether to adopt a new package
- Remediating CVEs in existing dependencies
- Hardening supply chain against typosquatting and hijacking

## When NOT to Use

- Application-level security review (use `security-scan`)
- Upgrading frameworks with breaking changes (use framework-specific skills)
- License-only compliance (use dedicated license scanning tools)


## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Ignore `npm audit` warnings because "they're all transitive" | Transitive deps execute with same privileges as direct deps | Audit all, override only after manual CVSS review |
| Pin exact versions without lockfile | Reproducible on your machine, not CI or teammates | Always commit lockfile (package-lock.json, yarn.lock, bun.lockb) |
| Auto-merge Dependabot PRs without review | Breaking changes, malicious version bumps, yanked packages | Review changelogs, check download counts, verify maintainer identity |
| Add packages with <100 weekly downloads for critical paths | High abandonment and hijack risk | Check `npm info` — maintainers, last publish date, download trend |
| Skip `--ignore-scripts` for untrusted packages | Install scripts can execute arbitrary code | Use `npm install --ignore-scripts` then manually verify postinstall |

## CVSS Quick Reference

| Score | Severity | Action |
|-------|----------|--------|
| 9.0-10.0 | Critical | Patch within 24 hours, consider rollback |
| 7.0-8.9 | High | Patch within 1 week |
| 4.0-6.9 | Medium | Patch in next sprint |
| 0.1-3.9 | Low | Track, patch at convenience |

## Audit Commands

```bash
# JavaScript/Node
npm audit --json | jq '.vulnerabilities | to_entries[] | select(.value.severity == "critical")'

# Python
pip-audit --desc
safety check

# Package reputation check
npm info <package> --json | jq '{maintainers, time, versions: (.versions | length)}'
```

## Supply Chain Hardening

1. **Lockfile integrity** — Use `npm ci` in CI (not `npm install`)
2. **Scope to trusted registries** — Use `.npmrc` to restrict registries
3. **Pin GitHub Actions** — Use commit SHAs, not tags: `uses: actions/checkout@<sha>`
4. **Review new maintainers** — If a package changes ownership, audit before updating
5. **Typosquatting check** — Verify package name spelling before install

## Package Evaluation Checklist

Before adding a new dependency:
- [ ] >1000 weekly downloads (or justified niche use)
- [ ] Last published within 12 months
- [ ] Multiple maintainers or org-owned
- [ ] License compatible (MIT, Apache-2.0, BSD)
- [ ] No known critical CVEs
- [ ] Bundle size acceptable (`bundlephobia.com`)
