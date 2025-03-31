# ATLAS: Incremental Development Milestones

**Guiding Principles:**

1.  **Duration:** Target 1-2 days effort per milestone.
2.  **Philosophy:** Working software over comprehensive features. Build the skeleton, then add muscle.
3.  **Outcome:** Each milestone delivers a usable increment, demonstrating progress and allowing early feedback.
4.  **Design:** Follow durable execution patterns with clearly separated workflow and activity code.

---

**Phase 1: Core Infrastructure & Temporal Setup**

*   **Milestone 1: Project Foundation & Temporal Environment**
    *   **Goal:** Establish development environment with Temporal integration.
    *   **Tasks:**
        *   Initialize project with top-level `backend/` and `frontend/` directories.
        *   Set up `backend/` structure with subdirectories (`workflows/`, `activities/`, `api/`, `workers/`).
        *   Set up Docker Compose for local Temporal server and PostgreSQL database.
        *   Configure backend development dependencies (Python Temporal SDK, FastAPI, SQLModel, pytest).
        *   Create core project configuration files (`backend/pyproject.toml`, `.env`) and documentation.
        *   Implement a basic health check workflow and activity.
    *   **Deliverable:** A functioning development environment with Temporal server and the ability to run a simple workflow. **Value:** Core infrastructure validated.

*   **Milestone 2: Article Intake Workflow**
    *   **Goal:** Implement article submission workflow using durable execution patterns.
    *   **Tasks:**
        *   Define `Article` model for database storage in `backend/models/`.
        *   Create `SubmitArticleWorkflow` in the `backend/workflows/` directory, implementing the durable workflow pattern.
        *   Implement `StoreArticleActivity` in `backend/activities/` directory to handle database interactions.
        *   Create API endpoint in `backend/api/` that triggers the workflow via Temporal client.
        *   Implement `GetArticlesActivity` and integrate it with a query workflow.
    *   **Deliverable:** Ability to submit article URLs via API, with durable execution guarantees, and retrieve submitted articles. **Value:** System demonstrates the workflow-as-code pattern for article intake.

*   **Milestone 3: Content Fetching Workflow**
    *   **Goal:** Implement durable content fetching with reliable error handling and retries.
    *   **Tasks:**
        *   Create `FetchContentWorkflow` in `backend/workflows/` directory.
        *   Implement `FetchContentActivity` in `backend/activities/` to call external APIs (e.g., `r.jina.ai`).
        *   Configure retry policies and error handling in both the workflow and activity.
        *   Implement activity for storing fetched content in the database.
        *   Create API endpoints in `backend/api/` to trigger content fetching workflows and query their status.
    *   **Deliverable:** Durable, fault-tolerant content fetching for submitted articles with automatic retries. **Value:** System demonstrates resilient external API interaction using Temporal patterns.

---

**Phase 2: AI Processing Workflows & UI Integration**

*   **Milestone 4: AI Gist Generation Workflow ("Taste")**
    *   **Goal:** Implement a durable workflow for AI gist generation with proper error handling.
    *   **Tasks:**
        *   Create `GistGenerationWorkflow` in the `backend/workflows/` directory.
        *   Implement `GenerateGistActivity` in `backend/activities/` directory to handle LLM interactions.
        *   Configure retry policies specifically tailored for LLM API calls.
        *   Implement storage activities for persisting generated gists.
        *   Create API endpoints in `backend/api/` to trigger gist generation and query results.
        *   Add workflow signaling to allow cancellation of long-running LLM calls.
    *   **Deliverable:** Fault-tolerant AI gist generation with durable execution guarantees. **Value:** First AI processing integrated within the workflow architecture.

*   **Milestone 5: Frontend UI Implementation & Integration**
    *   **Goal:** Create a web interface that displays workflows and their current statuses.
    *   **Tasks:**
        *   Initialize the `frontend/` directory structure with standard web project organization.
        *   Create API client in `frontend/api/` to interact with backend endpoints.
        *   Implement UI components in `frontend/components/` for displaying article data and workflow status.
        *   Create pages in `frontend/pages/` for triggering various workflows (submission, fetching, gist generation).
        *   Implement polling or server-sent events for updating workflow status.
        *   Set up build pipeline for frontend assets.
    *   **Deliverable:** A dynamic web interface showing workflow execution status and results. **Value:** Visibility into the durable execution system.

*   **Milestone 6: Summary Generation Workflow ("Swallow")**
    *   **Goal:** Implement a structured summary workflow with activity chaining.
    *   **Tasks:**
        *   Create `SummaryGenerationWorkflow` that orchestrates multiple activities.
        *   Implement modular activities for different aspects of summarization.
        *   Configure workflow-level retry and error handling policies.
        *   Implement compensation logic for handling partial failures.
        *   Update API and UI to support summary generation and display.
    *   **Deliverable:** Multi-step summary generation process with compensation handling for failures. **Value:** Demonstrates advanced workflow patterns for complex AI processing.

*   **Milestone 7: Flashcard Generation Child Workflow ("Swallow")**
    *   **Goal:** Implement child workflow pattern for flashcard generation.
    *   **Tasks:**
        *   Create `FlashcardGenerationWorkflow` designed to run as a child workflow.
        *   Implement activities for extracting and formatting flashcards.
        *   Create a parent workflow that coordinates summary and flashcard generation.
        *   Implement signal-based triggers to influence workflow execution.
        *   Add export functionality to retrieve generated flashcards in various formats.
    *   **Deliverable:** Hierarchical workflow architecture for complex content processing. **Value:** Demonstrates parent-child workflow pattern for modular process design.

---

**Phase 3: Advanced Synthesis & Creative Output Workflows**

*   **Milestone 8: Topic Modeling Workflow ("Digest")**
    *   **Goal:** Implement a scalable, durable workflow for article clustering.
    *   **Tasks:**
        *   Create `TopicModelingWorkflow` with configurable parameters.
        *   Implement `GenerateEmbeddingsActivity` for processing article content.
        *   Design `ClusterArticlesActivity` for topic identification.
        *   Create a cron-scheduled workflow for periodic clustering of new content.
        *   Implement dynamic task routing based on computation requirements.
        *   Add UI components for visualizing topic clusters and their relationships.
    *   **Deliverable:** Scalable, scheduled topic clustering with automatic processing of new articles. **Value:** Demonstrates scheduled workflows and resource-intensive computation patterns.

*   **Milestone 9: Narrative Synthesis Workflow ("Digest")**
    *   **Goal:** Implement an event-driven workflow for narrative generation across articles.
    *   **Tasks:**
        *   Create `NarrativeSynthesisWorkflow` triggered by topic updates.
        *   Implement activities for gathering related articles and generating narrative.
        *   Design compensation logic for handling partial narrative generation failures.
        *   Create a signal handler for injecting human feedback during narrative generation.
        *   Implement versioning to manage narrative evolution over time.
    *   **Deliverable:** Event-driven narrative generation that can incorporate user feedback. **Value:** Demonstrates event-driven workflow patterns and user interaction within workflows.

*   **Milestone 10: Content Transformation Workflows ("Conference")**
    *   **Goal:** Create a family of parallel workflows for transforming content into different formats.
    *   **Tasks:**
        *   Design a common `ContentTransformationWorkflow` interface.
        *   Implement specific workflows: `PodcastScriptWorkflow`, `BriefingWorkflow`, `OutlineWorkflow`.
        *   Create modular transformation activities shared across workflows.
        *   Implement parallel execution of transformations when appropriate.
        *   Design a unified UI for accessing all transformation outputs.
    *   **Deliverable:** A suite of content transformation workflows executing in parallel. **Value:** Demonstrates workflow interface patterns and parallel execution strategies.

---

**Phase 4: System Refinement & Operationalization**

*   **Milestone 11: Deployment Automation & Monitoring**
    *   **Goal:** Establish CI/CD pipeline and observability for workflows.
    *   **Tasks:**
        *   Set up GitHub Actions workflows for testing and deployment.
        *   Implement Prometheus metrics collection for workflow and activity monitoring.
        *   Create Grafana dashboards for key performance indicators.
        *   Implement structured logging with correlation IDs throughout the system.
        *   Configure alerting for workflow failures and performance degradation.
    *   **Deliverable:** Production-ready deployment pipeline with comprehensive monitoring. **Value:** Operational excellence for the durable execution architecture.

*   **Milestone 12: Security & Multi-tenancy**
    *   **Goal:** Implement secure, isolated workflow execution for multiple users.
    *   **Tasks:**
        *   Design namespace-based tenant isolation in Temporal.
        *   Implement user authentication and authorization for workflow triggering.
        *   Create secure credential handling for activities requiring external API access.
        *   Add data encryption for sensitive workflow inputs and outputs.
        *   Implement resource quotas and rate limiting per tenant.
    *   **Deliverable:** Secure multi-tenant system ready for multiple user profiles. **Value:** Production-grade security and isolation.

*   **Milestone 13: Performance Optimization**
    *   **Goal:** Optimize workflow execution for high throughput and minimal latency.
    *   **Tasks:**
        *   Profile and optimize critical workflow paths.
        *   Implement worker-specific task queues for specialized activities.
        *   Design caching mechanisms for frequently accessed data.
        *   Implement batch processing patterns for high-volume operations.
        *   Configure auto-scaling for workers based on queue depth.
    *   **Deliverable:** Optimized system capable of handling production load. **Value:** Scalable, efficient workflow execution.
