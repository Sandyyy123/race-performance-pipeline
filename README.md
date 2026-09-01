> **⚠️ Proprietary — All Rights Reserved.** © 2026 Sandeep Grover. This repository is licensed to Sandeep Grover and may **not** be used, run, copied, modified, distributed, or used to train models without prior written permission. Public visibility does not grant a license. See [LICENSE](LICENSE).

---

# Race Performance Analytics Pipeline (demo)

A backend data pipeline + PDF generation engine for sports performance analytics.
Scrapes public race results, stores them in PostgreSQL, runs them through a
pluggable scoring engine (percentiles, variance/consistency, conditional
penalty gates), and auto-generates a premium athlete PDF report.

This is a **runnable demo** built for an Upwork proposal. The proprietary
scoring math is stubbed with illustrative logic and slots into
`pipeline/logic_engine.py` after the discovery call.

## Architecture

```
 Typeform intake
        │
        ▼
 scraper.py ──(Playwright + rotating BrightData/Smartproxy pool, backoff)
        │
        ▼
 db.py ─────── PostgreSQL (Supabase / AWS RDS)  ← client runs own SQL here
        │
        ▼
 logic_engine.py ── percentiles · consistency (CoV) · penalty gates
        │
        ▼
 report.py ──── matplotlib PDF: line chart (time trend) + clustered bars
        │
        ▼
 email delivery (SMTP)
```

## Run it (zero infra)

```bash
pip install -r requirements.txt        # or run with no deps - it falls back
python main.py "Jane Athlete"
```

With no Playwright/Postgres/matplotlib installed it still runs end-to-end using
deterministic fixture data, local SQLite, and a text-report fallback - so you
can verify the full flow on any machine.

## Production wiring

| Concern        | Env var        | Notes                                          |
|----------------|----------------|------------------------------------------------|
| Database       | `DATABASE_URL` | Supabase / RDS connection string               |
| Proxy pool     | `PROXY_POOL`   | comma-separated `http://user:pass@host:port`   |
| SQLite path    | `SQLITE_PATH`  | demo fallback DB location                       |

## Modules

- `pipeline/scraper.py` - proxy-rotated, retrying scraper (Playwright)
- `pipeline/db.py` - PostgreSQL schema + upsert (SQLite fallback)
- `pipeline/logic_engine.py` - scoring math (percentiles, CoV, penalty gates)
- `pipeline/report.py` - matplotlib PDF (line + clustered bar charts)
- `main.py` - orchestrates the full flow

Dr. Sandeep Grover - PhD Data Science
