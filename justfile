# ATLAS Project Justfile
# This file contains common commands for development

# List available commands
default:
    @just --list

# Install dependencies
install:
    uv pip install -e ".[dev]"
    just lock

# Sync virtual environment with pyproject.toml (including dev dependencies)
sync:
    @echo "Syncing virtual environment with pyproject.toml..."
    # Use UV's sync command with flags to include dev dependencies
    uv sync --all-extras
    @echo "Sync complete!"

# Install pre-commit hooks
setup-hooks:
    uv pip install pre-commit
    uv run pre-commit install

# Run tests
test:
    uv run pytest

# Run tests with coverage and generate reports (XML and HTML)
test-cov:
    @echo "Running tests with coverage..."
    mkdir -p test-results/coverage
    uv run pytest --cov=backend --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml --cov-report=html:test-results/coverage

# Run static type checking
typecheck:
    pyright

# Run linting
lint:
    ruff check --fix .

# Run formatting
format:
    ruff format .

# Run all checks (linting, type checking, and tests)
check: format lint typecheck test

# Activate virtual environment (must be run with source prefix: `source $(just activate)`)
activate:
    echo .venv/bin/activate

# Create a new virtual environment
create-venv:
    uv venv

# Clean up python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type d -name ".ruff_cache" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name "test-results" -exec rm -rf {} +

# Update all dependencies and lock file to their latest versions
update-deps:
    @echo "Updating dependencies to latest versions..."
    uv pip install -e ".[dev]" --upgrade
    pre-commit autoupdate
    just lock
    @echo "Dependencies updated and lock file generated!"

# Generate or update lock file
lock:
    @echo "Generating lock file..."
    uv lock
    @echo "Lock file generated!"

# Install from lock file
install-locked:
    @echo "Installing dependencies from lock file..."
    uv sync --locked --all-extras

# Setup the whole project from scratch
setup: create-venv lock install-locked setup-hooks

# Run the API server with auto-reload
server:
    uvicorn backend.api.main:app --reload

# Run the worker
worker:
    python -m backend.workers.worker

# Create a new migration with a message
migrate message="auto":
    alembic revision --autogenerate -m "{{message}}"

# Apply all migrations
migrate-up:
    alembic upgrade head

# Rollback one migration
migrate-down:
    alembic downgrade -1
