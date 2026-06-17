"""
Logic engine: turns raw race rows into athlete performance metrics.

This is a DEMO stand-in for the client's proprietary blueprint. The real
formulas (the exact percentile bands, variance weighting, and penalty gates)
get dropped in here after the discovery call. The structure - pure, tested,
deterministic functions - stays the same.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Sequence


@dataclass
class RaceResult:
    athlete: str
    event: str
    date: str          # ISO yyyy-mm-dd
    time_seconds: float
    field_size: int
    placing: int


def percentile_rank(value: float, population: Sequence[float]) -> float:
    """Percent of the population at or below `value` (0-100). Lower time is better,
    so callers invert when scoring race times."""
    if not population:
        return 0.0
    below = sum(1 for p in population if p <= value)
    return round(100.0 * below / len(population), 2)


def consistency_score(times: Sequence[float]) -> float:
    """100 = perfectly consistent, falls off as relative variance grows.
    Uses coefficient of variation so it is comparable across events."""
    if len(times) < 2:
        return 100.0
    m = mean(times)
    if m == 0:
        return 0.0
    cv = pstdev(times) / m
    return round(max(0.0, 100.0 * (1 - cv)), 2)


def performance_penalty(result: RaceResult) -> float:
    """Demo conditional-gate logic. Real penalty gates come from the blueprint.
    Example gate: finishing in the bottom quartile of the field costs points,
    scaled by how deep in the field the athlete placed."""
    quartile_cut = 0.75 * result.field_size
    if result.placing <= quartile_cut:
        return 0.0
    depth = (result.placing - quartile_cut) / max(1, result.field_size - quartile_cut)
    return round(min(15.0, 15.0 * depth), 2)


def athlete_summary(results: Sequence[RaceResult]) -> dict:
    """Aggregate one athlete's results into the numbers the PDF renders."""
    times = [r.time_seconds for r in results]
    field_times = times  # in production this is the full cohort, not just one athlete
    rows = []
    for r in sorted(results, key=lambda x: x.date):
        # invert percentile so faster time => higher score
        speed_pct = 100 - percentile_rank(r.time_seconds, field_times)
        rows.append(
            {
                "date": r.date,
                "event": r.event,
                "time_seconds": r.time_seconds,
                "placing": r.placing,
                "field_size": r.field_size,
                "speed_percentile": round(speed_pct, 2),
                "penalty": performance_penalty(r),
            }
        )
    return {
        "athlete": results[0].athlete if results else "",
        "n_races": len(results),
        "best_time": min(times) if times else None,
        "consistency": consistency_score(times),
        "rows": rows,
    }
