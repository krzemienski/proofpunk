> Incorporated from the `eval` skill (skills-ref.zip). **Adaptation:** Requires the external Strands Evals SDK (pip install strands-evals); skip this reference if the SDK is unavailable and use eval-harness.md instead.

# EvalKit

Conversational evaluation framework for AI agents using Strands Evals SDK.

## When to Use

- Creating evaluations for AI agent behavior
- Measuring response quality across prompt variations
- Testing tool-use accuracy and reliability
- Benchmarking prompt changes before deployment

## When NOT to Use

- Unit testing application code (use language-specific test frameworks)
- Load/performance testing (use k6, Locust, etc.)
- UI testing (use Playwright or similar)


## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Use exact string matching for eval assertions | LLM outputs vary in wording; brittle tests | Use semantic similarity, rubric scoring, or LLM-as-judge |
| Evaluate on <20 test cases | Statistical noise dominates; unreliable results | Minimum 50 cases for meaningful signal; 200+ for production evals |
| Use the same model for generation and judging | Systematic bias; model favors its own outputs | Use a different/stronger model as judge, or use human eval |
| Skip baseline measurement before changes | No way to know if changes improved or regressed | Always measure current performance before modifying prompts |
| Test only happy paths | Edge cases are where agents fail most | Include adversarial inputs, ambiguous queries, and out-of-scope requests |

## Evaluation Types

| Type | Measures | Method |
|------|----------|--------|
| **Accuracy** | Correctness of factual claims | Ground truth comparison |
| **Relevance** | Stays on topic, addresses the question | Rubric scoring (1-5) |
| **Tool Use** | Correct tool selection and parameters | Exact match on tool calls |
| **Safety** | Refuses harmful requests, doesn't leak data | Red-team test suite |
| **Consistency** | Same input produces similar quality | Variance across N runs |

## Workflow

### 1. Plan Evaluation
Define what you're measuring and why:
```python
eval_plan = {
    "name": "Customer Support Agent v2",
    "hypothesis": "New prompt reduces hallucination rate by 30%",
    "metrics": ["accuracy", "relevance", "tool_use_precision"],
    "test_cases": 100,
    "baseline": "v1_results.json",
}
```

### 2. Generate Test Data
```python
from strands_evals import TestSuite

suite = TestSuite.from_examples([
    {"input": "What's my order status?", "expected_tool": "lookup_order", "context": {"order_id": "123"}},
    {"input": "Cancel my subscription", "expected_tool": "cancel_subscription"},
    # ... 98 more cases
])
```

### 3. Define Scoring Rubric
```python
rubric = {
    "accuracy": {
        5: "Completely correct, all facts verified",
        3: "Mostly correct, minor inaccuracies",
        1: "Major factual errors or hallucinations",
    },
    "relevance": {
        5: "Directly addresses the question with appropriate depth",
        3: "Addresses the question but includes irrelevant information",
        1: "Off-topic or doesn't answer the question",
    },
}
```

### 4. Execute and Analyze
```python
from strands_evals import Runner, LLMJudge

judge = LLMJudge(model="claude-sonnet-4-6", rubric=rubric)
results = await Runner(agent=my_agent, judge=judge).run(suite)

print(f"Accuracy: {results.mean('accuracy'):.2f} (baseline: {baseline.mean('accuracy'):.2f})")
print(f"Tool precision: {results.tool_precision:.1%}")
```

## Key Metrics

- **Mean score**: Average across all test cases per metric
- **P5 score**: Bottom 5th percentile — worst-case performance
- **Tool precision**: Correct tool calls / total tool calls
- **Regression rate**: % of cases that scored lower than baseline
