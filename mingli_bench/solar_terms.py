"""Approximate 24 solar-term calculation utilities.

The implementation uses the standard low-precision solar apparent longitude
formula from astronomical almanac practice and searches for the moment when the
Sun reaches each 15-degree ecliptic longitude. It is designed for deterministic
calendar tooling and tests, not high-precision ephemeris work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import floor, radians, sin
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_TZ_OFFSET_HOURS = 8.0


@dataclass(frozen=True)
class SolarTerm:
    """A solar term and its target apparent solar longitude."""

    name: str
    longitude: float
    approx_month: int
    approx_day: int


SOLAR_TERMS: Tuple[SolarTerm, ...] = (
    SolarTerm("小寒", 285.0, 1, 5),
    SolarTerm("大寒", 300.0, 1, 20),
    SolarTerm("立春", 315.0, 2, 4),
    SolarTerm("雨水", 330.0, 2, 19),
    SolarTerm("惊蛰", 345.0, 3, 6),
    SolarTerm("春分", 0.0, 3, 21),
    SolarTerm("清明", 15.0, 4, 5),
    SolarTerm("谷雨", 30.0, 4, 20),
    SolarTerm("立夏", 45.0, 5, 6),
    SolarTerm("小满", 60.0, 5, 21),
    SolarTerm("芒种", 75.0, 6, 6),
    SolarTerm("夏至", 90.0, 6, 21),
    SolarTerm("小暑", 105.0, 7, 7),
    SolarTerm("大暑", 120.0, 7, 23),
    SolarTerm("立秋", 135.0, 8, 8),
    SolarTerm("处暑", 150.0, 8, 23),
    SolarTerm("白露", 165.0, 9, 8),
    SolarTerm("秋分", 180.0, 9, 23),
    SolarTerm("寒露", 195.0, 10, 8),
    SolarTerm("霜降", 210.0, 10, 23),
    SolarTerm("立冬", 225.0, 11, 7),
    SolarTerm("小雪", 240.0, 11, 22),
    SolarTerm("大雪", 255.0, 12, 7),
    SolarTerm("冬至", 270.0, 12, 22),
)

SOLAR_TERM_BY_NAME = {term.name: term for term in SOLAR_TERMS}

JIE_MONTH_STARTS: Tuple[Tuple[str, str], ...] = (
    ("小寒", "丑"),
    ("立春", "寅"),
    ("惊蛰", "卯"),
    ("清明", "辰"),
    ("立夏", "巳"),
    ("芒种", "午"),
    ("小暑", "未"),
    ("立秋", "申"),
    ("白露", "酉"),
    ("寒露", "戌"),
    ("立冬", "亥"),
    ("大雪", "子"),
)


def julian_day(utc_dt: datetime) -> float:
    """Return the Julian Day for a naive UTC ``datetime``."""

    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day + (
        utc_dt.hour
        + (utc_dt.minute + (utc_dt.second + utc_dt.microsecond / 1_000_000) / 60) / 60
    ) / 24

    if month <= 2:
        year -= 1
        month += 12

    a = floor(year / 100)
    b = 2 - a + floor(a / 4)
    return (
        floor(365.25 * (year + 4716))
        + floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )


def solar_apparent_longitude(utc_dt: datetime) -> float:
    """Return the Sun's apparent ecliptic longitude in degrees."""

    t = (julian_day(utc_dt) - 2451545.0) / 36525
    mean_longitude = 280.46646 + t * (36000.76983 + t * 0.0003032)
    mean_anomaly = radians(357.52911 + t * (35999.05029 - 0.0001537 * t))
    equation_of_center = (
        sin(mean_anomaly) * (1.914602 - t * (0.004817 + 0.000014 * t))
        + sin(2 * mean_anomaly) * (0.019993 - 0.000101 * t)
        + sin(3 * mean_anomaly) * 0.000289
    )
    true_longitude = mean_longitude + equation_of_center
    omega = radians(125.04 - 1934.136 * t)
    apparent_longitude = true_longitude - 0.00569 - 0.00478 * sin(omega)
    return apparent_longitude % 360


def _signed_angle_delta(longitude: float, target: float) -> float:
    return ((longitude - target + 540) % 360) - 180


def _find_longitude_crossing(
    target_longitude: float,
    start_utc: datetime,
    end_utc: datetime,
) -> datetime:
    start_delta = _signed_angle_delta(solar_apparent_longitude(start_utc), target_longitude)
    end_delta = _signed_angle_delta(solar_apparent_longitude(end_utc), target_longitude)
    if start_delta > 0 or end_delta < 0:
        raise ValueError("search window does not bracket the requested solar longitude")

    lo = start_utc
    hi = end_utc
    for _ in range(60):
        mid = lo + (hi - lo) / 2
        delta = _signed_angle_delta(solar_apparent_longitude(mid), target_longitude)
        if delta < 0:
            lo = mid
        else:
            hi = mid
    return hi


def solar_term_datetime(
    year: int,
    term_name: str,
    *,
    tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
) -> datetime:
    """Return the local datetime when a solar term occurs.

    The returned ``datetime`` is naive local time using ``tz_offset_hours``.
    ``tz_offset_hours=8`` matches China Standard Time.
    """

    if term_name not in SOLAR_TERM_BY_NAME:
        raise ValueError(f"unknown solar term: {term_name!r}")

    term = SOLAR_TERM_BY_NAME[term_name]
    tz_delta = timedelta(hours=tz_offset_hours)
    approx_local = datetime(year, term.approx_month, term.approx_day, 12)
    start_utc = approx_local - timedelta(days=4) - tz_delta
    end_utc = approx_local + timedelta(days=4) - tz_delta
    crossing_utc = _find_longitude_crossing(term.longitude, start_utc, end_utc)
    return crossing_utc + tz_delta


def solar_terms_for_year(
    year: int,
    *,
    names: Optional[Iterable[str]] = None,
    tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
) -> Dict[str, datetime]:
    """Return solar-term local datetimes for a Gregorian year."""

    requested_names = (
        list(names) if names is not None else [term.name for term in SOLAR_TERMS]
    )
    return {
        name: solar_term_datetime(year, name, tz_offset_hours=tz_offset_hours)
        for name in requested_names
    }


def jie_boundaries_for_year(
    year: int,
    *,
    tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
) -> List[Tuple[datetime, str, str]]:
    """Return the 12 major solar-term boundaries used for Bazi months."""

    return [
        (
            solar_term_datetime(year, term_name, tz_offset_hours=tz_offset_hours),
            term_name,
            month_branch,
        )
        for term_name, month_branch in JIE_MONTH_STARTS
    ]


def solar_month_branch_for_datetime(
    local_dt: datetime,
    *,
    tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
) -> str:
    """Return the Bazi month branch for a local datetime."""

    boundaries = jie_boundaries_for_year(local_dt.year, tz_offset_hours=tz_offset_hours)
    current_branch = "子"
    for boundary, _term_name, month_branch in boundaries:
        if local_dt >= boundary:
            current_branch = month_branch
        else:
            break
    return current_branch


__all__ = [
    "DEFAULT_TZ_OFFSET_HOURS",
    "JIE_MONTH_STARTS",
    "SOLAR_TERMS",
    "SolarTerm",
    "jie_boundaries_for_year",
    "julian_day",
    "solar_apparent_longitude",
    "solar_month_branch_for_datetime",
    "solar_term_datetime",
    "solar_terms_for_year",
]
