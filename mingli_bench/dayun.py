"""Auditable Da Yun (major luck cycle) scaffolds for local reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil, floor
from typing import Any, Dict, Iterable, List, Optional

from .bazi_profile import BRANCH_POLARITY, POLARITY_LABELS, STEM_POLARITY, ten_god_for
from .calendar import BRANCH_TO_ELEMENT, STEM_TO_ELEMENT, sexagenary_index, sexagenary_name
from .chart_api import BaziChart
from .relations import analyze_branch_interactions
from .solar_terms import jie_boundaries_for_year


DAYUN_SCHEMA_VERSION = "dayun.v1"
DEFAULT_CYCLE_COUNT = 10

GENDER_ALIASES = {
    "男": "male",
    "男性": "male",
    "m": "male",
    "male": "male",
    "女": "female",
    "女性": "female",
    "f": "female",
    "female": "female",
}


@dataclass(frozen=True)
class DayunDirection:
    value: str
    step: int
    label: str


def build_dayun_analysis(
    chart: BaziChart,
    *,
    event_years: Optional[Iterable[Dict[str, Any]]] = None,
    cycle_count: int = DEFAULT_CYCLE_COUNT,
) -> Dict[str, Any]:
    """Build a deterministic Da Yun sequence and event-year overlay.

    This is a local, auditable scaffold. It uses the common rule:
    Yang-year male / Yin-year female goes forward; Yin-year male / Yang-year
    female goes backward. Starting age is approximated from the distance to the
    next/previous major solar-term boundary, using 3 days = 1 year.
    """

    gender = normalize_gender(chart.input.gender)
    year_stem = chart.pillars.year[0]
    year_polarity = STEM_POLARITY.get(year_stem)
    caveats = [
        "大运起运使用本地节气近似算法，按三天折一年估算；不同流派可能采用不同换算细节。",
        "当前未加入真太阳时、出生地经度校正和高精度星历。",
    ]

    if not gender or not year_polarity:
        missing = []
        if not gender:
            missing.append("gender")
            caveats.append("缺少性别，无法按阳男阴女/阴男阳女规则确定大运顺逆。")
        if not year_polarity:
            missing.append("year_stem_polarity")
        return {
            "schema_version": DAYUN_SCHEMA_VERSION,
            "available": False,
            "missing_inputs": missing,
            "gender": gender,
            "year_stem": year_stem,
            "year_stem_polarity": year_polarity,
            "direction": None,
            "start_timing": None,
            "cycles": [],
            "event_overlays": [],
            "caveats": caveats,
        }

    direction = dayun_direction(gender, year_polarity)
    start_timing = _start_timing(chart, direction)
    cycles = _build_cycles(chart, direction, start_timing, cycle_count)
    overlays = _build_event_overlays(chart, cycles, event_years or [])

    return {
        "schema_version": DAYUN_SCHEMA_VERSION,
        "available": True,
        "missing_inputs": [],
        "gender": gender,
        "year_stem": year_stem,
        "year_stem_polarity": year_polarity,
        "year_stem_polarity_label": POLARITY_LABELS.get(year_polarity, ""),
        "direction": direction.value,
        "direction_label": direction.label,
        "rule": "阳男阴女顺排，阴男阳女逆排",
        "start_timing": start_timing,
        "cycles": cycles,
        "event_overlays": overlays,
        "caveats": caveats,
    }


def normalize_gender(value: Optional[str]) -> Optional[str]:
    """Normalize user-facing gender strings for Da Yun direction rules."""

    if value is None:
        return None
    text = str(value).strip().lower()
    return GENDER_ALIASES.get(text)


def dayun_direction(gender: str, year_stem_polarity: str) -> DayunDirection:
    """Return Da Yun direction from normalized gender and year-stem polarity."""

    if gender not in {"male", "female"}:
        raise ValueError(f"unsupported normalized gender: {gender!r}")
    if year_stem_polarity not in {"yang", "yin"}:
        raise ValueError(f"unsupported year_stem_polarity: {year_stem_polarity!r}")
    forward = (gender == "male" and year_stem_polarity == "yang") or (
        gender == "female" and year_stem_polarity == "yin"
    )
    return DayunDirection(
        value="forward" if forward else "backward",
        step=1 if forward else -1,
        label="顺排" if forward else "逆排",
    )


def _start_timing(chart: BaziChart, direction: DayunDirection) -> Dict[str, Any]:
    birth_dt = _birth_local_datetime(chart)
    boundaries = _nearby_jie_boundaries(
        birth_dt.year,
        tz_offset_hours=float(chart.timezone.get("utc_offset_hours") or 8.0),
    )
    if direction.step > 0:
        anchor = next(item for item in boundaries if item["datetime"] > birth_dt)
        delta = anchor["datetime"] - birth_dt
        anchor_direction = "next_jie"
    else:
        anchor = next(item for item in reversed(boundaries) if item["datetime"] <= birth_dt)
        delta = birth_dt - anchor["datetime"]
        anchor_direction = "previous_jie"

    days_delta = delta.total_seconds() / 86400
    start_age_years = round(days_delta / 3, 2)
    start_age_months = int(round(start_age_years * 12))
    return {
        "method": "jie_boundary_3_days_per_year.v1",
        "birth_datetime": birth_dt.isoformat(timespec="minutes"),
        "anchor_direction": anchor_direction,
        "anchor_direction_label": "下一个节令" if anchor_direction == "next_jie" else "上一个节令",
        "anchor_term": anchor["term"],
        "anchor_datetime": anchor["datetime"].isoformat(timespec="minutes"),
        "days_delta": round(days_delta, 3),
        "start_age_years": start_age_years,
        "start_age_months": start_age_months,
    }


def _build_cycles(
    chart: BaziChart,
    direction: DayunDirection,
    start_timing: Dict[str, Any],
    cycle_count: int,
) -> List[Dict[str, Any]]:
    month_index = sexagenary_index(chart.pillars.month)
    start_age = float(start_timing["start_age_years"])
    birth_year = int(chart.solar_date[:4])
    cycles = []
    for offset in range(cycle_count):
        cycle_index = month_index + direction.step * (offset + 1)
        pillar = sexagenary_name(cycle_index)
        age_start = round(start_age + offset * 10, 2)
        age_end = round(age_start + 10, 2)
        start_year = birth_year + floor(age_start)
        end_year = birth_year + ceil(age_end) - 1
        cycles.append(
            {
                "index": offset + 1,
                "pillar": pillar,
                "stem": pillar[0],
                "branch": pillar[1],
                "stem_element": STEM_TO_ELEMENT.get(pillar[0]),
                "branch_element": BRANCH_TO_ELEMENT.get(pillar[1]),
                "stem_ten_god": ten_god_for(
                    chart.day_master,
                    STEM_TO_ELEMENT.get(pillar[0]) or "",
                    STEM_POLARITY.get(pillar[0]),
                ),
                "branch_ten_god": ten_god_for(
                    chart.day_master,
                    BRANCH_TO_ELEMENT.get(pillar[1]) or "",
                    BRANCH_POLARITY.get(pillar[1]),
                ),
                "age_start": age_start,
                "age_end": age_end,
                "approx_start_year": start_year,
                "approx_end_year": end_year,
                "branch_interactions": analyze_branch_interactions(
                    pillar[1],
                    _natal_branches(chart),
                ),
            }
        )
    return cycles


def _build_event_overlays(
    chart: BaziChart,
    cycles: List[Dict[str, Any]],
    event_years: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    birth_year = int(chart.solar_date[:4])
    overlays = []
    for event in event_years:
        year = int(event["year"])
        age = event.get("age")
        if age is None:
            age = year - birth_year
        active = _active_cycle_for_age(cycles, float(age))
        if not active:
            overlays.append(
                {
                    "year": year,
                    "age": age,
                    "year_pillar": event.get("year_pillar"),
                    "active_cycle": None,
                    "flow_to_dayun_interactions": [],
                    "note": "该年份未落入当前生成的大运范围。",
                }
            )
            continue
        flow_branch = str(event.get("branch") or str(event.get("year_pillar") or "")[1:2])
        overlays.append(
            {
                "year": year,
                "age": age,
                "year_pillar": event.get("year_pillar"),
                "active_cycle": {
                    "index": active["index"],
                    "pillar": active["pillar"],
                    "age_start": active["age_start"],
                    "age_end": active["age_end"],
                },
                "flow_to_dayun_interactions": analyze_branch_interactions(
                    flow_branch,
                    {"dayun": active["branch"]},
                )
                if flow_branch
                else [],
            }
        )
    return overlays


def _active_cycle_for_age(
    cycles: Iterable[Dict[str, Any]],
    age: float,
) -> Optional[Dict[str, Any]]:
    for cycle in cycles:
        if float(cycle["age_start"]) <= age < float(cycle["age_end"]):
            return cycle
    return None


def _birth_local_datetime(chart: BaziChart) -> datetime:
    hour = 12 if chart.input.hour is None else chart.input.hour
    return datetime.fromisoformat(f"{chart.solar_date}T{hour:02d}:{chart.input.minute:02d}:00")


def _nearby_jie_boundaries(
    year: int,
    *,
    tz_offset_hours: float,
) -> List[Dict[str, Any]]:
    boundaries = []
    for selected_year in [year - 1, year, year + 1]:
        for boundary, term, branch in jie_boundaries_for_year(
            selected_year,
            tz_offset_hours=tz_offset_hours,
        ):
            boundaries.append(
                {
                    "datetime": boundary,
                    "term": term,
                    "month_branch": branch,
                }
            )
    return sorted(boundaries, key=lambda item: item["datetime"])


def _natal_branches(chart: BaziChart) -> Dict[str, str]:
    return {
        "year": chart.pillars.year[1],
        "month": chart.pillars.month[1],
        "day": chart.pillars.day[1],
        "hour": chart.pillars.hour[1] if chart.pillars.hour else "",
    }


__all__ = [
    "DAYUN_SCHEMA_VERSION",
    "build_dayun_analysis",
    "dayun_direction",
    "normalize_gender",
]
