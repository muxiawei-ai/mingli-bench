"""MingLi Bench: Chinese metaphysics benchmark and chart utilities."""

__version__ = "1.0.0"

from .calendar import hour_branch, parse_bazi_pillars
from .charts import get_chart_summary
from .bazi import bazi_from_gregorian, day_pillar_for_date, hour_pillar_for_datetime, year_pillar_for_date

__all__ = [
    "FortuneTellingBenchmark",
    "ModelClient",
    "bazi_from_gregorian",
    "day_pillar_for_date",
    "get_chart_summary",
    "hour_branch",
    "hour_pillar_for_datetime",
    "parse_bazi_pillars",
    "year_pillar_for_date",
]


def __getattr__(name):
    """Lazy-load heavier benchmark classes only when requested."""

    if name == "FortuneTellingBenchmark":
        from .benchmark import FortuneTellingBenchmark

        return FortuneTellingBenchmark
    if name == "ModelClient":
        from .models.base import ModelClient

        return ModelClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
