> Incorporated from the `spec-compliance` skill (skills-ref.zip).

# Spec Compliance Auditor

## When to Use

- Starting any implementation task with a spec file
- Auditing whether prompts/instructions cover all spec requirements
- Ensuring no spec requirements are silently dropped during implementation
- Before running ralph or automated implementation loops

## When NOT to Use

- No spec file exists (write the spec first)
- Driving the running system as the end user (shared runbooks in `references/`, owned by `implement`'s validation phase)
- Code review against coding standards (use `code-review`)


## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Start implementing without checking spec coverage | Requirements get silently dropped | Run spec-compliance audit first; verify 100% coverage |
| Mark a requirement as "covered" by generic prompt text | False coverage; requirement may not actually get implemented | Each spec requirement needs a specific, traceable prompt instruction |
| Ignore non-functional requirements in specs | Performance, security, accessibility gaps ship to production | Treat NFRs as first-class requirements in coverage mapping |
| Update spec without re-running compliance check | Implementation and spec diverge silently | Re-audit after any spec change |

## Workflow

1. **Detect specs** — Find spec files in `./specs/` directory
2. **Extract items** — Parse every requirement, constraint, and acceptance criterion
3. **Map to prompt** — Match each spec item to PROMPT.md instructions
4. **Classify** — Mark each as COVERED, INCOMPLETE, or MISSING
5. **Report** — Generate coverage report with gaps highlighted
6. **Fix** — Add missing requirements to prompt/plan
7. **Verify** — Re-run audit to confirm 100% coverage

## Coverage Report Format

```markdown
## Spec Coverage Report

### Covered (8/10)
- [x] User authentication with OAuth
- [x] Role-based access control
...

### Gaps (2/10)
- [ ] Audit logging for admin actions (spec section 4.2)
- [ ] Data retention policy enforcement (spec section 5.1)

### Coverage: 80% — FAIL (100% required)
```
