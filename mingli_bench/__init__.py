"""MingLi Bench: Chinese metaphysics benchmark and chart utilities."""

__version__ = "0.1.0"

from .agent import AgentResult, MingLiAgent, build_interpretation_prompt
from .calendar import hour_branch, parse_bazi_pillars
from .charts import get_chart_summary
from .chart_api import BaziChart, BaziPillars, ChartInput, build_bazi_chart
from .bazi import (
    bazi_from_birth_info,
    bazi_from_gregorian,
    day_pillar_for_date,
    hour_pillar_for_datetime,
    month_pillar_for_datetime,
    year_pillar_for_date,
    year_pillar_for_datetime,
)
from .locations import resolve_timezone
from .lunar import (
    LunarDate,
    lunar_from_solar_date,
    parse_chinese_lunar_date,
    solar_from_lunar_date,
)
from .option_semantics import analyze_option_semantics, extract_options
from .relations import analyze_branch_interactions
from .solar_terms import solar_month_branch_for_datetime, solar_term_datetime

__all__ = [
    "FortuneTellingBenchmark",
    "BaziChart",
    "BaziPillars",
    "ChartInput",
    "LunarDate",
    "AgentResult",
    "ModelClient",
    "MingLiAgent",
    "analyze_branch_interactions",
    "analyze_option_semantics",
    "bazi_from_birth_info",
    "bazi_from_gregorian",
    "build_bazi_chart",
    "build_interpretation_prompt",
    "day_pillar_for_date",
    "extract_options",
    "get_chart_summary",
    "hour_branch",
    "hour_pillar_for_datetime",
    "month_pillar_for_datetime",
    "parse_bazi_pillars",
    "parse_chinese_lunar_date",
    "resolve_timezone",
    "lunar_from_solar_date",
    "solar_month_branch_for_datetime",
    "solar_term_datetime",
    "solar_from_lunar_date",
    "year_pillar_for_date",
    "year_pillar_for_datetime",
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
