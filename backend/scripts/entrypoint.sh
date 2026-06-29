#!/bin/sh
set -e

# Only the API service runs migrations (avoids race when celery starts in parallel)
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head

  if [ "${SEED_DATABASE}" = "true" ]; then
    echo "Seeding database..."
    python -c "from app.db.init_db import seed_database; seed_database()"
  fi
fi

# Celery worker / beat pass their command as arguments
if [ $# -gt 0 ]; then
  exec "$@"
fi

echo "Starting UNTOLD API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
