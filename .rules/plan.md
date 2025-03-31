# Project Plan: ATLAS

## 1. Core Philosophy & Vision

**Vision:** An intelligent companion ("ATLAS") that guides users through a deliberate, sequential process of transforming raw web articles (Lead) into valuable knowledge assets (Gold).

**Philosophy:** Inspired by Francis Bacon's "Of Studies," the workflow emphasizes distinct stages of engagement:
1.  **Prospecting (Taste):** Quickly assess relevance.
2.  **Extraction (Swallow):** Efficiently consume core facts and generate immediate recall aids (Flashcards).
3.  **Transmutation (Digest):** Deepen understanding through creative synthesis, interaction, and building evolving "Living Topics."
4.  **Quintessence (Conference):** Produce polished, shareable summaries (Podcasts, Briefings) for communication.

The goal is to make learning from articles an active, structured, and creative process, enhancing comprehension, recall, and the ability to communicate insights.

## 2. Guiding Principles (Learning Science & Bacon)

*   **Sequential Engagement:** Strict workflow (Taste -> Swallow -> Digest -> Conference) ensures deliberate processing.
*   **Chunking:** Breaking down articles (`Swallow`) and grouping them into "Living Topics" (`Digest`).
*   **Active Recall:** Generating Flashcards (`Swallow`) and prompting user reflection (`Digest`).
*   **Elaboration & Exactness:** AI Summaries/Insights (`Swallow`), AI Narrative Weaving, Analogy Generation, User Reflection (`Digest`) promote deeper processing and precise understanding ("Writing an exact man").
*   **Dual/Multi-Modal Learning:** Text summaries, Flashcards (`Swallow`), Visualizations, Narratives (`Digest`), Podcast Scripts (`Conference`).
*   **Meaningfulness:** User "Purpose Tags" align processing with goals. Creative outputs (`Digest`, `Conference`) make information more engaging.
*   **Synthesis & Readiness:** "Living Topics" (`Digest`) and generated Briefings/Podcast Scripts (`Conference`) prepare users for discussion ("Conference a ready man").
*   **Weigh & Consider:** AI prompts in `Digest` encourage critical interaction with the material.

## 3. Workflow Stages & Features

**Stage 1: Prospecting ("Taste")**
*   **Goal:** Quickly assess relevance.
*   **Input:** URLs, optional "Purpose Tag".
*   **Process:** Fetch (Jina API), AI Gist, Key Concepts -> Generate "Prospect Card".
*   **Output:** Queue/Dashboard of Prospect Cards.
*   **User Action:** Review Cards -> `Discard` or `Extract` (Proceed).

**Stage 2: Extraction ("Swallow")**
*   **Goal:** Consume core info, generate immediate recall aids.
*   **Input:** Promoted articles.
*   **Process (AI):** Structured Summary, Highlights (-> Flashcards), Actionable Insights. Cleaned Text provided.
*   **Output:** "Extracted Essence" (Summary, Flashcards, Insights, Text) stored in DB. Flashcards exportable (e.g., JSON/CSV).
*   **User Action:** Review, Export Flashcards -> `Archive` or `Transmute` (Proceed).

**Stage 3: Transmutation ("Digest")**
*   **Goal:** Deeper understanding via creative synthesis & interaction.
*   **Input:** Promoted articles + their "Extracted Essence".
*   **Process (Interactive AI Co-Pilot):**
    *   **Living Topic Document:** Create/update document associating related articles (using `bertopic`/embeddings).
    *   **AI Narrative Weaving:** Drafts/updates integrated narrative (user guides style: story, explanation).
    *   **AI Analogy/Metaphor Workbench:** Suggests analogies for concepts.
    *   **AI Visualization Data:** Generates data for infographic/mind-map (nodes, edges for concepts/arguments). Output data usable by visual tools or potentially an Image API.
    *   **AI Debate/Exploration:** User poses questions; AI simulates discussion between article viewpoints.
    *   **User Reflection Space:** Prompted critical thinking and connections.
*   **Output:** Evolving "Living Topic Documents" (narrative, analogies, viz data, debates, reflections) in DB.
*   **User Action:** Guide AI, Edit, Interact, Reflect, Manage Topics.

**Stage 4: Quintessence ("Conference")**
*   **Goal:** Produce polished, shareable summaries for communication.
*   **Input:** User-selected "Living Topic Document".
*   **Process (AI Production Assistant):**
    *   **Podcast Script Generation:** Draft script from Living Topic narrative/insights/analogies (formatted for external `podgen`).
    *   **Executive Briefing Generation:** Draft concise summary document.
    *   **Presentation Outline Generation:** Create slide outline.
*   **Output:** Podcast Scripts, Briefings, Outlines.
*   **User Action:** Select Topic, Choose output, Review/Edit, Export.

## 4. Proposed Technology Stack

*   **Language:** Python 3.10+
*   **Dependency Management:** `uv` & `pyproject.toml`
*   **Web Framework:** FastAPI (recommended for API-first & `pydantic` integration) or Flask.
*   **Frontend:** Basic HTML/CSS/JavaScript. Consider HTMX for simplicity or a lightweight JS framework if complex interactions are needed later.
*   **Database:** PostgreSQL.
*   **ORM:** `sqlmodel` (integrates SQL Alchemy + Pydantic).
*   **Web Scraping:** `httpx` (async) for Jina API `https://r.jina.ai/`.
*   **LLM Interaction:** `pydantic-ai` for structured I/O, `openai` client (or other provider's SDK).
*   **Topic Modeling/Clustering:** `bertopic`, `sentence-transformers` (for Living Topics).
*   **Flashcard Format:** JSON or CSV.
*   **Visualization:** Output structured data (JSON) for frontend libraries (e.g., `mermaid.js`, `D3.js`). Optional: AI Image Generation API (e.g., OpenAI DALL-E) for infographics.
*   **Background Tasks:** Consider `Celery` if processing becomes long.
*   **(Optional) CLI:** `typer` for backend admin tasks/batch processing.

## 5. High-Level Implementation Steps

1.  **Setup:** `uv init`, `pyproject.toml`, basic FastAPI app structure, Docker for Postgres.
2.  **Database Schema:** Define models (`sqlmodel`) for Articles, ProspectCards, ExtractedEssence, Flashcards, LivingTopics, UserReflections, etc.
3.  **Stage 1 (Prospecting):** Implement Jina API call, AI Gist generation (`pydantic-ai`), basic card UI.
4.  **Stage 4 (Extraction):** Implement AI Summary/Highlights/Insights (`pydantic-ai`), Flashcard generation/export, DB storage, UI display.
5.  **Stage 3 (Transmutation - Core):**
    *   Implement Living Topic logic (DB linking, `bertopic` integration).
    *   Develop prompts/logic for AI Narrative Weaving, Analogies, Visualization data.
    *   Build basic interactive UI components for user guidance and reflection.
6.  **Stage 4 (Quintessence):** Implement prompts for Podcast Script, Briefing, Outline generation; add export functionality. Ensure script format suits `podgen`.
7.  **Frontend Development:** Build out the UI iteratively for each stage.
8.  **Testing & Refinement:** Throughout the process.

## 6. Future Considerations

*   Spaced repetition integration for Flashcards or Living Topic key points.
*   More sophisticated visualization options.
*   Direct integration with highlight applications via API (if available).
*   User accounts and collaboration features.
