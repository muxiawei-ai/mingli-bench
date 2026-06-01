"""Stable chart-building API for application and agent integrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .bazi import bazi_from_gregorian
from .locations import resolve_timezone
from .lunar import LunarDate, normalize_lunar_date, solar_from_lunar_date
from .solar_terms import DEFAULT_TZ_OFFSET_HOURS


ChartInputLike = Union["ChartInput", Dict[str, Any]]


@dataclass(frozen=True)
class ChartInput:
    """Normalized birth-data input for chart generation."""

    calendar_type: str
    year: int
    month: int
    day: int
    hour: Optional[int] = None
    minute: int = 0
    gender: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    raw: Optional[str] = None
    is_leap_month: bool = False
    lunar_date: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "ChartInput":
        """Create ``ChartInput`` from dict-like user or benchmark data."""

        calendar_type = str(payload.get("calendar_type") or "solar").lower()
        lunar_date = payload.get("lunar_date")
        if calendar_type == "lunar" and lunar_date:
            lunar = normalize_lunar_date(str(lunar_date))
            year = lunar.year
            month = lunar.month
            day = lunar.day
            is_leap_month = lunar.is_leap_month
        else:
            year = _required_int(payload.get("year"), "year")
            month = _required_int(payload.get("month"), "month")
            day = _required_int(payload.get("day"), "day")
            is_leap_month = bool(payload.get("is_leap_month", False))

        return cls(
            calendar_type=calendar_type,
            year=year,
            month=month,
            day=day,
            hour=_optional_int(payload.get("hour"), "hour"),
            minute=_optional_int(payload.get("minute"), "minute") or 0,
            gender=payload.get("gender"),
            country=payload.get("country"),
            location=payload.get("location"),
            raw=payload.get("raw"),
            is_leap_month=is_leap_month,
            lunar_date=lunar_date,
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "calendar_type": self.calendar_type,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "gender": self.gender,
            "country": self.country,
            "location": self.location,
            "raw": self.raw,
            "is_leap_month": self.is_leap_month,
            "lunar_date": self.lunar_date,
        }


@dataclass(frozen=True)
class BaziPillars:
    """Four-pillar Bazi output."""

    year: str
    month: str
    day: str
    hour: Optional[str]

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
        }

    def display(self) -> str:
        return " ".join(
            pillar for pillar in [self.year, self.month, self.day, self.hour] if pillar
        )


@dataclass(frozen=True)
class BaziChart:
    """Stable JSON-friendly Bazi chart object."""

    input: ChartInput
    solar_date: str
    bazi_day_date: str
    pillars: BaziPillars
    day_master: str
    day_master_element: Optional[str]
    hour_branch: Optional[str]
    five_elements_summary: Dict[str, int]
    timezone: Dict[str, Any]
    lunar: Optional[Dict[str, Any]]
    warnings: List[str]
    source: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "input": self.input.as_dict(),
            "solar_date": self.solar_date,
            "bazi_day_date": self.bazi_day_date,
            "pillars": self.pillars.as_dict(),
            "pillars_text": self.pillars.display(),
            "day_master": self.day_master,
            "day_master_element": self.day_master_element,
            "hour_branch": self.hour_branch,
            "five_elements_summary": self.five_elements_summary,
            "timezone": self.timezone,
            "lunar": self.lunar,
            "warnings": self.warnings,
            "source": self.source,
        }


def _optional_int(value: Any, field_name: str) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be an integer-compatible value") from error


def _required_int(value: Any, field_name: str) -> int:
    parsed = _optional_int(value, field_name)
    if parsed is None:
        raise ValueError(f"{field_name} is required")
    return parsed


def _normalize_chart_input(payload: ChartInputLike) -> ChartInput:
    if isinstance(payload, ChartInput):
        return payload
    return ChartInput.from_mapping(payload)


def _resolve_solar_and_lunar(
    chart_input: ChartInput,
    *,
    fortune_data_path: Optional[str] = None,
) -> Dict[str, Any]:
    if chart_input.calendar_type == "solar":
        return {
            "solar_date": f"{chart_input.year:04d}-{chart_input.month:02d}-{chart_input.day:02d}",
            "lunar": None,
            "warnings": [],
            "source": "solar_input",
        }

    if chart_input.calendar_type != "lunar":
        raise ValueError(f"unsupported calendar_type: {chart_input.calendar_type!r}")

    if chart_input.lunar_date:
        lunar_source: Union[str, LunarDate] = chart_input.lunar_date
    else:
        lunar_source = LunarDate(
            chart_input.year,
            chart_input.month,
            chart_input.day,
            chart_input.is_leap_month,
        )
    lookup = solar_from_lunar_date(lunar_source, path=fortune_data_path)
    return {
        "solar_date": lookup["solar_date"],
        "lunar": lookup["lunar"],
        "warnings": ["lunar_conversion_uses_fixture_index"],
        "source": "lunar_fixture_lookup",
    }


def build_bazi_chart(
    payload: ChartInputLike,
    *,
    fortune_data_path: Optional[str] = None,
    default_tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
    zi_hour_day_rollover: bool = True,
) -> BaziChart:
    """Build a stable Bazi chart from normalized birth data.

    Lunar input currently uses the repository fixture index rather than a full
    standalone lunar calendar conversion engine.
    """

    chart_input = _normalize_chart_input(payload)
    date_resolution = _resolve_solar_and_lunar(
        chart_input,
        fortune_data_path=fortune_data_path,
    )
    timezone = resolve_timezone(
        chart_input.location,
        country=chart_input.country,
        default_tz_offset_hours=default_tz_offset_hours,
    )
    raw_chart = bazi_from_gregorian(
        date_resolution["solar_date"],
        hour=chart_input.hour,
        minute=chart_input.minute,
        tz_offset_hours=timezone.utc_offset_hours,
        zi_hour_day_rollover=zi_hour_day_rollover,
    )

    warnings = []
    warnings.extend(date_resolution["warnings"])
    warnings.extend(raw_chart["warnings"])
    warnings.extend(timezone.warnings)

    return BaziChart(
        input=chart_input,
        solar_date=str(raw_chart["solar_date"]),
        bazi_day_date=str(raw_chart["bazi_day_date"]),
        pillars=BaziPillars(
            year=str(raw_chart["year_pillar"]),
            month=str(raw_chart["month_pillar"]),
            day=str(raw_chart["day_pillar"]),
            hour=raw_chart["hour_pillar"],
        ),
        day_master=str(raw_chart["day_master"]),
        day_master_element=raw_chart["day_master_element"],
        hour_branch=raw_chart["hour_branch"],
        five_elements_summary=raw_chart["five_elements_summary"],
        timezone=timezone.as_dict(),
        lunar=date_resolution["lunar"],
        warnings=warnings,
        source=date_resolution["source"],
    )


__all__ = [
    "BaziChart",
    "BaziPillars",
    "ChartInput",
    "build_bazi_chart",
]
