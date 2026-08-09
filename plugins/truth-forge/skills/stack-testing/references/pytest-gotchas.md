> Incorporated from the `python-testing` skill (skills-ref.zip).

# Pytest Gotchas & Edge Cases

Claude knows basic pytest. This skill covers what Claude gets WRONG.

## When to Use

- Debugging pytest fixture scope issues
- Async test failures with no clear cause
- Coverage reports showing unexpected gaps
- Parametrize tests behaving inconsistently

## When NOT to Use

- Basic pytest setup (Claude knows this natively)
- Writing simple test functions or assertions
- Non-Python testing frameworks

## CONFLICT: No-Mock Mandate

This project has a **no-mocking rule**. If your project CLAUDE.md says "NEVER write mocks/stubs/test files", this skill's patterns still apply to understanding existing test suites but you should NOT create new test files. Validate through real system interaction instead.

---

## Anti-Patterns (NEVER/WHY/Fix)

### 1. Fixture Scope Mismatch
```python
# NEVER: session-scoped fixture depending on function-scoped fixture
@pytest.fixture(scope="session")
def db(app):  # app is function-scoped by default!
    return app.db

# WHY: ScopeMismatch error. Higher-scoped fixtures cannot use lower-scoped ones.
# Fix: Match or widen the dependency's scope
@pytest.fixture(scope="session")
def db(app_factory):  # app_factory must also be session-scoped
    return app_factory().db
```

### 2. Mutable Fixture Data Shared Across Tests
```python
# NEVER: Return mutable object from module/session fixture without copy
@pytest.fixture(scope="module")
def config():
    return {"debug": True, "items": []}

# WHY: test_a appends to items[], test_b sees test_a's data. Order-dependent failures.
# Fix: Use function scope, or return a factory/deep copy
@pytest.fixture
def config():
    return {"debug": True, "items": []}
```

### 3. Forgetting `@pytest.mark.asyncio` Mode Configuration
```python
# NEVER: Mix asyncio modes without explicit config
@pytest.mark.asyncio
async def test_fetch():
    result = await fetch_data()

# WHY: pytest-asyncio v0.21+ defaults to "strict" mode. Tests silently skip
# or fail with "coroutine never awaited" if mode isn't set.
# Fix: Set mode explicitly in pyproject.toml
# [tool.pytest.ini_options]
# asyncio_mode = "auto"  # or "strict" with explicit marks
```

### 4. conftest.py in Wrong Directory
```python
# NEVER: Put conftest.py inside a package with __init__.py at root test level
# tests/__init__.py  <-- This breaks fixture discovery for some layouts
# tests/conftest.py

# WHY: __init__.py at test root changes Python's import resolution.
# Fixtures may not be found or conftest files may not load.
# Fix: Remove __init__.py from tests/ root (keep in subdirs if needed)
```

### 5. Parametrize ID Collisions
```python
# NEVER: Use parametrize with unhashable or duplicate string representations
@pytest.mark.parametrize("data", [{"a": 1}, {"a": 2}])
def test_dict(data): ...

# WHY: Both params produce id "data0", "data1" — fine. But nested parametrize
# with same param names silently overwrites. Also, dict params make ugly IDs.
# Fix: Always provide explicit ids
@pytest.mark.parametrize("data", [{"a": 1}, {"a": 2}], ids=["a-is-1", "a-is-2"])
```

### 6. yield Fixture Teardown Swallows Exceptions
```python
# NEVER: Assume teardown runs if fixture setup partially fails
@pytest.fixture
def resource():
    r = acquire()
    configure(r)  # If this raises, teardown below never runs
    yield r
    r.release()  # Never reached

# WHY: yield fixtures only run teardown if yield was reached.
# Fix: Use try/finally or addfinalizer
@pytest.fixture
def resource(request):
    r = acquire()
    request.addfinalizer(r.release)  # Always runs after acquire
    configure(r)
    return r
```

---

## Critical Pytest Behaviors

### conftest.py Resolution Order
1. pytest walks UP from test file to rootdir
2. Each conftest.py is loaded in directory order (parent before child)
3. Same-name fixtures in child conftest OVERRIDE parent
4. `conftest.py` must NOT be imported manually — pytest handles it

### Fixture Finalization Order
- Fixtures are torn down in LIFO order (reverse of creation)
- `yield` teardown runs even if test fails (but NOT if fixture setup fails before yield)
- `addfinalizer` callbacks run in reverse registration order

### Parametrize x Fixture Interaction
- `@pytest.mark.parametrize` creates separate test items at collection time
- Parametrized values are NOT available as fixtures — they're function args
- `indirect=True` routes parametrize values THROUGH a fixture:
  ```python
  @pytest.fixture
  def db(request):
      return connect(request.param)

  @pytest.mark.parametrize("db", ["sqlite", "pg"], indirect=True)
  def test_query(db): ...
  ```

### Coverage Gotchas
- `--cov` must point to the INSTALLED package, not the source directory, when using `src/` layout
- `--cov-branch` is OFF by default — line coverage hides untested branches
- Subprocess coverage requires `COVERAGE_PROCESS_START` env var and a `.pth` file
- `# pragma: no cover` on a function def line excludes the ENTIRE function body
