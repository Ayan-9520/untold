#!/bin/sh
# PostgreSQL backup — local retention + optional S3 upload
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="${BACKUP_DIR}/untold_${TIMESTAMP}.sql.gz"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"

echo "[backup] Starting pg_dump -> $FILE"
PGHOST="${PGHOST:-db}" PGPORT="${PGPORT:-5432}" PGUSER="${PGUSER:-untold}" PGDATABASE="${PGDATABASE:-untold_db}" \
  pg_dump --no-owner --no-acl | gzip > "$FILE"

SIZE=$(du -h "$FILE" | cut -f1)
echo "[backup] Completed ${SIZE}"

find "$BACKUP_DIR" -name 'untold_*.sql.gz' -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
echo "[backup] Retention applied (${RETENTION_DAYS} days)"

if [ -n "${BACKUP_S3_URI:-}" ]; then
  if command -v aws >/dev/null 2>&1; then
    echo "[backup] Uploading to ${BACKUP_S3_URI}"
    aws s3 cp "$FILE" "${BACKUP_S3_URI}/$(basename "$FILE")"
    echo "[backup] S3 upload complete"
  else
    echo "[backup] WARN: BACKUP_S3_URI set but aws CLI not available"
  fi
fi
