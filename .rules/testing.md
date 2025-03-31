# Testing Guidelines for ATLAS Project

This document outlines the testing standards and best practices for the ATLAS project, with a focus on ensuring the reliability and correctness of our durable workflow execution architecture using Temporal.

## Testing Principles

1. **Test Determinism:** Like our workflows, our tests must be deterministic and produce the same results on each run.
2. **Test Isolation:** Each test should run independently of others without shared state.
3. **Workflow-Activity Separation:** Test workflows and activities separately to ensure proper separation of concerns.
4. **Complete Coverage:** Ensure all critical paths, error cases, and compensation logic are tested.
5. **Realistic Simulation:** Tests should simulate actual runtime conditions, including failures and delays.

## How to Write Tests

### General Process

1. **Identify Test Scope:**
   * Determine if you're testing a workflow, activity, API endpoint, or UI component.
   * Define the specific behavior or functionality to test.
   * Consider both the happy path and error scenarios.

2. **Setup Test Environment:**
   * For workflow tests: Use Temporal's testing framework to mock the Temporal server.
   * For activity tests: Create isolated test doubles for external dependencies.
   * For API tests: Use FastAPI's test client.
   * For UI tests: Setup component isolation.

3. **Write Test Cases:**
   * Start with simple cases and progressively add complexity.
   * Include edge cases and failure scenarios.
   * Add clear assertions that verify expected outcomes.

4. **Review and Refactor:**
   * Ensure tests are concise, readable, and maintainable.
   * Eliminate duplicate setup code by using fixtures.
   * Verify that tests fail when they should (test the tests).

### Example Process for a Workflow Test

```python
# 1. Import test libraries and the workflow under test
from temporalio.testing import WorkflowEnvironment
import pytest
from backend.workflows.article_workflow import SubmitArticleWorkflow

# 2. Setup test environment
@pytest.fixture
async def workflow_environment():
    env = await WorkflowEnvironment.start_local()
    yield env
    await env.shutdown()

# 3. Write the test case
async def test_submit_article_workflow(workflow_environment):
    """Verify that the article submission workflow correctly processes an article URL.

    Given: A valid article URL
    When: The SubmitArticleWorkflow is executed with the URL
    Then: The workflow should return a result with 'submitted' status and the correct URL
    """
    # Given: Setup test data
    article_url = "https://example.com/test-article"

    # When: Run the workflow
    result = await workflow_environment.execute_workflow(
        SubmitArticleWorkflow.run,
        article_url,
        id="test-workflow-id",
        task_queue="test-task-queue"
    )

    # Then: Verify the expected outcome
    assert result.status == "submitted"
    assert result.url == article_url
```

## Unit Test Structure

### Directory Organization

We follow a "tests-alongside-code" organization pattern. Unit tests are placed in the same directory as the module they test:

```
backend/
├── workflows/
│   ├── article_workflow.py
│   ├── article_workflow_test.py    # Tests for article_workflow.py
│   ├── content_workflow.py
│   └── content_workflow_test.py    # Tests for content_workflow.py
├── activities/
│   ├── fetch_content_activity.py
│   └── fetch_content_activity_test.py  # Tests for the corresponding activity
├── api/
│   ├── article.py
│   └── article_test.py      # Tests for article routes
├── tests/                          # Common test utilities and fixtures
│   ├── conftest.py                 # Shared pytest fixtures
│   ├── factories.py                # Test data factories
│   ├── mocks.py                    # Common mock objects and utilities
│   └── utils.py                    # Test utility functions
```

### Integration and E2E Tests

Integration and end-to-end tests have their own directories:

```
backend/
├── tests/
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
```

### Test File Naming

- Test files should be named `{module_name}_test.py`
- Test classes (if used) should be named `Test{ClassUnderTest}`
- Test methods should be named `test_{method_name}_{scenario}`

### Structure Within Test Files

1. **Imports and Setup:**
   * Import required modules and test utilities
   * Import fixtures from shared conftest if needed

2. **Local Fixtures (if needed):**
   * Define module-specific fixtures
   * Reuse shared fixtures from conftest.py when possible

3. **Test Cases:**
   * Each test function should focus on a single behavior
   * Use descriptive test names that explain the expected behavior
   * Prefer flat test functions over test classes unless grouping is necessary

4. **Teardown:**
   * Use pytest fixtures for automatic teardown
   * Clean up any resources created during tests

## Unit Testing Strategy

### Backend Testing

#### Workflow Tests

- **Goal:** Verify the orchestration logic, not the activities themselves.
- **Approach:**
  * Use Temporal's testing framework to mock the Temporal server and client.
  * Mock or stub activities to isolate workflow logic.
  * Verify workflow decision-making, sequencing, and error handling.
  * Test signals, timers, and child workflow interactions.

```python
async def test_workflow_retry_on_activity_failure():
    """Verify that workflows automatically retry failed activities."""
    # given
    activity_mock = mock_activity("fetch_content_activity")
    activity_mock.side_effect = [Exception("Simulated failure"), {"content": "Success"}]

    # when
    result = await workflow_environment.execute_workflow(FetchContentWorkflow.run, "http://example.com")

    # then
    assert result["status"] == "completed"
    assert activity_mock.call_count == 2
```

#### Activity Tests

- **Goal:** Verify individual activity functionality in isolation.
- **Approach:**
  * Mock external dependencies (databases, APIs, file systems).
  * Test both success and failure cases.
  * Verify idempotency behavior.
  * Test activity retry logic if applicable.

```python
async def test_fetch_content_activity():
    """Verify that fetch content activity correctly retrieves and processes article content."""
    # given
    mock_http = MockHttpClient()
    mock_http.add_response("https://example.com", 200, "Article content")

    # when
    result = await fetch_content_activity("https://example.com", http_client=mock_http)

    # then
    assert result["status"] == "success"
    assert result["content"] == "Article content"
```

#### API Tests

- **Goal:** Verify API endpoints correctly trigger workflows and return appropriate responses.
- **Approach:**
  * Use FastAPI's TestClient.
  * Mock Temporal client for workflow execution.
  * Test request validation, response formatting, and error handling.

```python
def test_submit_article_api():
    """Verify that the article submission API correctly starts a workflow."""
    # given
    mock_temporal = MockTemporalClient()
    app.dependency_overrides[get_temporal_client] = lambda: mock_temporal

    # when
    response = client.post("/articles/", json={"url": "https://example.com"})

    # then
    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    assert mock_temporal.workflows_started[0].name == "SubmitArticleWorkflow"
```

### Frontend Testing

- **Goal:** Verify UI components correctly render data and handle user interactions.
- **Approach:**
  * Test component rendering with mock data.
  * Test user interactions and state updates.
  * Verify API client integration with mock requests.

## Format for Unit Tests

We follow the Given-When-Then pattern from Behavior-Driven Development (BDD) for structuring test cases:

### 1. Given

Establish the initial context and preconditions for the test:

```python
# Given
article_url = "https://example.com/article"
mock_db = MockDatabase()
mock_db.setup([])  # Empty database
activity = StoreArticleActivity(db=mock_db)
```

### 2. When

Execute the action or behavior being tested:

```python
# When
result = await activity.store_article(article_url)
```

### 3. Then

Verify the expected outcomes and postconditions:

```python
# Then
assert result.id is not None
assert result.url == article_url
assert result.status == "pending"
assert len(mock_db.articles) == 1
```

### Complete Example

```python
async def test_store_article_activity_creates_new_article():
    """Verify that the store article activity creates a new article in the database."""
    # given
    article_url = "https://example.com/test-article"
    mock_db = MockDatabase()
    activity = StoreArticleActivity(db=mock_db)

    # when
    result = await activity.store_article(article_url)

    # then
    assert result.id is not None
    assert result.url == article_url
    assert result.status == "pending"
    stored_article = mock_db.find_article_by_id(result.id)
    assert stored_article is not None
    assert stored_article.url == article_url
```

## Testing Temporal-Specific Components

### Mocking Temporal Services

Use the Temporal Python SDK testing utilities:

```python
# In backend/tests/conftest.py
@pytest.fixture
async def workflow_environment():
    env = await WorkflowEnvironment.start_local()
    client = await env.client()

    # Register your workflows and activities
    worker = Worker(client, task_queue="test-queue")
    worker.register_workflow(SubmitArticleWorkflow)
    worker.register_activity(store_article_activity)
    await worker.start()

    yield client

    await worker.shutdown()
    await env.shutdown()

# Then in your workflow_test.py file:
async def test_submit_article(workflow_environment):
    # Test using the shared fixture
    result = await workflow_environment.execute_workflow(...)
```

### Testing Workflow Determinism

Ensure workflows produce the same results given the same history:

```python
async def test_workflow_determinism():
    """Verify that workflows are deterministic by replaying execution history."""
    # First run
    result1 = await client.execute_workflow(MyWorkflow.run, "input")

    # Replay from history
    history = await client.get_workflow_history("workflow_id")
    replayer = WorkflowReplayer()
    replayer.register_workflow(MyWorkflow)
    await replayer.replay_workflow(history)  # Should not raise exceptions
```

## Test Data Management

1. **Common Fixtures:** Use shared pytest fixtures in `backend/tests/conftest.py` for common setup.
2. **Factory Patterns:** Implement factory functions in `backend/tests/factories.py` to create test objects.
3. **Local Fixtures:** Define test-specific fixtures within the test file.
4. **Randomized Testing:** Use controlled randomization for property-based testing.

## Continuous Integration

1. All tests must pass before merging code into main branches.
2. Run unit tests on every pull request.
3. Run integration and e2e tests nightly or before releases.

## Test Coverage Requirements

1. **Workflows:** 100% coverage of all execution paths.
2. **Activities:** 90%+ coverage with emphasis on error handling paths.
3. **API Endpoints:** 100% coverage of all endpoints and response types.
4. **Models:** 100% coverage of model validation and constraints.

## Guidelines for Testing Specific Scenarios

### Long-Running Workflows

- Use simulated time in Temporal test environment.
- Test workflow resumption after simulated crashes.

### Error Recovery

- Test compensation logic when activities fail.
- Verify saga patterns work as expected.

### Concurrency

- Test workflows that execute activities in parallel.
- Verify child workflow coordination.

---

By following these guidelines, we ensure our durable execution architecture remains reliable, maintainable, and adaptable to changing requirements. Testing is not an afterthought but a core part of our development process.
