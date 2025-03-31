# ATLAS

ATLAS is an intelligent companion that guides users through a deliberate, sequential process of transforming raw web articles into valuable knowledge assets.

## Project Philosophy

Inspired by Francis Bacon's "Of Studies," the workflow emphasizes distinct stages of engagement:

1. **Prospecting (Taste):** Quickly assess relevance.
2. **Extraction (Swallow):** Efficiently consume core facts and generate immediate recall aids (Flashcards).
3. **Transmutation (Digest):** Deepen understanding through creative synthesis, interaction, and building evolving "Living Topics."
4. **Quintessence (Conference):** Produce polished, shareable summaries (Podcasts, Briefings) for communication.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) for package management
- PostgreSQL

### Setup with UV

```bash
# Clone the repository
git clone https://github.com/yourusername/atlas.git
cd atlas

# Create and activate a virtual environment using UV
uv venv
source .venv/bin/activate  # On Unix/MacOS
# .venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### Set up pre-commit hooks

```bash
pre-commit install
```

## Development

### Code Formatting and Linting

This project uses Ruff for linting and formatting:

```bash
# Run linting
ruff check .

# Run formatting
ruff format .
```

### Static Type Checking

```bash
# Run Pyright
pyright
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=backend/```

## Project Structure

The project structure follows the architecture defined in the [`.rules/architecture.md`](.rules/architecture.md) document. This document details the separation of backend and frontend concerns, with the backend implementing a workflow-based architecture using Temporal for durable execution. Please refer to this document for the most up-to-date information about the project structure.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
