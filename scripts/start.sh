#!/bin/bash
set -e

# Run migrations
alembic upgrade head

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 