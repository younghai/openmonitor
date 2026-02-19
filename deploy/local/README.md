# Local Docker Ops (amd64)

These scripts are for preparing and validating an amd64 image for service rollout.

## 1) Build image

```bash
cd /Users/young/Downloads/personal_project/observe/openobserve
./deploy/local/docker-build-amd64.sh
```

Optional overrides:

```bash
IMAGE_NAME=younghai/openmonitor IMAGE_TAG=v0.1.0 ./deploy/local/docker-build-amd64.sh
```

## 2) Run container

Credentials are required on first startup.
By default this also bootstraps:
- Dummy ingest data (logs/metrics/pipelines/streams/report-runs)
- Dashboard import JSON
- Report definitions JSON

```bash
cd /Users/young/Downloads/personal_project/observe/openobserve
export ZO_ROOT_USER_EMAIL="admin@your-domain.tld"
export ZO_ROOT_USER_PASSWORD="<set-a-strong-password>"
./deploy/local/docker-run.sh
```

Optional overrides:

```bash
HOST_PORT=5080 CONTAINER_NAME=openmonitor DATA_DIR="$PWD/data/openmonitor" ./deploy/local/docker-run.sh
```

Disable auto bootstrap:

```bash
AUTO_BOOTSTRAP_DUMMY=false ./deploy/local/docker-run.sh
```

## 3) Health check

```bash
cd /Users/young/Downloads/personal_project/observe/openobserve
./deploy/local/docker-healthcheck.sh
```

## 4) Verify UI and login

- URL: `http://127.0.0.1:5080`
- Login with `ZO_ROOT_USER_EMAIL` / `ZO_ROOT_USER_PASSWORD`

## Notes

- `deploy/build/Dockerfile.tag.amd64` is used by default (release-prod profile).
- `.dockerignore` is configured to reduce build context and exclude local secrets/artifacts.
- For Kubernetes, keep using secret-based auth env injection (`openobserve-auth`).
- Demo bootstrap files are in `deploy/local/bootstrap`.
