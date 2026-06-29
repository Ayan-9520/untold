#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

if [ "${SEED_DATABASE}" = "true" ]; then
  echo "Seeding database..."
  python -c "from app.db.init_db import seed_database; seed_database()"
fi

echo "Starting UNTOLD API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
