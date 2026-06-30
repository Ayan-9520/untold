#!/bin/sh
# Restore PostgreSQL from gzip dump — DESTRUCTIVE
set -eu

if [ $# -lt 1 ]; then
  echo "Usage: restore.sh /backups/untold_YYYYMMDD_HHMMSS.sql.gz"
  exit 1
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
  echo "Backup file not found: $FILE"
  exit 1
fi

echo "[restore] WARNING: This will replace database ${PGDATABASE:-untold_db}"
echo "[restore] Restoring from $FILE"

gunzip -c "$FILE" | PGPASSWORD="${PGPASSWORD}" psql \
  -h "${PGHOST:-db}" -p "${PGPORT:-5432}" -U "${PGUSER:-untold}" -d "${PGDATABASE:-untold_db}" \
  --single-transaction --set ON_ERROR_STOP=on

echo "[restore] Complete"
