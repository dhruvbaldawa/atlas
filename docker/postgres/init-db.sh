#!/bin/bash
set -e

# Function to create a database if it doesn't exist
create_db_if_not_exists() {
  local db_name=$1
  echo "Checking if database '$db_name' exists..."
  if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
    echo "Database '$db_name' already exists"
  else
    echo "Creating database '$db_name'..."
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $db_name;"
    echo "Database '$db_name' created successfully"
  fi
}

# Create databases for application and Temporal
create_db_if_not_exists "atlas"
create_db_if_not_exists "temporal"

# Grant privileges
echo "Setting up privileges..."
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE atlas TO $POSTGRES_USER;"
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE temporal TO $POSTGRES_USER;"

echo "Database initialization completed successfully!"
