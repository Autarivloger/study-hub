# Week 42 — Docker & deployment

A separate continuation of the Week 41 Notes API, with the same account/owned-note API and local explorer, plus container packaging and PostgreSQL operations. Use fictional practice accounts and **fresh Week42 storage**. This folder does not read or migrate Study Hub browser progress or your older API instance.

## What you learn

| Day | Focus | Outcome |
|---|---|---|
| 1 | Container mental model, processes, files, ports and lifecycle | Explain what an image packages and what a running container still needs |
| 2 | Dockerfile, context, cache, stages, runtime user and configuration | Review and build the API artifact |
| 3 | Compose, PostgreSQL, service networking, roles, secrets and readiness | Operate a repeatable local stack with persistent data |
| 4 | Static hosting, PaaS, VPS, functions and managed databases | Write a defensible deployment decision record |
| 5 | Release identity, runtime configuration, migration, DNS/TLS and smoke checks | Follow an ordered staging release and rollback plan |
| 6 | HTTPS, backup/restore, monitoring, scaling, budget and runbooks | Collect honest operational evidence |

Each day has six parts in Study Hub. Python outputs in lessons are executed against temporary owned copies. Terminal panes are actual commands to run with Docker/provider access, **not fabricated terminal output**. The website remains readable offline. Installing tools/images initially and deploying a service require network access.

## Local Python checks first

Create a virtual environment if needed, activate it, then run each line separately from this folder:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python app.py
```

The local teaching server binds to `127.0.0.1:8002`, uses its own SQLite `instance/`, and serves the authored explorer at `/docs`. Ctrl+C stops it. Tests use disposable temporary folders, never that local instance. The container runtime is a different path described below.

## Run the actual Docker stack

Install/start a suitable Docker Engine or Docker Desktop with Linux containers and the current Compose plugin. Check its current licensing/system requirements yourself. No Docker daemon is needed just to read the course or run the local Python tests.

```powershell
docker version
docker compose version
python ops.py init-secrets
docker compose config --quiet
docker compose up --build -d --wait api
docker compose ps
```

Open **http://127.0.0.1:8042/docs**. The initial build downloads the Python base and dependencies; PostgreSQL is also pulled. The first startup creates an empty Week42 database, restricted roles and then applies `w42_001` through `w42_003` once via `migrate`. The API checks the expected head, rather than every web process migrating concurrently.

`ops.py init-secrets` generates four random local files, never prints their values, and **does not overwrite existing files**. `.secrets/` and backups/instance/cache paths are Git-ignored and outside the Docker context allowlist. On POSIX, the directory is owner-only; files are readable bind secrets for the non-root container UID. On Windows, protect the directory with your account's filesystem access controls. Compose file secrets are not an encrypted secret vault.

The secret sources are `owner_db_password`, `runtime_db_password`, `migration_db_password` and `jwt_secret`. Only the database bootstrap receives its owner password. Normal API requests use `studyhub_runtime`, which has data permissions but cannot create schema objects. `studyhub_migrator` owns controlled migrations. Role initialization only runs on a **new** PostgreSQL volume; replacing a password file does not update a role already stored in the database.

### Service boundaries

* `db`: PostgreSQL 17 on the private backend network, durable `pg_data` volume, no published host port.
* `migrate`: same API image, different restricted credentials, runs `python manage.py upgrade` and exits. API startup waits for successful completion.
* `api`: non-root UID/GID 10001, read-only root, writable temporary `/tmp`, one Uvicorn worker, container port 8002 mapped to **host loopback** 8042.

The browser uses host port 8042. API-to-database traffic uses `db:5432`. `EXPOSE` is documentation; it does not publish a port. Your phone's localhost is your phone, so the local loopback URL is not the public-host exercise.

```powershell
docker compose logs --tail 30 api
docker compose stop
docker compose start
```

Ordinary stopping keeps the database volume. Do not use a volume-removing shutdown for data you want to keep. The GitHub workflow removes only its owned throwaway runner volume after its checks.

## What is actually tested

`.github/workflows/python-week42.yml` installs pinned tools, runs isolated Python tests/lint/format checks, builds the real Dockerfile, starts PostgreSQL/migrations/API and runs `container_smoke.py`. That script is intended for a **fresh disposable stack**, because it creates a fixed fictional account and restore database. It verifies:

1. Live and database-ready endpoints.
2. Registration, login, authenticated note creation/read and anonymous rejection.
3. Runtime UID, non-superuser role and denied schema-creation privilege.
4. No `.key` or `.secrets` folder embedded under `/app` (runtime `/run/secrets` mounts are intentional).
5. API recreation retains note data and the valid login.
6. Database outage changes readiness to 503 while liveness stays 200; recovery restores service.
7. A custom PostgreSQL dump restores into a **different** database, with correct note count and schema head.

A workflow file is not evidence of a successful run. Inspect the result for the exact commit you intend to use. The authoring Windows host has no Docker daemon; container evidence is collected by the GitHub runner. Python/test-client evidence and public HTTPS evidence remain distinct.

## Backup and separate restore rehearsal

These commands target only this lab's Compose project. Keep the source database intact:

```powershell
docker compose exec -T db pg_dump -U studyhub_owner -d studyhub -Fc -f /tmp/week42.dump
python -c "from pathlib import Path; Path('backups').mkdir(exist_ok=True)"
docker compose cp db:/tmp/week42.dump ./backups/week42.dump
```

Treat dumps as private. Copy an encrypted/protected recovery copy to independent storage with appropriate retention. The command writes a binary file inside the container before copying it, avoiding binary stdout-redirection pitfalls in older PowerShell.

On a fresh drill, choose a separate database name that does not already exist:

```powershell
docker compose exec -T db createdb -U studyhub_owner -O studyhub_migrator studyhub_restore
docker compose exec -T db pg_restore -U studyhub_owner --role studyhub_migrator --no-owner -d studyhub_restore /tmp/week42.dump
docker compose exec -T db psql -U studyhub_owner -d studyhub_restore -c "SELECT count(*) FROM notes"
docker compose exec -T db psql -U studyhub_owner -d studyhub_restore -c "SELECT version_num FROM alembic_version"
```

If the drill name already exists, **stop and pick another owned target**, rather than dropping an unknown database. Validate representative data and permissions, not only file existence. A database-only backup does not replace the secure recovery plan for required runtime secrets, roles, provider configuration and release identity.

## Ordered public staging deployment checklist

This is a manual exercise on an account and budget you choose. It does not create a host, DNS record, monitoring subscription or paid resource automatically.

1. Review current provider Docker runtime, region, port, health, migration-job and billing capabilities. Compare total app/database/storage/backup/log/egress cost. The course's cost numbers are fictional arithmetic inputs.
2. A managed Docker web service plus managed PostgreSQL is the demonstrated first-staging shape. Render's FastAPI/Docker documentation is a concrete reference, not a free-plan guarantee. VPS and function hosts have different operating/invocation responsibilities.
3. Select the repository and **root directory `docs/python-week42`**. Use its Dockerfile. Record source commit and the resulting immutable image identity where the platform exposes it; minor-version image tags in the local lab are mutable.
4. Provision a **fresh staging PostgreSQL** database in an appropriate region. Establish a restricted runtime role and a migration identity. Apply equivalent privileges to this lab using your provider's supported admin tools; do not merely use its default superuser everywhere.
5. In private runtime settings, configure `APP_ENV=production`, an externally generated signing secret using `API_JWT_SECRET` or a supported `API_JWT_SECRET_FILE`, and a restricted `DATABASE_URL` (`postgresql://` normalises to the psycopg dialect). Keep passwords out of Git, images, screenshots and lesson notes. Follow provider-verified TLS/CA requirements; do not copy local Compose's `DB_SSLMODE=disable` into a public database URL.
6. Confirm the provider's `PORT` contract and that the container listens on `0.0.0.0` internally. Configure `/health/ready` as readiness where supported. Runtime settings reject invalid ports and missing production signing material.
7. Run **one** controlled pre-deploy/one-off `python manage.py upgrade` with migration credentials, where the selected plan supports that capability. Verify the resulting head. Then start API workers with runtime credentials. If no controlled job facility is available, arrange one through the provider's supported administrative procedure before routing traffic; do not race migrations in every worker.
8. The image runs `python server.py`. Its default forwarded-header trust is loopback only. Review your platform's actual proxy addresses and configure an appropriate explicit trust policy before depending on forwarded protocol/client data. A wildcard trust is not a substitute for that review.
9. Verify the provider's HTTPS URL first. For a custom hostname, configure the exact A/AAAA/CNAME record that provider requires, verify certificate issuance and renewal, and confirm routing/readiness. DNS does not start the Python process or forward an arbitrary port.
10. From your phone or another network, use fictional staging accounts to check HTTPS, readiness, registration/login, authorised owned-note CRUD, anonymous rejection and cross-user denial. Never put a bearer token in a query string or public evidence file. Record statuses and redacted outcomes.
11. Before promotion, retain a compatible previous artifact and a reviewed recovery plan. Schema/data recovery is separate from code rollback; rehearse expand/contract changes and restore before a destructive migration.
12. Configure actual external uptime checks, bounded timeouts, thresholds, a notification recipient and an incident owner. Test alert/recovery. A Docker healthcheck alone is not human notification. Set a verified budget policy, retention limits and a maintenance/secret-rotation schedule.

### Public-use limits

This is a deployment learning project, not a complete public account product. The app still needs an appropriate edge/request-size policy, login abuse/rate controls, account recovery policy, provider-specific proxy hardening and real operational review before accepting personal production data. `APP_ENV=production` enforces configuration rules; it does not add those facilities or HTTPS automatically. Keep the course's staging exercise fictional until those concrete gaps are addressed.

## Evidence record

Record source revision, image identity, schema head, test/build/container results, restore validation, selected host configuration version, redacted external-device smoke results and incident/cost ownership. Mark unperformed checks pending. Do not invent a public URL or treat local TestClient output as public deployment evidence.

Primary references: [Docker overview](https://docs.docker.com/get-started/docker-overview/), [Docker build practices](https://docs.docker.com/build/building/best-practices/), [Compose startup conditions](https://docs.docker.com/compose/how-tos/startup-order/), [Compose secrets](https://docs.docker.com/compose/how-tos/use-secrets/), [FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/), [PostgreSQL backup](https://www.postgresql.org/docs/17/backup-dump.html), [Render FastAPI deployment](https://render.com/docs/deploy-fastapi).
