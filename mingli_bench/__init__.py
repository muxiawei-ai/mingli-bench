"""MingLi Bench: Chinese metaphysics benchmark and chart utilities."""

__version__ = "1.0.0"

from .calendar import hour_branch, parse_bazi_pillars
from .charts import get_chart_summary

__all__ = [
    "FortuneTellingBenchmark",
    "ModelClient",
    "get_chart_summary",
    "hour_branch",
    "parse_bazi_pillars",
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
