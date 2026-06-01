"""Chinese lunar-date parsing and fixture-backed lookup utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Union


PathLike = Union[str, Path]

_YEAR_DIGITS = {
    "〇": "0",
    "零": "0",
    "Ｏ": "0",
    "○": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
}

_MONTH_NAMES = {
    "正": 1,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "冬": 11,
    "十一": 11,
    "腊": 12,
    "臘": 12,
    "十二": 12,
}

_DAY_NAMES = {
    "初一": 1,
    "初二": 2,
    "初三": 3,
    "初四": 4,
    "初五": 5,
    "初六": 6,
    "初七": 7,
    "初八": 8,
    "初九": 9,
    "初十": 10,
    "十一": 11,
    "十二": 12,
    "十三": 13,
    "十四": 14,
    "十五": 15,
    "十六": 16,
    "十七": 17,
    "十八": 18,
    "十九": 19,
    "二十": 20,
    "廿一": 21,
    "廿二": 22,
    "廿三": 23,
    "廿四": 24,
    "廿五": 25,
    "廿六": 26,
    "廿七": 27,
    "廿八": 28,
    "廿九": 29,
    "三十": 30,
}


@dataclass(frozen=True)
class LunarDate:
    """Structured Chinese lunar calendar date."""

    year: int
    month: int
    day: int
    is_leap_month: bool = False

    def key(self) -> Tuple[int, int, int, bool]:
        return (self.year, self.month, self.day, self.is_leap_month)

    def as_dict(self) -> Dict[str, object]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "is_leap_month": self.is_leap_month,
        }


def _parse_lunar_year(year_text: str) -> int:
    digits = []
    for char in year_text:
        if char in _YEAR_DIGITS:
            digits.append(_YEAR_DIGITS[char])
        elif char.isdigit():
            digits.append(char)
        else:
            raise ValueError(f"unsupported lunar year character: {char!r}")
    if not digits:
        raise ValueError("lunar year is empty")
    return int("".join(digits))


def _parse_lunar_month(month_text: str) -> Tuple[int, bool]:
    is_leap_month = month_text.startswith(("闰", "閏"))
    normalized = month_text[1:] if is_leap_month else month_text
    normalized = normalized.removesuffix("月")
    try:
        return _MONTH_NAMES[normalized], is_leap_month
    except KeyError as error:
        raise ValueError(f"unsupported lunar month: {month_text!r}") from error


def _parse_lunar_day(day_text: str) -> int:
    try:
        return _DAY_NAMES[day_text]
    except KeyError as error:
        raise ValueError(f"unsupported lunar day: {day_text!r}") from error


def parse_chinese_lunar_date(value: str) -> LunarDate:
    """Parse a Chinese lunar date like ``一九八四年闰十月十七``."""

    text = value.strip()
    if "年" not in text or "月" not in text:
        raise ValueError(f"lunar date must contain 年 and 月: {value!r}")
    year_text, rest = text.split("年", 1)
    month_text, day_text = rest.split("月", 1)
    month, is_leap_month = _parse_lunar_month(month_text + "月")
    day = _parse_lunar_day(day_text)
    return LunarDate(
        year=_parse_lunar_year(year_text),
        month=month,
        day=day,
        is_leap_month=is_leap_month,
    )


def normalize_lunar_date(
    lunar_date: Union[str, LunarDate, Dict[str, Any], int],
    month: Optional[int] = None,
    day: Optional[int] = None,
    *,
    is_leap_month: bool = False,
) -> LunarDate:
    """Normalize supported lunar-date inputs into ``LunarDate``."""

    if isinstance(lunar_date, LunarDate):
        return lunar_date
    if isinstance(lunar_date, str) and month is None and day is None:
        return parse_chinese_lunar_date(lunar_date)
    if isinstance(lunar_date, dict):
        return LunarDate(
            year=int(lunar_date["year"]),
            month=int(lunar_date["month"]),
            day=int(lunar_date["day"]),
            is_leap_month=bool(lunar_date.get("is_leap_month", False)),
        )
    if month is None or day is None:
        raise ValueError("month and day are required when passing a numeric lunar year")
    return LunarDate(
        year=int(lunar_date),
        month=int(month),
        day=int(day),
        is_leap_month=is_leap_month,
    )


def _solar_date_key(value: Union[str, date]) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(value).isoformat()


def build_lunar_solar_index(
    records: Iterable[Dict[str, Any]],
) -> Dict[str, Dict[Any, Dict[str, Any]]]:
    """Build fixture-backed lookup indexes for solar and lunar dates."""

    by_solar: Dict[str, Dict[str, Any]] = {}
    by_lunar: Dict[Any, Dict[str, Any]] = {}
    for record in records:
        if record.get("status") != "success":
            continue
        chart = (
            record.get("api_response", {})
            .get("data", {})
            .get("data", {})
        )
        solar_date = chart.get("solarDate")
        lunar_text = chart.get("lunarDate")
        if not solar_date or not lunar_text:
            continue
        lunar = parse_chinese_lunar_date(lunar_text)
        item = {
            "case_id": record.get("case_id"),
            "solar_date": solar_date,
            "lunar_date": lunar_text,
            "lunar": lunar.as_dict(),
            "source": "fortune_api_results_fixture",
        }
        by_solar[solar_date] = item
        by_lunar[lunar.key()] = item
    return {"by_solar": by_solar, "by_lunar": by_lunar}


def load_lunar_solar_index(
    path: Optional[PathLike] = None,
) -> Dict[str, Dict[Any, Dict[str, Any]]]:
    """Load fixture-backed lunar/solar lookup indexes."""

    from .charts import load_fortune_records

    return build_lunar_solar_index(load_fortune_records(path))


def lunar_from_solar_date(
    solar_date: Union[str, date],
    *,
    path: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """Return fixture-backed lunar data for a Gregorian date."""

    index = load_lunar_solar_index(path)["by_solar"]
    key = _solar_date_key(solar_date)
    try:
        return index[key]
    except KeyError as error:
        raise KeyError(f"solar date not found in lunar fixture index: {key}") from error


def solar_from_lunar_date(
    lunar_date: Union[str, LunarDate, Dict[str, Any], int],
    month: Optional[int] = None,
    day: Optional[int] = None,
    *,
    is_leap_month: bool = False,
    path: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """Return fixture-backed Gregorian data for a lunar date."""

    normalized = normalize_lunar_date(
        lunar_date,
        month,
        day,
        is_leap_month=is_leap_month,
    )
    index = load_lunar_solar_index(path)["by_lunar"]
    try:
        return index[normalized.key()]
    except KeyError as error:
        raise KeyError(
            f"lunar date not found in fixture index: {normalized.as_dict()}"
        ) from error


__all__ = [
    "LunarDate",
    "build_lunar_solar_index",
    "load_lunar_solar_index",
    "lunar_from_solar_date",
    "normalize_lunar_date",
    "parse_chinese_lunar_date",
    "solar_from_lunar_date",
]
