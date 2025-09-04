#!/bin/sh
set -e

# Wait for Postgres to be ready
echo "Waiting for Postgres..."
until pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI..."
exec "$@"