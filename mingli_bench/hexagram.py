"""Deterministic hexagram helpers for MingLi report integrations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .bazi import year_pillar_for_datetime
from .calendar import hour_branch as _hour_branch
from .chart_api import BaziChart
from .hexagram_data import get_hexagram_text, get_line_text
from .solar_terms import DEFAULT_TZ_OFFSET_HOURS


Line = str
TrigramLines = Tuple[Line, Line, Line]


BRANCH_NUMBERS = {
    "子": 1,
    "丑": 2,
    "寅": 3,
    "卯": 4,
    "辰": 5,
    "巳": 6,
    "午": 7,
    "未": 8,
    "申": 9,
    "酉": 10,
    "戌": 11,
    "亥": 12,
}


@dataclass(frozen=True)
class Trigram:
    """One bagua trigram, represented by lines from bottom to top."""

    number: int
    name: str
    symbol: str
    element: str
    lines: TrigramLines


TRIGRAMS_BY_NUMBER: Dict[int, Trigram] = {
    1: Trigram(1, "乾", "☰", "金", ("yang", "yang", "yang")),
    2: Trigram(2, "兑", "☱", "金", ("yang", "yang", "yin")),
    3: Trigram(3, "离", "☲", "火", ("yang", "yin", "yang")),
    4: Trigram(4, "震", "☳", "木", ("yang", "yin", "yin")),
    5: Trigram(5, "巽", "☴", "木", ("yin", "yang", "yang")),
    6: Trigram(6, "坎", "☵", "水", ("yin", "yang", "yin")),
    7: Trigram(7, "艮", "☶", "土", ("yin", "yin", "yang")),
    8: Trigram(8, "坤", "☷", "土", ("yin", "yin", "yin")),
}

TRIGRAMS_BY_NAME = {trigram.name: trigram for trigram in TRIGRAMS_BY_NUMBER.values()}
TRIGRAMS_BY_LINES = {trigram.lines: trigram for trigram in TRIGRAMS_BY_NUMBER.values()}


HEXAGRAM_NAMES = {
    1: "乾卦",
    2: "坤卦",
    3: "屯卦",
    4: "蒙卦",
    5: "需卦",
    6: "讼卦",
    7: "师卦",
    8: "比卦",
    9: "小畜卦",
    10: "履卦",
    11: "泰卦",
    12: "否卦",
    13: "同人卦",
    14: "大有卦",
    15: "谦卦",
    16: "豫卦",
    17: "随卦",
    18: "蛊卦",
    19: "临卦",
    20: "观卦",
    21: "噬嗑卦",
    22: "贲卦",
    23: "剥卦",
    24: "复卦",
    25: "无妄卦",
    26: "大畜卦",
    27: "颐卦",
    28: "大过卦",
    29: "坎卦",
    30: "离卦",
    31: "咸卦",
    32: "恒卦",
    33: "遁卦",
    34: "大壮卦",
    35: "晋卦",
    36: "明夷卦",
    37: "家人卦",
    38: "睽卦",
    39: "蹇卦",
    40: "解卦",
    41: "损卦",
    42: "益卦",
    43: "夬卦",
    44: "姤卦",
    45: "萃卦",
    46: "升卦",
    47: "困卦",
    48: "井卦",
    49: "革卦",
    50: "鼎卦",
    51: "震卦",
    52: "艮卦",
    53: "渐卦",
    54: "归妹卦",
    55: "丰卦",
    56: "旅卦",
    57: "巽卦",
    58: "兑卦",
    59: "涣卦",
    60: "节卦",
    61: "中孚卦",
    62: "小过卦",
    63: "既济卦",
    64: "未济卦",
}


KING_WEN_BY_TRIGRAMS: Dict[Tuple[str, str], int] = {
    ("乾", "乾"): 1,
    ("兑", "乾"): 43,
    ("离", "乾"): 14,
    ("震", "乾"): 34,
    ("巽", "乾"): 9,
    ("坎", "乾"): 5,
    ("艮", "乾"): 26,
    ("坤", "乾"): 11,
    ("乾", "兑"): 10,
    ("兑", "兑"): 58,
    ("离", "兑"): 38,
    ("震", "兑"): 54,
    ("巽", "兑"): 61,
    ("坎", "兑"): 60,
    ("艮", "兑"): 41,
    ("坤", "兑"): 19,
    ("乾", "离"): 13,
    ("兑", "离"): 49,
    ("离", "离"): 30,
    ("震", "离"): 55,
    ("巽", "离"): 37,
    ("坎", "离"): 63,
    ("艮", "离"): 22,
    ("坤", "离"): 36,
    ("乾", "震"): 25,
    ("兑", "震"): 17,
    ("离", "震"): 21,
    ("震", "震"): 51,
    ("巽", "震"): 42,
    ("坎", "震"): 3,
    ("艮", "震"): 27,
    ("坤", "震"): 24,
    ("乾", "巽"): 44,
    ("兑", "巽"): 28,
    ("离", "巽"): 50,
    ("震", "巽"): 32,
    ("巽", "巽"): 57,
    ("坎", "巽"): 48,
    ("艮", "巽"): 18,
    ("坤", "巽"): 46,
    ("乾", "坎"): 6,
    ("兑", "坎"): 47,
    ("离", "坎"): 64,
    ("震", "坎"): 40,
    ("巽", "坎"): 59,
    ("坎", "坎"): 29,
    ("艮", "坎"): 4,
    ("坤", "坎"): 7,
    ("乾", "艮"): 33,
    ("兑", "艮"): 31,
    ("离", "艮"): 56,
    ("震", "艮"): 62,
    ("巽", "艮"): 53,
    ("坎", "艮"): 39,
    ("艮", "艮"): 52,
    ("坤", "艮"): 15,
    ("乾", "坤"): 12,
    ("兑", "坤"): 45,
    ("离", "坤"): 35,
    ("震", "坤"): 16,
    ("巽", "坤"): 20,
    ("坎", "坤"): 8,
    ("艮", "坤"): 23,
    ("坤", "坤"): 2,
}


@dataclass(frozen=True)
class HexagramInput:
    """All time-derived numbers needed for one Meihua Yi Shu cast.

    Prefer constructing this via :func:`hexagram_input_from_datetime` rather
    than setting fields directly.  The dataclass is frozen so instances can be
    cached or used as dict keys.

    Attributes:
        year_branch:   Bazi year *branch* character, e.g. ``"午"``.
        month_number:  Lunar month 1-12, or solar month used as proxy.
        day_number:    Lunar day 1-30, or solar day used as proxy.
        hour_branch:   Hour branch derived from cast time, e.g. ``"酉"``.
        number_source: ``"lunar_date"`` when lunar values were supplied,
                       ``"solar_input_proxy"`` otherwise.
        source_type:   Intent label — ``"birth_time"``, ``"question_time"``,
                       or ``"casting_time"``.
        source_label:  Human-readable provenance string for audit logs.
    """

    year_branch: str
    month_number: int
    day_number: int
    hour_branch: str
    number_source: str
    source_type: str
    source_label: str


def hexagram_input_from_datetime(
    dt: datetime,
    *,
    source_type: str = "casting_time",
    lunar_month: Optional[int] = None,
    lunar_day: Optional[int] = None,
    tz_offset_hours: int = DEFAULT_TZ_OFFSET_HOURS,
) -> HexagramInput:
    """Build a :class:`HexagramInput` from any Python datetime.

    Meihua Yi Shu (梅花易数) traditionally uses the Chinese lunar calendar for
    month and day numbers.  When *lunar_month* and *lunar_day* are both provided
    those values are used directly.  Otherwise the solar calendar values are
    substituted as a proxy and the caveat is recorded in the
    :func:`cast_hexagram` output.

    Args:
        dt: The datetime to cast from.
        source_type: Intent label — ``"birth_time"``, ``"question_time"``, or
            ``"casting_time"``.  Does not change the calculation; used for
            provenance in the output.
        lunar_month: Known lunar month (1-12).  Must be provided together with
            *lunar_day* to activate accurate lunar calculation.
        lunar_day: Known lunar day (1-30).  Must be provided together with
            *lunar_month* to activate accurate lunar calculation.
        tz_offset_hours: UTC offset hours used for the Li Chun year-boundary
            when determining the Bazi year branch.

    Returns:
        :class:`HexagramInput` ready to pass to :func:`cast_hexagram`.
    """
    year_pillar = year_pillar_for_datetime(dt, tz_offset_hours=tz_offset_hours)
    year_br = year_pillar[1]  # stem(0) + branch(1); we want the branch
    hour_br = _hour_branch(dt.hour, dt.minute)

    if lunar_month is not None and lunar_day is not None:
        number_source = "lunar_date"
        m, d = lunar_month, lunar_day
        source_label = (
            f"{dt.strftime('%Y-%m-%d %H:%M')}"
            f"（农历{m}月{d}日，{source_type}）"
        )
    else:
        number_source = "solar_input_proxy"
        m, d = dt.month, dt.day
        source_label = (
            f"{dt.strftime('%Y-%m-%d %H:%M')}"
            f"（公历月日代入，{source_type}）"
        )

    return HexagramInput(
        year_branch=year_br,
        month_number=m,
        day_number=d,
        hour_branch=hour_br,
        number_source=number_source,
        source_type=source_type,
        source_label=source_label,
    )


def cast_hexagram(hi: HexagramInput) -> Dict[str, Any]:
    """Cast a Meihua Yi Shu time hexagram from a :class:`HexagramInput`.

    This is a **pure function**: the result depends only on the four
    integer/string fields inside *hi*.  No network calls, no ``BaziChart``
    object, no LLM.

    Formula (standard Meihua time-number method)::

        upper_total   = year_number + month_number + day_number
        lower_total   = upper_total + hour_number
        upper_trigram = upper_total mod 8  (1-based)
        lower_trigram = lower_total mod 8  (1-based)
        moving_line   = lower_total mod 6  (1-based)

    Returns a dict with the same schema as :func:`build_time_hexagram`, plus
    two provenance fields: ``"source_type"`` and ``"source_label"``.
    """
    year_number = BRANCH_NUMBERS[hi.year_branch]
    hour_number = BRANCH_NUMBERS[hi.hour_branch]
    upper_total = year_number + hi.month_number + hi.day_number
    lower_total = upper_total + hour_number
    upper_number = _mod_one_based(upper_total, 8)
    lower_number = _mod_one_based(lower_total, 8)
    moving_line = _mod_one_based(lower_total, 6)

    upper = TRIGRAMS_BY_NUMBER[upper_number]
    lower = TRIGRAMS_BY_NUMBER[lower_number]
    primary = lookup_hexagram(upper.name, lower.name, role="本卦")
    changed_lines = _change_line(primary["lines"], moving_line)
    changed_lower_tri = TRIGRAMS_BY_LINES[tuple(changed_lines[:3])]
    changed_upper_tri = TRIGRAMS_BY_LINES[tuple(changed_lines[3:])]
    changed = lookup_hexagram(changed_upper_tri.name, changed_lower_tri.name, role="变卦")

    moving_line_name = _line_name(moving_line, primary["lines"][moving_line - 1])
    moving_line_data = get_line_text(primary["number"], moving_line)

    caveats: List[str] = [
        "卦象由本地梅花易数时间法规则生成，不代表确定事实。",
        "当前版本已接入 64 卦基础卦辞/爻辞资料；细分断语仍需结合问题语境。",
    ]
    if hi.number_source == "solar_input_proxy":
        caveats.append(
            "当前为公历输入，月日数暂按公历月日代入；"
            "如需准确农历数，请在 hexagram_input_from_datetime() 中"
            "传入 lunar_month 和 lunar_day 参数。"
        )

    return {
        "method": "梅花易数时间法",
        "source_type": hi.source_type,
        "source_label": hi.source_label,
        "basis": [
            (
                f"年支数({year_number}，{hi.year_branch}年)"
                f"+月数({hi.month_number})"
                f"+日数({hi.day_number})={upper_total}"
                f" -> 余{upper_number} -> 上卦：{upper.name}{upper.symbol}"
            ),
            (
                f"加时支数({hour_number}，{hi.hour_branch}时)={lower_total}"
                f" -> 余{lower_number} -> 下卦：{lower.name}{lower.symbol}"
                f" · 动爻：第{moving_line}爻"
            ),
        ],
        "number_source": {
            "year_branch": hi.year_branch,
            "year_number": year_number,
            "month_number": hi.month_number,
            "day_number": hi.day_number,
            "hour_branch": hi.hour_branch,
            "hour_number": hour_number,
            "calendar_source": hi.number_source,
            "upper_total": upper_total,
            "lower_total": lower_total,
        },
        "primary": primary,
        "changed": changed,
        "moving_line": moving_line,
        "moving_line_name": moving_line_name,
        "moving_line_text": (
            moving_line_data["text"]
            if moving_line_data
            else f"{moving_line_name}为本次动爻；经典爻辞库待补充。"
        ),
        "moving_line_note": (
            moving_line_data.get("note")
            if moving_line_data
            else "本地规则定位此爻为动爻，解读时应重点关注。"
        ),
        "moving_line_source": (
            moving_line_data.get("source") if moving_line_data else "pending"
        ),
        "interpretation": (
            f"本地时间法生成本卦《{primary['name'].removesuffix('卦')}》"
            f"，动{moving_line_name}，变卦为《{changed['name'].removesuffix('卦')}》。"
            "该结果用于提供可审计的卦象结构，后续解读应基于此结构展开。"
        ),
        "caveats": caveats,
        "line_details": _line_details(primary["number"], primary["lines"], moving_line),
    }


def build_time_hexagram(chart: BaziChart) -> Optional[Dict[str, Any]]:
    """Build a Meihua-style time hexagram from a deterministic Bazi chart.

    The rule used here is the common time-number scaffold:
    upper = year branch number + month number + day number (mod 8)
    lower = upper total + hour branch number (mod 8)
    moving line = lower total (mod 6)

    Month/day currently come from the input calendar when available. For solar
    input this is a transparent approximation until a full lunar calendar
    conversion engine is available for all dates.
    """

    if chart.hour_branch is None:
        return None

    date_numbers = _date_numbers(chart)
    year_branch = chart.pillars.year[1]
    year_number = BRANCH_NUMBERS[year_branch]
    hour_number = BRANCH_NUMBERS[chart.hour_branch]
    upper_total = year_number + date_numbers["month"] + date_numbers["day"]
    lower_total = upper_total + hour_number
    upper_number = _mod_one_based(upper_total, 8)
    lower_number = _mod_one_based(lower_total, 8)
    moving_line = _mod_one_based(lower_total, 6)

    upper = TRIGRAMS_BY_NUMBER[upper_number]
    lower = TRIGRAMS_BY_NUMBER[lower_number]
    primary = lookup_hexagram(upper.name, lower.name, role="本卦")
    changed_lines = _change_line(primary["lines"], moving_line)
    changed_lower = TRIGRAMS_BY_LINES[tuple(changed_lines[:3])]
    changed_upper = TRIGRAMS_BY_LINES[tuple(changed_lines[3:])]
    changed = lookup_hexagram(changed_upper.name, changed_lower.name, role="变卦")

    moving_line_name = _line_name(moving_line, primary["lines"][moving_line - 1])
    moving_line_data = get_line_text(primary["number"], moving_line)
    return {
        "method": "梅花易数时间法",
        "basis": [
            (
                f"年支数({year_number}，{year_branch}年)"
                f"+月数({date_numbers['month']})"
                f"+日数({date_numbers['day']})={upper_total}"
                f" -> 余{upper_number} -> 上卦：{upper.name}{upper.symbol}"
            ),
            (
                f"加时支数({hour_number}，{chart.hour_branch}时)={lower_total}"
                f" -> 余{lower_number} -> 下卦：{lower.name}{lower.symbol}"
                f" · 动爻：第{moving_line}爻"
            ),
        ],
        "number_source": {
            "year_branch": year_branch,
            "year_number": year_number,
            "month_number": date_numbers["month"],
            "day_number": date_numbers["day"],
            "hour_branch": chart.hour_branch,
            "hour_number": hour_number,
            "calendar_source": date_numbers["source"],
            "upper_total": upper_total,
            "lower_total": lower_total,
        },
        "primary": primary,
        "changed": changed,
        "moving_line": moving_line,
        "moving_line_name": moving_line_name,
        "moving_line_text": (
            moving_line_data["text"]
            if moving_line_data
            else f"{moving_line_name}为本次动爻；经典爻辞库待补充。"
        ),
        "moving_line_note": (
            moving_line_data.get("note")
            if moving_line_data
            else "本地规则定位此爻为动爻，解读时应重点关注。"
        ),
        "moving_line_source": (
            moving_line_data.get("source") if moving_line_data else "pending"
        ),
        "interpretation": (
            f"本地时间法生成本卦《{primary['name'].removesuffix('卦')}》"
            f"，动{moving_line_name}，变卦为《{changed['name'].removesuffix('卦')}》。"
            "该结果用于提供可审计的卦象结构，后续解读应基于此结构展开。"
        ),
        "caveats": _hexagram_caveats(chart, date_numbers["source"]),
        "line_details": _line_details(primary["number"], primary["lines"], moving_line),
    }


def lookup_hexagram(upper: str, lower: str, *, role: str = "卦象") -> Dict[str, Any]:
    """Return King Wen metadata for one upper/lower trigram pair."""

    upper_trigram = TRIGRAMS_BY_NAME[upper]
    lower_trigram = TRIGRAMS_BY_NAME[lower]
    number = KING_WEN_BY_TRIGRAMS[(upper, lower)]
    text_data = get_hexagram_text(number)
    return {
        "role": role,
        "name": HEXAGRAM_NAMES[number],
        "symbol": chr(0x4DC0 + number - 1),
        "number": number,
        "upper": upper,
        "lower": lower,
        "upper_symbol": upper_trigram.symbol,
        "lower_symbol": lower_trigram.symbol,
        "upper_element": upper_trigram.element,
        "lower_element": lower_trigram.element,
        "lines": list(lower_trigram.lines + upper_trigram.lines),
        "description": f"{upper}上{lower}下",
        "theme": text_data.get("theme") if text_data else None,
        "judgment": text_data.get("judgment") if text_data else None,
        "image": text_data.get("image") if text_data else None,
        "text_source": text_data.get("source") if text_data else "pending",
        "text_coverage": text_data.get("coverage") if text_data else "pending",
    }


def _date_numbers(chart: BaziChart) -> Dict[str, Any]:
    if chart.lunar:
        return {
            "month": int(chart.lunar["month"]),
            "day": int(chart.lunar["day"]),
            "source": "lunar_date",
        }
    return {
        "month": int(chart.input.month),
        "day": int(chart.input.day),
        "source": "solar_input_proxy",
    }


def _mod_one_based(total: int, base: int) -> int:
    remainder = total % base
    return remainder if remainder else base


def _change_line(lines: List[Line], moving_line: int) -> List[Line]:
    changed = list(lines)
    index = moving_line - 1
    changed[index] = "yin" if changed[index] == "yang" else "yang"
    return changed


def _line_name(index: int, line: Line) -> str:
    yang_names = ["", "初九", "九二", "九三", "九四", "九五", "上九"]
    yin_names = ["", "初六", "六二", "六三", "六四", "六五", "上六"]
    return (yang_names if line == "yang" else yin_names)[index]


def _line_details(
    hexagram_number: int,
    lines: List[Line],
    moving_line: int,
) -> List[Dict[str, Any]]:
    details = []
    for index, line in enumerate(lines, start=1):
        moving = index == moving_line
        text_data = get_line_text(hexagram_number, index)
        details.append(
            {
                "index": index,
                "name": _line_name(index, line) + (" · 动爻" if moving else ""),
                "line_type": line,
                "text": text_data["text"] if text_data else "经典爻辞待补充。",
                "note": (
                    text_data.get("note")
                    if text_data
                    else (
                        "本地规则定位此爻为动爻，解读时应重点关注。"
                        if moving
                        else "本地规则已确定该爻阴阳，爻辞文本库待补充。"
                    )
                ),
                "source": text_data.get("source") if text_data else "pending",
            }
        )
    return details


def _hexagram_caveats(chart: BaziChart, date_source: str) -> List[str]:
    caveats = [
        "卦象由本地梅花易数时间法规则生成，不代表确定事实。",
        "当前版本已接入 64 卦基础卦辞/爻辞资料；细分断语仍需结合问题语境。",
    ]
    if date_source == "solar_input_proxy":
        caveats.append("当前为公历输入，月日数暂按公历月日代入；未来接入完整农历引擎后可改用农历月日。")
    if chart.timezone.get("warnings"):
        caveats.append("出生地或时区存在标准化假设，时辰数可能受地点校正影响。")
    return caveats


__all__ = [
    "BRANCH_NUMBERS",
    "HEXAGRAM_NAMES",
    "HexagramInput",
    "KING_WEN_BY_TRIGRAMS",
    "TRIGRAMS_BY_NUMBER",
    "build_time_hexagram",
    "cast_hexagram",
    "hexagram_input_from_datetime",
    "lookup_hexagram",
]
