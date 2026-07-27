#!/usr/bin/env sh
set -eu

: "${DATABASE_URL:?set DATABASE_URL to the source PostgreSQL database}"
: "${VERIFY_DATABASE_URL:?set VERIFY_DATABASE_URL to a disposable verification database}"

if [ "$DATABASE_URL" = "$VERIFY_DATABASE_URL" ]; then
  echo "refusing to restore over the source database" >&2
  exit 2
fi

dump_path=${1:-/tmp/learning-dashboard-v14.dump}

pg_dump --format=custom --file "$dump_path" "$DATABASE_URL"
pg_restore --clean --if-exists --no-owner --no-privileges \
  --dbname "$VERIFY_DATABASE_URL" "$dump_path"

schema_present=$(psql "$VERIFY_DATABASE_URL" -Atc \
  "SELECT to_regclass('public.learners') IS NOT NULL AND to_regclass('public.auth_sessions') IS NOT NULL AND to_regclass('public.audit_events') IS NOT NULL")
constraints_present=$(psql "$VERIFY_DATABASE_URL" -Atc \
  "SELECT count(*) >= 4 FROM pg_constraint WHERE connamespace = 'public'::regnamespace")

printf '%s\n' \
  "backup_format=custom" \
  "restore_database=disposable-verification-database" \
  "schema_present=$schema_present" \
  "constraints_present=$constraints_present" \
  "restore_verified=$([ "$schema_present" = t ] && [ "$constraints_present" = t ] && printf true || printf false)"

test "$schema_present" = t
test "$constraints_present" = t
