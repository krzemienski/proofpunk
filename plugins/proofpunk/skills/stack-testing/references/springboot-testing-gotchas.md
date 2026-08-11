> Incorporated from the `springboot-tdd` skill (skills-ref.zip). **Adaptation:** This plugin enforces a no-mock Iron Rule: mock/stub chapters below are for UNDERSTANDING existing suites, not for writing new ones. New tests must run against the real system (real database, real server, real browser). Testcontainers chapters are the gold pattern here: real services in Docker.

# Spring Boot Testing Gotchas

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Anti-Patterns (NEVER/WHY/Fix)](#anti-patterns-neverwhyfix)
- [Critical Spring Test Behaviors](#critical-spring-test-behaviors)
- [CONFLICT: No-Mock Mandate](#conflict-no-mock-mandate)
- [APPLICABILITY GUARD](#applicability-guard)


Claude knows basic JUnit5/Mockito/MockMvc. This skill covers what Claude gets WRONG.

## When to Use

- Flaky Spring Boot tests in CI but passing locally
- Testcontainers lifecycle or startup failures
- `@Transactional` tests seeing stale or unexpected data
- Spring context loading failures or excessive context reloads

## When NOT to Use

- Basic JUnit5 assertion syntax (Claude knows this natively)
- Simple Mockito stubbing (Claude knows this natively)
- Non-Spring testing frameworks

---

## Anti-Patterns (NEVER/WHY/Fix)

### 1. @Transactional on Integration Tests with Async
```java
// NEVER: Use @Transactional on tests that trigger async operations
@SpringBootTest
@Transactional  // Rolls back at test end
class OrderServiceTest {
    @Test
    void createsOrder() {
        orderService.createOrder(req);  // Fires @Async event
        // Async handler runs in DIFFERENT thread — can't see
        // uncommitted transaction data. Handler sees empty DB.
    }
}

// WHY: @Transactional wraps the test thread's transaction. Async handlers,
// @EventListener, or @Scheduled run in separate threads that can't see
// the test's uncommitted data. Test passes if async is fast enough to
// complete before rollback; fails under load. Classic flaky test.
// Fix: Don't use @Transactional; clean up manually or use @DirtiesContext
@SpringBootTest
class OrderServiceTest {
    @Autowired JdbcTemplate jdbc;

    @AfterEach
    void cleanup() { jdbc.execute("DELETE FROM orders"); }
}
```

### 2. Testcontainers Without Reusable Flag
```java
// NEVER: Create new container per test class without reuse
@Container
static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16");

// WHY: Each test class starts a fresh container (5-15 seconds).
// With 50 test classes, that's 4-12 minutes of container startup alone.
// Fix: Use singleton pattern OR testcontainers.reuse.enable=true
// In ~/.testcontainers.properties:
// testcontainers.reuse.enable=true

@Container
static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16")
    .withReuse(true);
```

### 3. @MockBean Polluting Spring Context Cache
```java
// NEVER: Use @MockBean in multiple test classes with different mock targets
@SpringBootTest
class TestA {
    @MockBean UserService userService;  // Creates context variant A
}

@SpringBootTest
class TestB {
    @MockBean OrderService orderService;  // Creates context variant B
}

// WHY: Each unique combination of @MockBean creates a NEW Spring context.
// 10 test classes with different @MockBean sets = 10 context loads (30-60s each).
// This is the #1 cause of slow Spring Boot test suites.
// Fix: Consolidate mocks in a shared configuration, or avoid @MockBean
@TestConfiguration
class SharedMocks {
    @Bean UserService userService() { return mock(UserService.class); }
    @Bean OrderService orderService() { return mock(OrderService.class); }
}
```

### 4. @DirtiesContext on Every Test
```java
// NEVER: Use @DirtiesContext as a default cleanup strategy
@SpringBootTest
@DirtiesContext(classMode = ClassMode.AFTER_EACH_TEST_METHOD)
class EveryTestDirties { }

// WHY: Destroys and rebuilds the entire Spring context after EACH test.
// A context load takes 5-30 seconds. With 20 tests, that's 2-10 minutes
// of pure context rebuilding. Use ONLY as last resort.
// Fix: Clean up state explicitly instead
@AfterEach
void cleanup() {
    cacheManager.getCacheNames().forEach(n -> cacheManager.getCache(n).clear());
    jdbc.execute("TRUNCATE TABLE orders CASCADE");
}
```

### 5. MockMvc Without @AutoConfigureMockMvc
```java
// NEVER: Manually create MockMvc when using @SpringBootTest
@SpringBootTest
class ApiTest {
    MockMvc mockMvc = MockMvcBuilders.standaloneSetup(new MyController()).build();
    // Missing: filters, interceptors, error handlers, Spring Security

// WHY: Standalone setup skips the entire Spring web infrastructure.
// Security filters don't run, custom error handlers don't fire,
// content negotiation differs from production. Tests pass but
// production breaks.
// Fix: Use @AutoConfigureMockMvc for full web layer
@SpringBootTest
@AutoConfigureMockMvc
class ApiTest {
    @Autowired MockMvc mockMvc;  // Full infrastructure
}
```

### 6. WebTestClient Timeout on Reactive Endpoints
```java
// NEVER: Use default WebTestClient timeout for slow reactive chains
webTestClient.get().uri("/slow-endpoint")
    .exchange()
    .expectStatus().isOk();  // Fails with timeout after 5s

// WHY: Default WebTestClient timeout is 5 seconds. Reactive chains
// involving database calls, external APIs, or Testcontainers can
// take longer, especially in CI.
// Fix: Configure timeout explicitly
@AutoConfigureWebTestClient(timeout = "30s")
// OR
webTestClient.mutate().responseTimeout(Duration.ofSeconds(30)).build()
```

---

## Critical Spring Test Behaviors

### Context Cache Key
Spring caches application contexts by these properties:
- `@ActiveProfiles` value
- `@MockBean` / `@SpyBean` targets
- `@TestPropertySource` values
- `@ContextConfiguration` classes
- **Any difference creates a NEW context.** Minimize variation across test classes.

### @Sql Execution Order
- `@Sql` scripts run BEFORE `@BeforeEach` methods
- `@Sql(executionPhase = AFTER_TEST_METHOD)` runs AFTER `@AfterEach`
- Scripts in `@Sql` on class level run before EACH test method, not once

### Test Slice Annotations
- `@WebMvcTest` — loads ONLY web layer (controllers, filters, advisors)
- `@DataJpaTest` — loads ONLY JPA layer (repos, entities, Flyway/Liquibase)
- `@SpringBootTest` — loads EVERYTHING (slow but complete)
- **Mixing slices** (e.g., `@WebMvcTest` + `@DataJpaTest`) is NOT supported

## CONFLICT: No-Mock Mandate

This project has a **no-mocking rule**. If your project CLAUDE.md says "NEVER write mocks/stubs/test files", use this skill only to understand and debug EXISTING test suites. Do not create new test files.

## APPLICABILITY GUARD

This skill applies to **Spring Boot 3.x** with JUnit 5 projects. For Spring Boot 2.x, some annotations and behaviors differ (e.g., `@ExtendWith(SpringExtension.class)` is automatic in 3.x but required in 2.x).