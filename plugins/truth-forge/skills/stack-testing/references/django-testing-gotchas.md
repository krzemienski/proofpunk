> Incorporated from the `django-tdd` skill (skills-ref.zip). **Adaptation:** This plugin enforces a no-mock Iron Rule: mock/stub chapters below are for UNDERSTANDING existing suites, not for writing new ones. New tests must run against the real system (real database, real server, real browser).

# Django Testing Gotchas

Claude knows basic pytest-django and DRF testing. This skill covers what Claude gets WRONG.

## When to Use

- Flaky Django tests (pass locally, fail in CI, or vice versa)
- factory_boy factories producing unexpected data
- DRF serializer tests with validation edge cases
- Database state leaking between test methods

## When NOT to Use

- Basic pytest assertions or Django model creation (Claude knows this natively)
- Non-Django Python testing (use `python-testing`)
- Frontend testing for Django templates

---

## Anti-Patterns (NEVER/WHY/Fix)

### 1. TestCase with Database-Level Triggers/Signals
```python
# NEVER: Use TestCase when testing code that relies on database triggers,
# constraints checked at COMMIT, or post_save signals with DB side effects
class TestOrderWorkflow(TestCase):  # Wraps in transaction
    def test_order_creates_invoice(self):
        order = Order.objects.create(...)
        # post_save signal fires BUT runs in same transaction
        # If signal does a separate DB query, it may see uncommitted data
        invoice = Invoice.objects.get(order=order)  # May fail!

# WHY: TestCase wraps each test in a transaction and rolls back at end.
# Deferred constraints, triggers, and signals that expect committed data
# see inconsistent state. Tests pass with SQLite but fail with Postgres.
# Fix: Use TransactionTestCase when testing commit-dependent behavior
class TestOrderWorkflow(TransactionTestCase):
    def test_order_creates_invoice(self):
        order = Order.objects.create(...)  # Actually commits
        invoice = Invoice.objects.get(order=order)  # Works
```

### 2. factory_boy SubFactory Creating Unexpected Related Objects
```python
# NEVER: Use SubFactory without understanding cascade creation
class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    user = factory.SubFactory(UserFactory)
    # Every OrderFactory() creates a NEW UserFactory too!

# WHY: 10 OrderFactory() calls create 10 users. Tests that assert
# User.objects.count() get unexpected numbers. Worse: if UserFactory
# has SubFactory(CompanyFactory), you get 10 companies too.
# Fix: Pass explicit related objects, or use LazyAttribute
order1 = OrderFactory(user=shared_user)
order2 = OrderFactory(user=shared_user)  # Same user

# Or use a shared fixture
@pytest.fixture
def user():
    return UserFactory()

def test_orders(user):
    order1 = OrderFactory(user=user)
    order2 = OrderFactory(user=user)
```

### 3. Forgetting --reuse-db Interaction with Migrations
```python
# NEVER: Use --reuse-db when schema has changed without regenerating
# pytest.ini: addopts = --reuse-db

# WHY: --reuse-db skips CREATE TABLE on subsequent runs. If you added
# a new field or model, the test DB still has the OLD schema.
# Tests fail with "column does not exist" but only in CI or after
# schema changes. Locally it works because you ran without --reuse-db once.
# Fix: Use --create-db after schema changes, or use --reuse-db
# with --migrations (not --nomigrations)
```

### 4. DRF Serializer .is_valid() Without raise_exception
```python
# NEVER: Call serializer.is_valid() without checking the return value
serializer = MySerializer(data=request.data)
serializer.is_valid()  # Returns False silently!
serializer.save()  # Crashes with AssertionError

# WHY: .is_valid() returns a boolean. Without raise_exception=True,
# invalid data is silently accepted and .save() crashes later with
# an unhelpful AssertionError instead of a clear validation error.
# Fix: Always use raise_exception=True in views
serializer.is_valid(raise_exception=True)
# Or check explicitly in tests
assert serializer.is_valid(), serializer.errors
```

### 5. Fixtures Loading in Wrong Order
```python
# NEVER: Depend on fixture loading order without explicit dependencies
# fixtures/users.json references company_id=1
# fixtures/companies.json defines company id=1
class TestSetup(TestCase):
    fixtures = ['users', 'companies']  # Users loaded FIRST!

# WHY: Fixtures load in list order. If users.json references a company
# that hasn't been loaded yet, you get IntegrityError (foreign key).
# Fix: Order fixtures by dependency (parents before children)
    fixtures = ['companies', 'users']  # Companies first
# Better: Use factory_boy instead of fixtures entirely
```

### 6. APIClient Without Authentication in Tests
```python
# NEVER: Test authenticated endpoints without setting up auth
def test_create_order(self):
    client = APIClient()
    response = client.post('/api/orders/', data={...})
    assert response.status_code == 201  # Gets 401 or 403!

# WHY: APIClient starts unauthenticated. DRF's default permission
# is IsAuthenticated. Test gets 401/403 and assertion fails with
# unhelpful "AssertionError: 403 != 201".
# Fix: Authenticate the client explicitly
def test_create_order(self, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/orders/', data={...})
```

---

## Critical Django Test Behaviors

### TestCase vs TransactionTestCase
- `TestCase` — wraps test in transaction, rolls back (fast, but no commit)
- `TransactionTestCase` — truncates tables after each test (slow, but real commits)
- Use `TestCase` for 95% of tests; `TransactionTestCase` only for commit-dependent code

### pytest-django Marks
- `@pytest.mark.django_db` — required for any test touching the database
- `@pytest.mark.django_db(transaction=True)` — equivalent to TransactionTestCase
- Without the mark, DB access raises `RuntimeError`

### factory_boy Gotchas
- `Sequence` starts at 0 and increments globally across ALL tests in a run
- `LazyAttribute` evaluates at build time, not at call time
- `create()` hits the database; `build()` does not (use build for speed)

## CONFLICT: No-Mock Mandate

This project has a **no-mocking rule**. If your project CLAUDE.md says "NEVER write mocks/stubs/test files", use this skill only to understand existing Django test suites. Do not create new test files.

## APPLICABILITY GUARD

This skill applies to **Django 4.x+ with pytest-django**. For Django with unittest-style TestCase only, some patterns differ (no marks, no fixtures parameter on functions).
