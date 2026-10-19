# Local deployment and production handoff

## Local rehearsal

Use the README environment, then run:

```powershell
python -m uvicorn capstone.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/ on this computer. CAPSTONE_DB selects a database path;
the default is data/studylog.sqlite relative to the process working directory.
Use an explicit absolute path for an operational install, with read/write access
for the service identity. Existing unknown schemas are rejected rather than reset.

CAPSTONE_TOKEN, if configured, requires a private bearer token of at least 16 ASCII
characters. Supply a value you generate yourself through your host's secret
configuration; do not commit it, place it in HTML, put it in a URL or send it here.
CAPSTONE_PUBLIC=1 refuses startup without such a token. This setting does not bind
a port, provide TLS or make an unsafe host/network configuration safe automatically.
The UI token input retains it only until refresh; a remote connection needs HTTPS.

## Container recipe (optional, not required for the lessons)

The Dockerfile provides a starting recipe. Review/build it on your own machine.
The local verification runs real Uvicorn processes; it does not claim Docker was
executed on a machine where no Docker daemon was available.

```text
docker build -t studylog-capstone .
docker volume create studylog-data
docker run --rm -p 127.0.0.1:8000:8000 -v studylog-data:/app/data studylog-capstone
```

The container binds internally to 0.0.0.0; the host mapping confines this recipe
to localhost. Removing that host restriction is a separate exposure decision.
Keep data on the named volume; rebuilding an image is not a database backup.

## Public or second-device verification: manual handoff

Choose a Python-capable host or a private machine you control. Configure persistent
storage, a service account, a secret, HTTPS and a deliberately restricted network
route. With a reverse proxy, configure only trusted forwarding addresses and check
the external scheme/host used by same-origin requests. Avoid trusting arbitrary
forwarded headers from untrusted clients. Do not run a debug/reload server publicly.

Before calling it production: verify health, authenticated create/read/update,
conflict behavior, restart persistence and restoration with synthetic records;
check access denial from an unauthenticated client; inspect logs without secrets;
set request/body/rate limits at the front door; document who can access the service,
how to rotate the shared token, and how to roll back code without erasing data.
The application limits record fields, but does not itself impose a global transport
body-size limit. Multi-user identity/authorization needs a separate design.

For the curriculum's second-device milestone, run those acceptance actions from a
different device after intentional private/remote setup and record the observed
URL/environment and results yourself. A local TestClient or localhost browser
does not establish a real second-device or public deployment result.

## Backup and restore rehearsal

Stop making changes while you perform a practice restore. Create a new snapshot:

```text
python -m capstone.backup data/studylog.sqlite artifacts/studylog-backup.sqlite
```

Choose a new destination each time. Keep a protected copy on a different failure
domain for real use. Verify its integrity and open it in a separate rehearsal
instance using CAPSTONE_DB before changing an operational database path. Restore
means checking actual useful records, not only seeing a successful copy message.
The helper assumes you control the destination directory and no competing process
is racing to create that new backup filename. It is not a remote backup service.
