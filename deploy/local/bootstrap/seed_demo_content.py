#!/usr/bin/env python3
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DASHBOARD_FILE = DATA_DIR / "multimenu_observability_dashboard_v5.json"
REPORTS_FILE = DATA_DIR / "reports_seed.json"


OO_URL = os.getenv("OPENOBSERVE_URL", "http://127.0.0.1:5080").rstrip("/")
OO_ORG = os.getenv("OPENOBSERVE_ORG", "default")
OO_USER = os.getenv("ZO_ROOT_USER_EMAIL", "")
OO_PASS = os.getenv("ZO_ROOT_USER_PASSWORD", "")
REPORT_RECIPIENT = os.getenv("REPORT_RECIPIENT", OO_USER)
FORCE_RESEED = os.getenv("FORCE_RESEED", "false").lower() == "true"
TZ_NAME = os.getenv("OPENOBSERVE_TZ", "UTC")
TZ_OFFSET = int(os.getenv("OPENOBSERVE_TZ_OFFSET", "0"))

DASHBOARD_TITLE = "Multi-Menu Observability Dashboard"


def fail(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(1)


def require_env() -> None:
    if not OO_USER:
        fail("Set ZO_ROOT_USER_EMAIL")
    if not OO_PASS:
        fail("Set ZO_ROOT_USER_PASSWORD")
    if not DASHBOARD_FILE.exists():
        fail(f"Missing dashboard seed file: {DASHBOARD_FILE}")
    if not REPORTS_FILE.exists():
        fail(f"Missing reports seed file: {REPORTS_FILE}")


def api_request(method: str, path: str, payload=None):
    url = f"{OO_URL}{path}"
    auth = base64.b64encode(f"{OO_USER}:{OO_PASS}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8") if resp.length != 0 else ""
            body = {}
            if raw:
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    body = {"raw": raw}
            return resp.status, body
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        body = {"raw": raw}
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            pass
        return e.code, body


def write_json(path: Path, records):
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"))


def generate_dummy_data():
    now_us = int(time.time() * 1_000_000)
    now_s = now_us // 1_000_000

    logs = []
    for i in range(1, 361):
        ts = now_us - (360 - i) * 10_000_000
        levels = ["INFO", "WARN", "ERROR", "DEBUG"]
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        services = ["gateway", "auth", "orders", "billing"]
        level = levels[i % 4]
        method = methods[i % 5]
        svc = services[i % 4]
        logs.append(
            {
                "_timestamp": ts,
                "level": level,
                "service": svc,
                "method": method,
                "kubernetes_pod_name": f"{svc}-pod-{i % 7 + 1}",
                "kubernetes_host": f"log-node-{i % 3 + 1}",
                "message": f"logs-menu dummy event {i}",
                "log": f"[{level}] {method} /api/{svc} req={i}",
                "code": (i % 5) * 100 + 200,
                "took": i % 250 + 5,
            }
        )

    pipelines = []
    for i in range(1, 241):
        ts = now_us - (240 - i) * 15_000_000
        names = [
            "ingest-normalizer",
            "security-redaction",
            "geoip-enrichment",
            "alerts-fanout",
        ]
        status = "success"
        if i % 10 in (6, 7):
            status = "running"
        elif i % 10 == 8:
            status = "retry"
        elif i % 10 == 9:
            status = "failed"
        pipelines.append(
            {
                "_timestamp": ts,
                "pipeline_name": names[i % 4],
                "status": status,
                "processed_records": 1000 + (i % 40) * 120,
                "duration_ms": 40 + (i % 35) * 15,
                "error_count": (i % 5 + 1) if status == "failed" else (1 if status == "retry" else 0),
                "env": "prod",
            }
        )

    streams = []
    for i in range(1, 181):
        ts = now_us - (180 - i) * 20_000_000
        names = [
            "logs_app_demo",
            "infra_metrics_demo",
            "pipeline_events_demo",
            "report_runs_demo",
            "audit_trail_demo",
        ]
        tiers = ["hot", "warm", "cold"]
        streams.append(
            {
                "_timestamp": ts,
                "stream_name": names[i % 5],
                "tier": tiers[i % 3],
                "ingest_mb": 20 + (i % 50) * 3,
                "doc_count": 5000 + (i % 80) * 100,
                "index_latency_ms": 10 + (i % 20) * 2,
            }
        )

    reports = []
    for i in range(1, 121):
        ts = now_us - (120 - i) * 30_000_000
        names = [
            "daily-ops-summary",
            "pipeline-health-report",
            "sla-weekly-report",
            "security-audit-report",
        ]
        if i % 8 in (6,):
            status = "queued"
        elif i % 8 in (7,):
            status = "failed"
        else:
            status = "delivered"
        formats = ["pdf", "xlsx", "csv"]
        reports.append(
            {
                "_timestamp": ts,
                "report_name": names[i % 4],
                "status": status,
                "duration_sec": 8 + (i % 18),
                "size_kb": 120 + (i % 40) * 15,
                "format": formats[i % 3],
                "recipient": "ops-team@example.com",
            }
        )

    metrics = []
    for i in range(1, 361):
        ts = now_s - (360 - i) * 10
        host = f"mnode-{i % 3 + 1}"
        cpu = round(45 + (i % 30) * 1.3, 2)
        mem = round(52 + (i % 25) * 1.1, 2)
        req = round(120 + (i % 40) * 2.4, 2)
        metrics.append(
            {
                "__name__": "infra_metrics_demo",
                "__type__": "gauge",
                "metric": "cpu_usage",
                "host": host,
                "service": "api",
                "_timestamp": ts,
                "value": cpu,
            }
        )
        metrics.append(
            {
                "__name__": "infra_metrics_demo",
                "__type__": "gauge",
                "metric": "memory_usage",
                "host": host,
                "service": "api",
                "_timestamp": ts,
                "value": mem,
            }
        )
        metrics.append(
            {
                "__name__": "infra_metrics_demo",
                "__type__": "counter",
                "metric": "request_rate",
                "host": host,
                "service": "api",
                "_timestamp": ts,
                "value": req,
            }
        )

    write_json(DATA_DIR / "logs_menu_dummy.json", logs)
    write_json(DATA_DIR / "pipelines_menu_dummy.json", pipelines)
    write_json(DATA_DIR / "streams_menu_dummy.json", streams)
    write_json(DATA_DIR / "reports_menu_dummy.json", reports)
    write_json(DATA_DIR / "metrics_menu_dummy.json", metrics)
    print("[ok] generated fresh dummy datasets")


def ingest_dummy_data():
    ingest_jobs = [
        (f"/api/{OO_ORG}/logs_menu_demo/_json", DATA_DIR / "logs_menu_dummy.json"),
        (f"/api/{OO_ORG}/pipeline_events_demo/_json", DATA_DIR / "pipelines_menu_dummy.json"),
        (f"/api/{OO_ORG}/stream_inventory_demo/_json", DATA_DIR / "streams_menu_dummy.json"),
        (f"/api/{OO_ORG}/report_runs_demo/_json", DATA_DIR / "reports_menu_dummy.json"),
        (f"/api/{OO_ORG}/ingest/metrics/_json", DATA_DIR / "metrics_menu_dummy.json"),
    ]
    for endpoint, file_path in ingest_jobs:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        status, body = api_request("POST", endpoint, payload)
        if status not in (200, 201, 202):
            fail(f"ingest failed {endpoint}: status={status}, body={body}")
    print("[ok] ingested dummy logs/metrics streams")


def ensure_dashboard():
    title_query = urllib.parse.quote(DASHBOARD_TITLE)
    status, body = api_request("GET", f"/api/{OO_ORG}/dashboards?title={title_query}")
    if status != 200:
        fail(f"list dashboards failed: status={status}, body={body}")
    dashboards = body.get("dashboards", [])
    matches = [d for d in dashboards if d.get("title") == DASHBOARD_TITLE]

    if matches and FORCE_RESEED:
        for d in matches:
            dashboard_id = d.get("dashboard_id")
            if dashboard_id:
                api_request("DELETE", f"/api/{OO_ORG}/dashboards/{urllib.parse.quote(dashboard_id)}")
        matches = []

    if not matches:
        dashboard_payload = json.loads(DASHBOARD_FILE.read_text(encoding="utf-8"))
        status, body = api_request("POST", f"/api/{OO_ORG}/dashboards", dashboard_payload)
        if status not in (200, 201):
            fail(f"create dashboard failed: status={status}, body={body}")
        status, body = api_request("GET", f"/api/{OO_ORG}/dashboards?title={title_query}")
        if status != 200:
            fail(f"re-list dashboards failed: status={status}, body={body}")
        matches = [d for d in body.get("dashboards", []) if d.get("title") == DASHBOARD_TITLE]
        if not matches:
            fail("dashboard created but not found in list")

    dash = matches[0]
    print(f"[ok] dashboard ready: {dash.get('dashboard_id')} ({dash.get('folder_id')})")
    return dash.get("dashboard_id"), dash.get("folder_id")


def ensure_reports(dashboard_id: str, folder_id: str):
    templates = json.loads(REPORTS_FILE.read_text(encoding="utf-8"))
    now_us = int(time.time() * 1_000_000)

    for tmpl in templates:
        report_name = tmpl["name"]
        tab = tmpl.get("tab", "logs")
        period = tmpl.get("period", "30m")
        destinations = tmpl.get("destinations", [])
        for dest in destinations:
            email = dest.get("email")
            if email == "__REPORT_RECIPIENT__":
                dest["email"] = REPORT_RECIPIENT

        payload = {
            "name": report_name,
            "title": tmpl.get("title", report_name),
            "description": tmpl.get("description", ""),
            "orgId": OO_ORG,
            "dashboards": [
                {
                    "folder": folder_id,
                    "dashboard": dashboard_id,
                    "tabs": [tab],
                    "variables": [],
                    "timerange": {
                        "type": "relative",
                        "period": period,
                        "from": 0,
                        "to": 0,
                    },
                }
            ],
            "destinations": destinations,
            "enabled": tmpl.get("enabled", True),
            "media_type": "Pdf",
            "message": "Auto-seeded demo report",
            "start": now_us,
            "frequency": tmpl.get("frequency", {"type": "hours", "interval": 1, "cron": ""}),
            "timezone": TZ_NAME,
            "timezoneOffset": TZ_OFFSET,
            "owner": OO_USER,
            "lastEditedBy": OO_USER,
        }

        path_name = urllib.parse.quote(report_name, safe="")
        exists_status, _ = api_request("GET", f"/api/{OO_ORG}/reports/{path_name}")
        if exists_status == 200:
            status, body = api_request("PUT", f"/api/{OO_ORG}/reports/{path_name}", payload)
            action = "updated"
        else:
            status, body = api_request("POST", f"/api/{OO_ORG}/reports", payload)
            action = "created"

        if status not in (200, 201):
            fail(f"report {action} failed for {report_name}: status={status}, body={body}")
        print(f"[ok] report {action}: {report_name}")

    status, body = api_request("GET", f"/api/{OO_ORG}/reports")
    if status != 200:
        fail(f"list reports failed: status={status}, body={body}")
    print(f"[ok] reports in org '{OO_ORG}': {len(body) if isinstance(body, list) else 'unknown'}")


def main():
    require_env()
    generate_dummy_data()
    ingest_dummy_data()
    dashboard_id, folder_id = ensure_dashboard()
    ensure_reports(dashboard_id, folder_id)
    print("[done] dashboard + reports + dummy ingest bootstrap completed")


if __name__ == "__main__":
    main()
