# System Architecture: Durable Workflow Execution

## 1. Architectural Overview

Our system architecture is built on the principle of durable execution, implemented through the Temporal framework. This document serves as a practical guide for engineers and AI agents to understand the architectural pattern and implement solutions within it.

**Core Architecture Principles:**

* **Workflow-as-Code Pattern:** Business processes are defined as code that orchestrates activities.
* **Separation of Concerns:** Workflow logic (orchestration) is distinct from activity implementation (execution).
* **State Externalization:** Workflow state is managed by the execution engine, not your application code.
* **Built-in Resilience:** The architecture inherently handles retries, timeouts, and recovery from failures.

## 2. Temporal Integration

Temporal serves as our durable execution engine. In our architecture, Temporal provides:

* **Workflow State Management:** Handles persistence of execution state during pauses, failures, and scaling events.
* **Task Dispatching:** Routes workflow and activity tasks to available workers.
* **Retry Management:** Configurable policies for handling transient failures.
* **Visibility:** Built-in tools for monitoring workflow execution and troubleshooting.

## 3. System Structure and Implementation

### Directory Structure

* **Backend (`backend/`):** Contains all server-side code and business logic
* **Frontend (`frontend/`):** Contains all client-side code and UI components

### Core Backend Components

1. **Workflow Definitions**
   * Located in: `backend/workflows/` directory
   * Implement orchestration logic using Python
   * Call activities, handle signals, and manage child workflows

2. **Activity Implementations**
   * Located in: `backend/activities/` directory
   * Implement actual business logic and external system interactions
   * Language: Python with asyncio for efficient async operations

3. **Worker Services**
   * Located in: `backend/workers/`
   * Deployed as containerized services in our Kubernetes cluster
   * Separate worker deployments for workflow execution and activity execution
   * Auto-scaling based on task queue depth

4. **API Layer**
   * Located in: `backend/api/`
   * Modular structure with separate routers for different endpoint categories
     * Main app in `backend/api/main.py` - bootstraps and configures FastAPI app
     * Route modules in `backend/api/routes/` - organized by domain/feature
     * Shared schemas in `backend/api/schemas.py` - common data models
     * Core dependencies in `backend/api/routes/core/` - shared dependencies
   * FastAPI-based REST API that translates HTTP requests into workflow executions
   * Event handlers that initiate workflows in response to message queue events

### Core Frontend Components

1. **UI Components**
   * Located in: `frontend/components/`
   * Reusable UI elements for displaying workflow and content data

2. **Pages**
   * Located in: `frontend/pages/`
   * Main application views and routing logic

3. **API Integration**
   * Located in: `frontend/api/`
   * Client code for interacting with backend APIs

### Technology Stack Integration

* **Runtime Environment:** Kubernetes for worker deployment
* **Development Environment:** Local Temporal server via Docker Compose for development
* **Backend Framework:** FastAPI for API endpoints and Temporal client integration
* **Database:** PostgreSQL with SQLModel ORM
* **Observability:** Prometheus/Grafana for metrics, ELK stack for logging
* **CI/CD Pipeline:** GitHub Actions for testing and deployment automation

## 4. Development Guidelines

### Workflow Development

1. **Workflow Structure**
   * Begin with a clear definition of workflow inputs, outputs, and business steps
   * Define error handling and compensation logic up front
   * Model long-running waits using Temporal timers rather than polling

2. **Activity Definition**
   * Define activity interfaces using Python type hints and Pydantic models
   * Use dataclasses or Pydantic for structured inputs and outputs
   * Document each activity's purpose, behavior, and side effects with docstrings

3. **Naming Conventions**
   * Workflows: `backend/workflows/{business_process}_workflow.py` with main class as `{BusinessProcess}Workflow` (e.g., `OrderFulfillmentWorkflow`)
   * Activities: `backend/activities/{action}_{entity}_activity.py` with main function as `{action}_{entity}` (e.g., `reserve_inventory`)
   * API Routes: `backend/api/{resource}.py` (e.g., `article.py`)
   * Task Queues: `{domain}-{workflow|activity}` (e.g., `orders-workflow`)

### Engineering Requirements

1. **Determinism in Workflows**
   * Workflow code must be deterministic - given the same history, it must produce the same decisions
   * Restrict in workflow code:
     * No random numbers or current time access
     * No direct external API calls
     * No access to global/shared mutable state
     * No direct database access
   * Move all non-deterministic operations to activities

2. **Idempotency in Activities**
   * All activities must be idempotent (safe to retry)
   * Implement idempotency using:
     * Generate and pass idempotency keys for external API calls
     * Check-then-act patterns for resource creation
     * Atomic database operations

3. **Error Handling Strategy**
   * Transient errors: Configure retry policies on activities
   * Business errors: Return typed errors, not exceptions
   * Critical errors: Implement compensation logic via Saga pattern

## 5. Design Principles

### SOLID for Durable Execution

1. **Single Responsibility**
   * Workflows should only orchestrate, not implement business logic
   * Activities should perform one focused task
   * Split complex activities into multiple smaller activities

2. **Open/Closed**
   * Design for workflow versioning
   * Use signals for dynamic behavior changes
   * Implement feature flags via workflow parameters

3. **Dependency Inversion**
   * Workflows depend on activity interfaces, not implementations
   * Activities depend on service interfaces, not concrete implementations
   * Use dependency injection for activity and service implementations

### Additional Design Principles

1. **YAGNI (You Ain't Gonna Need It)**
   * Start with simple workflow structure
   * Add complexity only when requirements demand it
   * Avoid speculative branches or error handling

2. **DRY (Don't Repeat Yourself)**
   * Extract common workflow patterns into reusable child workflows
   * Create shared libraries for common activity patterns
   * Standardize error handling and retry policies

3. **KISS (Keep It Simple, Stupid)**
   * Prefer readability over clever optimizations
   * Model workflow steps to match business process steps
   * Use clear activity names that reflect business language

## 6. Implementation Patterns

### Common Workflow Patterns

1. **Request-Response**
   * For synchronous API operations requiring orchestration
   * Client initiates workflow and waits for completion
   * Implement with workflow timeouts appropriate to client expectations

2. **Long-Running Process**
   * For processes that may take minutes to days
   * Client receives workflow ID for status tracking
   * Use signals to allow external influence (cancellation, modification)

3. **Event-Driven**
   * Initiated by events from message queues or webhooks
   * May spawn multiple child workflows
   * Often implements the Saga pattern for distributed transactions

4. **Scheduled Operations**
   * For periodic maintenance or batch processing
   * Use Temporal's cron scheduling
   * Implement idempotency checks to handle overlapping executions

### Integration Approaches

1. **FastAPI Integration**
   * REST endpoints map to workflow executions
   * Synchronous endpoints wait for workflow completion (with timeout)
   * Asynchronous endpoints return workflow ID and status URL

2. **Event Source Integration**
   * Subscribers to message queues launch workflows
   * Workflow results can be published to output queues
   * Ensure exactly-once semantics via idempotency checks

## 7. Operational Considerations

### Deployment Model

* **Development:** Local Temporal server via Docker Compose
* **Testing:** Dedicated Temporal namespace in shared cluster

### Monitoring & Observability

* **Key Metrics to Track**
  * Workflow completion rate and latency
  * Activity error rates
  * Task queue depth
  * Worker utilization

* **Log Management**
  * Structured logging with correlation IDs
  * Workflow execution IDs included in all logs
  * Activity-specific logging with context

### Security Guidelines

* Sensitive data should be encrypted before workflow input/output
* Implement namespaces for multitenancy isolation
* Use least-privilege service accounts for workers

## 8. Conclusion

This architecture provides a resilient, maintainable foundation for building complex, long-running business processes. By adhering to the design principles and implementation patterns outlined in this document, engineers can create systems that are reliable, scalable, and adaptable to changing business requirements.
