#!/usr/bin/env bash
set -eu
# Only runs for a fresh named volume. Never enable shell tracing here.
RUNTIME_DB_PASSWORD="$(cat /run/secrets/runtime_db_password)"
MIGRATION_DB_PASSWORD="$(cat /run/secrets/migration_db_password)"
export RUNTIME_DB_PASSWORD MIGRATION_DB_PASSWORD
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv runtime_password RUNTIME_DB_PASSWORD
\getenv migration_password MIGRATION_DB_PASSWORD
CREATE ROLE studyhub_runtime LOGIN PASSWORD :'runtime_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE studyhub_migrator LOGIN PASSWORD :'migration_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER SCHEMA public OWNER TO studyhub_migrator;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO studyhub_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE studyhub_migrator IN SCHEMA public GRANT SELECT,INSERT,UPDATE,DELETE ON TABLES TO studyhub_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE studyhub_migrator IN SCHEMA public GRANT USAGE,SELECT ON SEQUENCES TO studyhub_runtime;
SQL
unset RUNTIME_DB_PASSWORD MIGRATION_DB_PASSWORD
