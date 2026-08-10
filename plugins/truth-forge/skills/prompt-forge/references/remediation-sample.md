# Remediation Sample — a full RATE pass, end to end

This is what §2.1 looks like when executed, not described. Input:
`weather-tool.md`, invoked as `prompt-forge rate weather-tool.md`
(no flags — so the default file-output contract applies).

## 1. The input file (BEFORE)

```markdown
Write a Python function that gets the weather for a city.
It should handle errors and be fast. Use best practices.
```

## 2. Sequential thinking (0.1), abbreviated

1. Decompose: the prompt asks for code but defines no interface, no data
   source, no error taxonomy, no success metric.
2. Analyze: "handle errors" and "be fast" are unmeasurable; "best
   practices" is a placeholder for thought, not a constraint.
3. Branch: remediate as (a) XML-skeleton agentic prompt, or (b) plain
   markdown with sections. Pick (a) — the executor is an agent with
   tools, and the 0.5 skeleton is the default.
4. Verify: every deduction below cites a line from the BEFORE text.

## 3. Rating report (written to `weather-tool.rating.md`)

```markdown
## Prompt Rating — weather-tool
Overall: 34/100 — rewrite
| Dimension        | Score | Notes |
|------------------|-------|-------|
| Clarity          | 8/20  | "gets the weather" — which provider? which units? (line 1) |
| Specificity      | 3/15  | no function signature, no return shape (line 1) |
| Structure        | 2/15  | no tags/sections at all; 0.5 skeleton absent (lines 1-3) |
| Output contract  | 2/15  | "a function" — no name, params, types, or file target (line 1) |
| Edge-case cover  | 4/15  | "handle errors" names zero error cases (line 2) |
| Testability      | 0/10  | no success metric exists; "be fast" is unmeasurable (line 2) |
| Token efficiency | 15/15 | nothing wasted — because nothing is there |
## Failure modes predicted
- Executor invents a provider (or asks, stalling the run)
- "Errors" swallowed into a bare `except: pass`
- "Fast" rationalized as "it's one HTTP call"
## Test cases
1. city="London" -> typed result with temp_c, source, fetched_at
2. city="" -> ValueError naming the field, no network call
3. provider 500 -> WeatherFetchError after exactly 2 retries
4. city="Nowhereistan" -> CityNotFoundError, distinct from network failure
## Top 3 fixes, ordered by impact
1. Pin the output contract: signature, return type, file path
2. Enumerate the error taxonomy and per-case behavior
3. Replace "be fast" / "best practices" with measurable constraints
## Remediation: applied to weather-tool.remediated.md — re-scored 34/100 -> 91/100
```

## 4. The remediated file (written to `weather-tool.remediated.md`)

```markdown
<task>Implement get_weather(city: str) -> WeatherReport in
src/weather.py, fetching current conditions from the Open-Meteo API.</task>

<context>Python 3.12 project, httpx already a dependency, no API key
available — Open-Meteo is keyless. WeatherReport dataclass lives in
src/models.py: fields temp_c (float), condition (str), source (str),
fetched_at (datetime).</context>

<sequential_thinking>
1. Validate inputs before any network call.
2. Geocode the city, then fetch conditions — two calls, ordered.
3. Map provider JSON to WeatherReport; reject unknown fields.
4. Classify every failure into the taxonomy in <constraints> before raising.
</sequential_thinking>

<constraints>
- Error taxonomy: ValueError (empty/blank city, no network call made);
  CityNotFoundError (geocoding zero results); WeatherFetchError (HTTP
  error after exactly 2 retries, backoff 1s/2s).
- No bare except; no swallowed exceptions; no retries beyond the 2 stated.
- Total wall-clock budget per call: 5s timeout on each HTTP request.
- No new dependencies.
</constraints>

<output_contract>src/weather.py containing get_weather with the exact
signature above; returns WeatherReport; raises only the three taxonomy
errors. Public contract of src/models.py unchanged.</output_contract>

<validation>As the end user: run the four test cases from the rating
report against the real function with the real API (city="London",
city="", provider-500 via a local stub server, city="Nowhereistan") and
assert on actual return values / exception types. A green pytest suite is
REGRESSION evidence only, never validation.</validation>

<example>get_weather("London") ->
WeatherReport(temp_c=11.2, condition="overcast", source="open-meteo",
fetched_at=datetime(2026, 8, 11, 9, 0, tzinfo=timezone.utc))</example>
```

## 5. Re-score (AFTER) — 91/100, production-ready

| Dimension | Before | After | What changed |
|-----------|--------|-------|--------------|
| Clarity | 8 | 18 | provider, units, flow pinned |
| Specificity | 3 | 14 | exact signature, types, file path |
| Structure | 2 | 14 | 0.5 skeleton, balanced tags |
| Output contract | 2 | 14 | contract explicit, models.py stability named |
| Edge-case cover | 4 | 13 | three-case taxonomy with per-case behavior |
| Testability | 0 | 9 | four concrete test cases with expected results |
| Token efficiency | 15 | 9 | longer — the cost of saying something |

## 6. What the flags would have changed here

- `prompt-forge rate weather-tool.md --in-place` — `weather-tool.md`
  itself would have been replaced with the §4 content (consent via flag).
- `prompt-forge rate weather-tool.md --report-only` — only §3, no §4
  file; anything else would have violated 0.4.
- Had the AFTER score stayed at 64 (`needs-work`), delivery would have
  required `--ship-below-threshold` or an explicit "ship it" from the
  user — otherwise the report states what evidence is still missing.
