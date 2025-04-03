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
- PostgreSQL (for database)
- Temporal server (for workflow execution)

### Setup with Just

ATLAS uses [Just](https://github.com/casey/just) as a command runner for common development tasks:

```bash
# Clone the repository
git clone https://github.com/yourusername/atlas.git
cd atlas

# Full setup (creates venv, installs dependencies, and sets up pre-commit hooks)
just setup

# Activate the virtual environment
source .venv/bin/activate  # On Unix/MacOS
# .venv\Scripts\activate  # On Windows
```

Alternatively, you can perform each step manually:

```bash
# Create virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Unix/MacOS
# .venv\Scripts\activate  # On Windows

# Install dependencies with lock file
just install-locked

# Setup pre-commit hooks
just setup-hooks
```

### Set up pre-commit hooks

```bash
pre-commit install
```

## Development

### Running the Application

```bash
# Start the API server (with hot reload)
just server

# In a separate terminal, start the worker
just worker
```

### Database Migrations

```bash
# Create a new migration
just migrate "Description of the changes"

# Apply all migrations
just migrate-up

# Rollback the most recent migration
just migrate-down
```

### Code Quality

```bash
# Run linting and formatting
just lint

# Run type checking
just check

# Run tests
just test

# Run tests with coverage
just test-cov
```

## Project Structure

The project implements a workflow-based architecture using Temporal for durable execution:

```
/backend
├── activities/       # Temporal activity implementations
├── api/              # FastAPI endpoints and server setup
├── db/               # Database models and connections
│   └── migrations/   # Alembic migrations
├── temporal/         # Temporal client configuration
├── workflows/        # Temporal workflow definitions
└── workers/          # Temporal worker setup
```

For more detailed information about the architecture, refer to the [`.rules/architecture.md`](.rules/architecture.md) document.

## Environment Variables

### Database Configuration
- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: atlas)
- `DB_USER`: Database username (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)

### Temporal Configuration
- `TEMPORAL_HOST`: Temporal server host (default: localhost)
- `TEMPORAL_PORT`: Temporal server port (default: 7233)
- `TEMPORAL_NAMESPACE`: Temporal namespace (default: default)

### API Configuration
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8000)

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

The AGPL-3.0 license ensures that:
- You are free to use, modify, and distribute this software
- If you modify the software, you must share those modifications under the same license
- If you use a modified version of this software to provide a service over a network, you must make your modified source code available
- This software cannot be relicensed under different terms without permission
