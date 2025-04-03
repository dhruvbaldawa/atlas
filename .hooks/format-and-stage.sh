#!/bin/bash
set -e

# Run ruff format on all staged Python files
echo "Running ruff format..."
ruff format .

# Add all formatted files back to staging
echo "Auto-staging formatted files..."
git add -u

# Return success
exit 0
