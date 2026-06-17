"""
PDF report generator.

Builds a premium athlete report: a chronological line chart of race times and
a clustered bar chart of speed-percentile vs penalty per race, plus a summary
header. Uses matplotlib (Agg backend, no display needed). Falls back to a text
report if matplotlib is unavailable so the pipeline never hard-fails.
"""
from __future__ import annotations

from typing import Optional


def build_report(summary: dict, out_path: str = "athlete_report.pdf") -> str:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except Exception:
        return _text_fallback(summary, out_path.replace(".pdf", ".txt"))

    rows = summary["rows"]
    dates = [r["date"] for r in rows]
    times = [r["time_seconds"] for r in rows]
    pcts = [r["speed_percentile"] for r in rows]
    penalties = [r["penalty"] for r in rows]

    with PdfPages(out_path) as pdf:
        # Page 1 - header + chronological line chart
        fig, ax = plt.subplots(figsize=(8.27, 5.5))
        ax.plot(dates, times, marker="o", color="#6c5ce7", linewidth=2)
        ax.set_title(
            f"{summary['athlete']} - Race Time Trend "
            f"(consistency {summary['consistency']})"
        )
        ax.set_ylabel("Time (s) - lower is better")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2 - clustered bar chart: speed percentile vs penalty
        import numpy as np

        fig, ax = plt.subplots(figsize=(8.27, 5.5))
        x = np.arange(len(dates))
        w = 0.4
        ax.bar(x - w / 2, pcts, w, label="Speed percentile", color="#00b894")
        ax.bar(x + w / 2, penalties, w, label="Penalty", color="#d63031")
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha="right")
        ax.set_title(f"{summary['athlete']} - Per-Race Scoring")
        ax.legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return out_path


def _text_fallback(summary: dict, out_path: str) -> str:
    lines = [
        f"Athlete: {summary['athlete']}",
        f"Races: {summary['n_races']}  Best: {summary['best_time']}  "
        f"Consistency: {summary['consistency']}",
        "",
        "date        event    time     pct    penalty",
    ]
    for r in summary["rows"]:
        lines.append(
            f"{r['date']}  {r['event']:<7} {r['time_seconds']:>7.1f}  "
            f"{r['speed_percentile']:>5}  {r['penalty']:>5}"
        )
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    return out_path
