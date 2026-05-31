"""Small Bazi calculation primitives.

The functions here intentionally implement only the parts that can be kept
small and well tested today: year pillar, day pillar, and hour pillar.
Month pillar derivation depends on solar-term boundaries and is left explicit
until a proper solar-term engine is added.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Optional, Union

from .calendar import (
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    STEM_TO_ELEMENT,
    count_five_elements,
    hour_branch,
    sexagenary_index,
    sexagenary_name,
)


DateLike = Union[str, date]

REFERENCE_DAY = date(1974, 4, 28)
REFERENCE_DAY_PILLAR = "己亥"
YEAR_PILLAR_REFERENCE_YEAR = 1984
YEAR_PILLAR_REFERENCE = "甲子"

HOUR_STEM_START_BY_DAY_STEM = {
    "甲": "甲",
    "己": "甲",
    "乙": "丙",
    "庚": "丙",
    "丙": "戊",
    "辛": "戊",
    "丁": "庚",
    "壬": "庚",
    "戊": "壬",
    "癸": "壬",
}


def parse_solar_date(value: DateLike) -> date:
    """Parse a Gregorian date object or ``YYYY-MM-DD`` string."""

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError("solar date must be a date, datetime, or YYYY-MM-DD string")


def year_pillar_for_date(
    solar_date: DateLike,
    *,
    li_chun_month: int = 2,
    li_chun_day: int = 4,
) -> str:
    """Return the sexagenary year pillar for a Gregorian date.

    Bazi year boundaries are based on Li Chun (立春), not Lunar New Year.
    This helper uses a configurable Feb 4 default boundary as a transparent
    approximation until the project adds a full solar-term engine.
    """

    parsed_date = parse_solar_date(solar_date)
    pillar_year = parsed_date.year
    if (parsed_date.month, parsed_date.day) < (li_chun_month, li_chun_day):
        pillar_year -= 1

    reference_index = sexagenary_index(YEAR_PILLAR_REFERENCE)
    return sexagenary_name(reference_index + pillar_year - YEAR_PILLAR_REFERENCE_YEAR)


def day_pillar_for_date(solar_date: DateLike) -> str:
    """Return the sexagenary day pillar for a Gregorian date.

    The continuous day cycle is calibrated against the repository fixture
    ``case_1`` where 1974-04-28 is ``己亥``. The same calibration is then
    validated against all available fixture dates in the test suite.
    """

    parsed_date = parse_solar_date(solar_date)
    reference_index = sexagenary_index(REFERENCE_DAY_PILLAR)
    day_delta = (parsed_date - REFERENCE_DAY).days
    return sexagenary_name(reference_index + day_delta)


def bazi_day_date_for_time(
    solar_date: DateLike,
    hour: Optional[int] = None,
    *,
    zi_hour_day_rollover: bool = True,
) -> date:
    """Return the date used for Bazi day-pillar calculation.

    Many Bazi systems treat late Zi hour (23:00-23:59) as the next day for
    day-pillar purposes. The default follows that convention because it matches
    the bundled chart fixtures.
    """

    parsed_date = parse_solar_date(solar_date)
    if zi_hour_day_rollover and hour == 23:
        return parsed_date + timedelta(days=1)
    return parsed_date


def day_pillar_for_datetime(
    solar_date: DateLike,
    hour: Optional[int] = None,
    *,
    zi_hour_day_rollover: bool = True,
) -> str:
    """Return the day pillar, optionally applying late-Zi-hour rollover."""

    return day_pillar_for_date(
        bazi_day_date_for_time(
            solar_date,
            hour,
            zi_hour_day_rollover=zi_hour_day_rollover,
        )
    )


def hour_pillar_for_datetime(
    solar_date: DateLike,
    hour: int,
    minute: int = 0,
    *,
    zi_hour_day_rollover: bool = True,
) -> str:
    """Return the Bazi hour pillar for a Gregorian date and 24-hour time."""

    day_stem = day_pillar_for_datetime(
        solar_date,
        hour,
        zi_hour_day_rollover=zi_hour_day_rollover,
    )[0]
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    branch = hour_branch(hour, minute)
    branch_index = EARTHLY_BRANCHES.index(branch)
    start_stem_index = HEAVENLY_STEMS.index(start_stem)
    return HEAVENLY_STEMS[(start_stem_index + branch_index) % 10] + branch


def bazi_from_gregorian(
    solar_date: DateLike,
    *,
    hour: Optional[int] = None,
    minute: int = 0,
    zi_hour_day_rollover: bool = True,
) -> Dict[str, object]:
    """Return a partial Bazi chart from Gregorian date/time.

    ``month_pillar`` is intentionally ``None`` until solar-term based month
    derivation is implemented.
    """

    parsed_date = parse_solar_date(solar_date)
    year_pillar = year_pillar_for_date(parsed_date)
    bazi_day_date = bazi_day_date_for_time(
        parsed_date,
        hour,
        zi_hour_day_rollover=zi_hour_day_rollover,
    )
    day_pillar = day_pillar_for_date(bazi_day_date)
    hour_pillar = (
        hour_pillar_for_datetime(
            parsed_date,
            hour,
            minute,
            zi_hour_day_rollover=zi_hour_day_rollover,
        )
        if hour is not None
        else None
    )
    pillars = [year_pillar, day_pillar]
    if hour_pillar:
        pillars.append(hour_pillar)

    return {
        "solar_date": parsed_date.isoformat(),
        "bazi_day_date": bazi_day_date.isoformat(),
        "year_pillar": year_pillar,
        "month_pillar": None,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "day_master": day_pillar[0],
        "day_master_element": STEM_TO_ELEMENT.get(day_pillar[0]),
        "hour_branch": hour_branch(hour, minute) if hour is not None else None,
        "five_elements_summary": count_five_elements(pillars),
        "warnings": [
            "month_pillar_requires_solar_terms",
            "year_pillar_uses_approximate_li_chun_boundary",
        ],
    }


__all__ = [
    "REFERENCE_DAY",
    "REFERENCE_DAY_PILLAR",
    "bazi_from_gregorian",
    "bazi_day_date_for_time",
    "day_pillar_for_datetime",
    "day_pillar_for_date",
    "hour_pillar_for_datetime",
    "parse_solar_date",
    "year_pillar_for_date",
]
