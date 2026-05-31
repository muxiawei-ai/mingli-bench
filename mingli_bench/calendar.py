"""Calendar and Ganzhi helpers used by MingLi-Bench.

This module intentionally focuses on small, testable primitives. It does not
attempt to replace a full Chinese calendar engine yet; lunar conversion and
solar-term calculation are listed as roadmap items.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Optional


HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_TO_ELEMENT = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

BRANCH_TO_ELEMENT = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


def sexagenary_name(index: int) -> str:
    """Return the sexagenary cycle name at zero-based index.

    Examples:
        ``sexagenary_name(0)`` -> ``"甲子"``
        ``sexagenary_name(59)`` -> ``"癸亥"``
    """

    if not isinstance(index, int):
        raise TypeError("index must be an integer")
    normalized = index % 60
    return HEAVENLY_STEMS[normalized % 10] + EARTHLY_BRANCHES[normalized % 12]


def sexagenary_index(pillar: str) -> int:
    """Return the zero-based sexagenary cycle index for a pillar."""

    if len(pillar) != 2:
        raise ValueError(f"pillar must contain exactly two Chinese characters: {pillar!r}")
    for index in range(60):
        if sexagenary_name(index) == pillar:
            return index
    raise ValueError(f"invalid sexagenary pillar: {pillar!r}")


def hour_branch(hour: int, minute: int = 0) -> str:
    """Return the earthly branch for a 24-hour clock time.

    Traditional double-hour mapping:
    子 23:00-00:59, 丑 01:00-02:59, ..., 亥 21:00-22:59.
    """

    if not 0 <= hour <= 23:
        raise ValueError("hour must be in 0..23")
    if not 0 <= minute <= 59:
        raise ValueError("minute must be in 0..59")
    return EARTHLY_BRANCHES[((hour + 1) // 2) % 12]


def split_pillars(chinese_date: str) -> List[str]:
    """Split a four-pillar Chinese date string into pillar tokens."""

    pillars = [part.strip() for part in chinese_date.split() if part.strip()]
    if len(pillars) != 4:
        raise ValueError(f"expected four pillars, got {len(pillars)}: {chinese_date!r}")
    for pillar in pillars:
        sexagenary_index(pillar)
    return pillars


def count_five_elements(pillars: Iterable[str]) -> Dict[str, int]:
    """Count five-element occurrences across stems and branches."""

    counter: Counter[str] = Counter()
    for pillar in pillars:
        for char in pillar:
            if char in STEM_TO_ELEMENT:
                counter[STEM_TO_ELEMENT[char]] += 1
            elif char in BRANCH_TO_ELEMENT:
                counter[BRANCH_TO_ELEMENT[char]] += 1
            else:
                raise ValueError(f"unknown ganzhi character: {char!r}")
    return dict(counter)


def parse_bazi_pillars(chinese_date: str) -> Dict[str, object]:
    """Parse a four-pillar string into a compact Bazi summary."""

    pillars = split_pillars(chinese_date)
    day_master: Optional[str] = pillars[2][0] if pillars[2] else None
    return {
        "chinese_date": chinese_date,
        "year_pillar": pillars[0],
        "month_pillar": pillars[1],
        "day_pillar": pillars[2],
        "hour_pillar": pillars[3],
        "day_master": day_master,
        "day_master_element": STEM_TO_ELEMENT.get(day_master),
        "five_elements_summary": count_five_elements(pillars),
    }


__all__ = [
    "BRANCH_TO_ELEMENT",
    "EARTHLY_BRANCHES",
    "HEAVENLY_STEMS",
    "STEM_TO_ELEMENT",
    "count_five_elements",
    "hour_branch",
    "parse_bazi_pillars",
    "sexagenary_index",
    "sexagenary_name",
    "split_pillars",
]
