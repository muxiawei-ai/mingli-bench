"""Utilities for working with pre-computed Bazi and Ziwei chart fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from .calendar import parse_bazi_pillars
from .lunar import parse_chinese_lunar_date
from .utils.path_utils import find_data_file


PathLike = Union[str, Path]


def load_fortune_records(path: Optional[PathLike] = None) -> List[Dict[str, Any]]:
    """Load ``fortune_api_results.json`` records."""

    resolved_path = Path(path) if path else find_data_file("fortune_api_results.json")
    if resolved_path is None:
        resolved_path = Path("data/fortune_api_results.json")
    if not resolved_path.exists():
        raise FileNotFoundError(f"fortune records not found: {resolved_path}")
    with resolved_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError(f"fortune records must be a list: {resolved_path}")
    return records


def build_fortune_index(records: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build a ``case_id -> record`` lookup table."""

    return {
        record["case_id"]: record
        for record in records
        if record.get("case_id") and record.get("status") == "success"
    }


def get_chart_record(case_id: str, path: Optional[PathLike] = None) -> Dict[str, Any]:
    """Return a raw fortune record by ``case_id``."""

    index = build_fortune_index(load_fortune_records(path))
    try:
        return index[case_id]
    except KeyError as error:
        raise KeyError(f"case_id not found in fortune records: {case_id}") from error


def extract_chart_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the nested chart payload from one fortune API result."""

    chart = (
        record.get("api_response", {})
        .get("data", {})
        .get("data", {})
    )
    if not isinstance(chart, dict) or not chart:
        raise ValueError(f"record has no chart payload: {record.get('case_id')}")
    return chart


def extract_bazi_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a normalized Bazi summary from a chart record."""

    chart = extract_chart_payload(record)
    chinese_date = chart.get("chineseDate")
    if not chinese_date:
        raise ValueError(f"chart has no chineseDate: {record.get('case_id')}")
    summary = parse_bazi_pillars(chinese_date)
    summary.update({
        "solar_date": chart.get("solarDate"),
        "lunar_date": chart.get("lunarDate"),
        "lunar": (
            parse_chinese_lunar_date(chart["lunarDate"]).as_dict()
            if chart.get("lunarDate")
            else None
        ),
        "time": chart.get("time"),
        "zodiac": chart.get("zodiac"),
        "five_elements_class": chart.get("fiveElementsClass"),
    })
    return summary


def extract_ziwei_palaces(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract compact Ziwei palace summaries from a chart record."""

    chart = extract_chart_payload(record)
    palaces = []
    for palace in chart.get("palaces") or []:
        stars = []
        for group_name in ("majorStars", "minorStars", "adjectiveStars"):
            stars.extend(
                star.get("name")
                for star in palace.get(group_name) or []
                if star.get("name")
            )
        palaces.append({
            "name": palace.get("name"),
            "heavenly_stem": palace.get("heavenlyStem"),
            "earthly_branch": palace.get("earthlyBranch"),
            "is_body_palace": palace.get("isBodyPalace"),
            "is_original_palace": palace.get("isOriginalPalace"),
            "stars": stars,
            "decadal": palace.get("decadal"),
        })
    return palaces


def get_chart_summary(case_id: str, path: Optional[PathLike] = None) -> Dict[str, Any]:
    """Return a developer-friendly chart summary for one benchmark case."""

    record = get_chart_record(case_id, path)
    chart = extract_chart_payload(record)
    return {
        "case_id": case_id,
        "birth_info": record.get("birth_info"),
        "gender": chart.get("gender"),
        "bazi": extract_bazi_summary(record),
        "ziwei": {
            "five_elements_class": chart.get("fiveElementsClass"),
            "zodiac": chart.get("zodiac"),
            "soul": chart.get("soul"),
            "body": chart.get("body"),
            "palaces": extract_ziwei_palaces(record),
        },
    }


__all__ = [
    "build_fortune_index",
    "extract_bazi_summary",
    "extract_chart_payload",
    "extract_ziwei_palaces",
    "get_chart_record",
    "get_chart_summary",
    "load_fortune_records",
]
