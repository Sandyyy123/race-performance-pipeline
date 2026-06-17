"""
End-to-end runnable entry point:

    Typeform intake  ->  scrape (proxy-rotated)  ->  store in PostgreSQL
                      ->  logic engine (percentiles/variance/penalties)
                      ->  premium PDF  ->  email delivery

Run with no infra:   python main.py "Jane Athlete"
It will use deterministic fixture data, write to local SQLite, and produce a
PDF (or text fallback). Wire DATABASE_URL + PROXY_POOL + SMTP creds for prod.
"""
from __future__ import annotations

import sys

from pipeline.scraper import scrape_athlete
from pipeline.db import connect, init_db, upsert_results
from pipeline.logic_engine import athlete_summary
from pipeline.report import build_report


def run(athlete: str) -> str:
    print(f"[1/4] scraping {athlete} ...")
    results = scrape_athlete(athlete)
    print(f"      got {len(results)} rows")

    print("[2/4] storing in database ...")
    conn = connect()
    init_db(conn)
    inserted = upsert_results(conn, results)
    print(f"      {inserted} new rows")

    print("[3/4] running logic engine ...")
    summary = athlete_summary(results)
    print(
        f"      best={summary['best_time']}  consistency={summary['consistency']}"
    )

    print("[4/4] building PDF report ...")
    path = build_report(summary, out_path=f"{athlete.replace(' ', '_')}_report.pdf")
    print(f"      wrote {path}")
    # send_email(to=..., attachment=path)  # SMTP wired in production
    return path


if __name__ == "__main__":
    athlete = sys.argv[1] if len(sys.argv) > 1 else "Jane Athlete"
    run(athlete)
