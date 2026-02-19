# Demo Bootstrap

`seed_demo_content.py` seeds OpenObserve with demo content so dashboards/reports are visible immediately after startup.

It performs:
- fresh dummy data generation with current timestamps
- logs/metrics ingest for demo streams
- dashboard import (`multimenu_observability_dashboard_v5.json`)
- report upsert (`reports_seed.json`)

## Manual run

```bash
cd /Users/young/Downloads/personal_project/observe/openobserve
OPENOBSERVE_URL=http://127.0.0.1:5080 \
OPENOBSERVE_ORG=default \
ZO_ROOT_USER_EMAIL=admin@your-domain.tld \
ZO_ROOT_USER_PASSWORD='<set-a-strong-password>' \
./deploy/local/bootstrap/seed_demo_content.py
```

## Optional env

- `FORCE_RESEED=true` : delete existing matching dashboard first
- `REPORT_RECIPIENT=someone@example.com` : report email destination
- `OPENOBSERVE_TZ=UTC` and `OPENOBSERVE_TZ_OFFSET=0`
