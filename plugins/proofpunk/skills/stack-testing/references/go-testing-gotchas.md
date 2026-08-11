> Incorporated from the `golang-testing` skill (skills-ref.zip).

# Go Testing Gotchas

Claude knows basic Go testing (table-driven tests, subtests, benchmarks). This skill covers what Claude gets WRONG.

## When to Use

- Go tests passing locally but failing in CI (or vice versa)
- Data races detected only with `-race` flag
- Benchmarks producing misleading numbers
- Test cache causing stale results

## When NOT to Use

- Basic table-driven test structure (Claude knows this natively)
- Simple assertion patterns
- Non-Go testing

---

## Anti-Patterns (NEVER/WHY/Fix)

### 1. t.Parallel() with Loop Variable Capture
```go
// NEVER: Use t.Parallel() in range loop without capturing loop variable
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        got := fn(tt.input)  // tt is shared across goroutines!
        // All parallel subtests see the LAST value of tt
    })
}

// WHY: The loop variable `tt` is captured by reference. By the time
// parallel subtests execute, the loop has finished and tt points to
// the last element. All subtests test the same case.
// Fix: Shadow the loop variable (Go 1.22+ fixes this with loopvar, but
// many projects still target earlier versions)
for _, tt := range tests {
    tt := tt  // Shadow: captures current value
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        got := fn(tt.input)  // Safe: each goroutine has its own tt
    })
}
```

### 2. TestMain Forgetting os.Exit
```go
// NEVER: Use TestMain without calling os.Exit
func TestMain(m *testing.M) {
    setup()
    m.Run()  // Return value ignored!
    teardown()
}

// WHY: m.Run() returns the exit code from the test run. Without
// os.Exit(code), the test binary always exits 0 — even if tests FAIL.
// CI reports success when tests actually failed.
// Fix: Always exit with m.Run()'s return code
func TestMain(m *testing.M) {
    setup()
    code := m.Run()
    teardown()
    os.Exit(code)
}
```

### 3. Benchmark Without Resetting Timer
```go
// NEVER: Include setup time in benchmark measurements
func BenchmarkProcess(b *testing.B) {
    data := expensiveSetup()  // This time is included in benchmark!
    for i := 0; i < b.N; i++ {
        process(data)
    }
}

// WHY: The benchmark timer starts before your function body.
// Setup code inflates the reported ns/op, making the benchmark
// unreliable for comparison.
// Fix: Reset timer after setup
func BenchmarkProcess(b *testing.B) {
    data := expensiveSetup()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        process(data)
    }
}
```

### 4. Testing with == on Slices or Maps
```go
// NEVER: Compare slices or maps with == in tests
if got == want {  // Compile error for slices/maps

// Even for structs containing slices:
if got == want {  // Compiles but panics or gives wrong result
                  // if struct contains unexported fields

// WHY: Go's == doesn't work on slices/maps (compile error).
// For structs with unexported fields, reflect.DeepEqual may panic.
// Fix: Use go-cmp for robust comparison
import "github.com/google/go-cmp/cmp"

if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("mismatch (-want +got):\n%s", diff)
}
```

### 5. t.Fatal/t.FailNow Inside Goroutine
```go
// NEVER: Call t.Fatal, t.FailNow, or require.X inside a goroutine
go func() {
    result, err := asyncOp()
    require.NoError(t, err)  // PANIC: FailNow called from non-test goroutine
}()

// WHY: t.Fatal and t.FailNow call runtime.Goexit() which only works
// in the test's goroutine. Calling from another goroutine panics
// the entire test binary, not just the current test.
// Fix: Use channels to communicate errors back to test goroutine
errCh := make(chan error, 1)
go func() {
    _, err := asyncOp()
    errCh <- err
}()
require.NoError(t, <-errCh)  // Safe: runs in test goroutine
```

### 6. Ignoring -count=1 for Cache Busting
```go
// NEVER: Assume `go test` re-runs tests after code changes

// WHY: Go caches test results. If you change a file that isn't
// directly imported by the test package, `go test` returns
// "(cached)" and doesn't re-run. Environment variable changes
// are also invisible to the cache.
// Fix: Use -count=1 to force re-run
// go test -count=1 ./...
// Or: go clean -testcache
```

---

## Critical Go Test Behaviors

### Test Execution Order
- Tests within a package run sequentially by default
- `t.Parallel()` allows subtests to run concurrently
- Packages run in parallel by default (`-p` flag controls count)
- `TestMain` runs ONCE per package, not per test

### Race Detector
- `-race` enables the race detector (2-10x slower, 5-10x more memory)
- Race detector catches data races but NOT deadlocks
- Always run `-race` in CI: `go test -race ./...`
- Race detector has false negatives — passing doesn't prove race-free

### Fuzz Testing
- `f.Fuzz()` callback receives `*testing.T`, not `*testing.F`
- Corpus entries must match the fuzz function's parameter types exactly
- `go test -fuzz=FuzzName -fuzztime=30s` to run with time limit
- Fuzz failures are saved to `testdata/fuzz/` — commit these files

## CONFLICT: No-Mock Mandate

This project has a **no-mocking rule**. If your project CLAUDE.md says "NEVER write mocks/stubs/test files", use this skill only to understand existing Go test suites.

## APPLICABILITY GUARD

This skill applies to **Go 1.21+** projects. For Go 1.22+ with loopvar fix, the t.Parallel() capture issue is resolved but other patterns still apply.
