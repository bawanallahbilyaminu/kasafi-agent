"""Rain-adjusted change and trends (docs/place-history.md §3).

Peak greenness is fitted against that season's rain across the plot's own years (a least-squares line). A year
is "below what the rain predicts" only when it sits more than one standard deviation of the residuals under
the line; otherwise it is normal variation. Both need at least MIN_YEARS usable years. Trends use the
Theil–Sen slope (the median of the pairwise slopes, robust to one odd year) and are worded only when the change
over the span is larger than the spread of the values around the line.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from statistics import median

MIN_YEARS = 5


@dataclass
class Fit:
    years: list[int]
    slope: float               # greenness per mm of seasonal rain
    intercept: float
    sd: float                  # residual standard deviation
    residuals: dict[int, float] = field(default_factory=dict)
    flags: dict[int, str] = field(default_factory=dict)      # year -> below | normal

    def predicted(self, rain_mm: float) -> float:
        return self.intercept + self.slope * rain_mm


def rain_fit(points: dict[int, tuple[float, float]]) -> Fit | None:
    """points: year -> (peak greenness, seasonal rain mm) for the usable years. None with fewer than MIN_YEARS."""
    years = sorted(points)
    if len(years) < MIN_YEARS:
        return None
    xs = [points[y][1] for y in years]
    ys = [points[y][0] for y in years]
    n = len(years)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
    intercept = my - slope * mx
    resid = {y: points[y][0] - (intercept + slope * points[y][1]) for y in years}
    sd = (sum(r * r for r in resid.values()) / max(n - 2, 1)) ** 0.5
    flags = {y: ("below" if sd > 1e-6 and r < -sd else "normal") for y, r in resid.items()}
    return Fit(years, slope, intercept, sd, resid, flags)


def trend(values: dict[int, float]) -> tuple[str, float] | None:
    """('rising' | 'falling' | 'no clear change', change over the span) for MIN_YEARS+ years, else None."""
    years = sorted(values)
    if len(years) < MIN_YEARS:
        return None
    slopes = [(values[b] - values[a]) / (b - a) for a, b in combinations(years, 2)]
    slope = median(slopes)
    change = slope * (years[-1] - years[0])
    mid = median([values[y] for y in years])
    line = {y: mid + slope * (y - median(years)) for y in years}
    spread = (sum((values[y] - line[y]) ** 2 for y in years) / max(len(years) - 1, 1)) ** 0.5
    if abs(change) <= spread:
        return "no clear change", change
    return ("rising" if change > 0 else "falling"), change
