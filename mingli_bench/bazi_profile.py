"""Deterministic Bazi profile scaffolds for local reports."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

from .calendar import BRANCH_TO_ELEMENT, STEM_TO_ELEMENT
from .chart_api import BaziChart


BAZI_PROFILE_SCHEMA_VERSION = "bazi_profile.v1"
ELEMENT_ORDER = ["木", "火", "土", "金", "水"]
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

STEM_POLARITY = {
    "甲": "yang",
    "乙": "yin",
    "丙": "yang",
    "丁": "yin",
    "戊": "yang",
    "己": "yin",
    "庚": "yang",
    "辛": "yin",
    "壬": "yang",
    "癸": "yin",
}
BRANCH_POLARITY = {
    "子": "yang",
    "丑": "yin",
    "寅": "yang",
    "卯": "yin",
    "辰": "yang",
    "巳": "yin",
    "午": "yang",
    "未": "yin",
    "申": "yang",
    "酉": "yin",
    "戌": "yang",
    "亥": "yin",
}
POLARITY_LABELS = {"yang": "阳", "yin": "阴"}

TEN_GOD_GROUPS = {
    "比肩": "peer",
    "劫财": "peer",
    "食神": "output",
    "伤官": "output",
    "正财": "wealth",
    "偏财": "wealth",
    "正官": "officer",
    "七杀": "officer",
    "正印": "resource",
    "偏印": "resource",
}
GROUP_LABELS = {
    "peer": "同类/自我",
    "output": "食伤/表达",
    "wealth": "财星/资源",
    "officer": "官杀/规则",
    "resource": "印星/支持",
}
POSITION_LABELS = {
    "year_stem": "年干",
    "year_branch": "年支",
    "month_stem": "月干",
    "month_branch": "月支",
    "day_stem": "日干",
    "day_branch": "日支",
    "hour_stem": "时干",
    "hour_branch": "时支",
}


def build_bazi_profile(chart: BaziChart) -> Dict[str, Any]:
    """Build a local, auditable Bazi profile from visible pillar characters."""

    characters = _visible_characters(chart)
    ten_gods = [_character_ten_god(item, chart.day_master) for item in characters]
    ten_god_summary = dict(Counter(item["ten_god"] for item in ten_gods if item.get("ten_god")))
    group_counts = _group_counts(ten_god_summary)
    month_relation = _month_branch_relation(chart)
    strength = _day_master_strength(chart, group_counts, month_relation)
    focus = _practical_focus(group_counts, chart)
    structure_signals = _structure_signals(group_counts, chart, strength)

    return {
        "schema_version": BAZI_PROFILE_SCHEMA_VERSION,
        "source": "visible_pillars_v1",
        "day_master": {
            "stem": chart.day_master,
            "element": chart.day_master_element,
            "polarity": STEM_POLARITY.get(chart.day_master),
            "polarity_label": POLARITY_LABELS.get(STEM_POLARITY.get(chart.day_master, "")),
        },
        "visible_characters": ten_gods,
        "ten_god_summary": ten_god_summary,
        "ten_god_groups": group_counts,
        "day_master_strength": strength,
        "month_branch_relation": month_relation,
        "structure_signals": structure_signals,
        "practical_focus": focus,
        "overview": _overview(chart, strength, group_counts, focus),
        "caveats": [
            "画像基于四柱显性天干地支与地支主五行代理计算，暂未展开藏干、旺衰格局、调候和大运。",
            "support_index 是本地启发式结构分数，用于提示分析方向，不是传统命理定论。",
        ],
    }


def ten_god_for(
    day_stem: str,
    target_element: str,
    target_polarity: Optional[str],
) -> Optional[str]:
    """Return the ten-god relation for one visible target against day stem."""

    day_element = STEM_TO_ELEMENT.get(day_stem)
    day_polarity = STEM_POLARITY.get(day_stem)
    if not day_element or not target_element or not target_polarity or not day_polarity:
        return None
    same_polarity = day_polarity == target_polarity
    if target_element == day_element:
        return "比肩" if same_polarity else "劫财"
    if GENERATES.get(target_element) == day_element:
        return "偏印" if same_polarity else "正印"
    if GENERATES.get(day_element) == target_element:
        return "食神" if same_polarity else "伤官"
    if CONTROLS.get(day_element) == target_element:
        return "偏财" if same_polarity else "正财"
    if CONTROLS.get(target_element) == day_element:
        return "七杀" if same_polarity else "正官"
    return None


def _visible_characters(chart: BaziChart) -> List[Dict[str, Any]]:
    pillars = [
        ("year", chart.pillars.year),
        ("month", chart.pillars.month),
        ("day", chart.pillars.day),
        ("hour", chart.pillars.hour),
    ]
    characters = []
    for pillar_name, pillar in pillars:
        if not pillar:
            continue
        stem, branch = pillar[0], pillar[1]
        characters.append(
            {
                "position": f"{pillar_name}_stem",
                "position_label": POSITION_LABELS[f"{pillar_name}_stem"],
                "char": stem,
                "kind": "stem",
                "element": STEM_TO_ELEMENT.get(stem),
                "polarity": STEM_POLARITY.get(stem),
            }
        )
        characters.append(
            {
                "position": f"{pillar_name}_branch",
                "position_label": POSITION_LABELS[f"{pillar_name}_branch"],
                "char": branch,
                "kind": "branch_main_element_proxy",
                "element": BRANCH_TO_ELEMENT.get(branch),
                "polarity": BRANCH_POLARITY.get(branch),
            }
        )
    return characters


def _character_ten_god(item: Dict[str, Any], day_stem: str) -> Dict[str, Any]:
    polarity = item.get("polarity")
    ten_god = ten_god_for(day_stem, str(item.get("element") or ""), polarity)
    group = TEN_GOD_GROUPS.get(ten_god or "")
    return {
        **item,
        "polarity_label": POLARITY_LABELS.get(str(polarity), ""),
        "ten_god": ten_god,
        "ten_god_group": group,
        "ten_god_group_label": GROUP_LABELS.get(group or "", ""),
    }


def _group_counts(ten_god_summary: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    counts = {group: 0 for group in GROUP_LABELS}
    details = {group: {} for group in GROUP_LABELS}
    for ten_god, count in ten_god_summary.items():
        group = TEN_GOD_GROUPS.get(ten_god)
        if not group:
            continue
        counts[group] += count
        details[group][ten_god] = count
    return {
        group: {
            "count": counts[group],
            "label": GROUP_LABELS[group],
            "details": details[group],
        }
        for group in GROUP_LABELS
    }


def _month_branch_relation(chart: BaziChart) -> Dict[str, Any]:
    month_branch = chart.pillars.month[1] if chart.pillars.month else None
    element = BRANCH_TO_ELEMENT.get(month_branch or "")
    polarity = BRANCH_POLARITY.get(month_branch or "")
    ten_god = ten_god_for(chart.day_master, element or "", polarity)
    return {
        "branch": month_branch,
        "element": element,
        "polarity": polarity,
        "polarity_label": POLARITY_LABELS.get(polarity or "", ""),
        "ten_god": ten_god,
        "group": TEN_GOD_GROUPS.get(ten_god or ""),
        "source": "month_branch_main_element_proxy",
    }


def _day_master_strength(
    chart: BaziChart,
    groups: Dict[str, Dict[str, Any]],
    month_relation: Dict[str, Any],
) -> Dict[str, Any]:
    peer = groups["peer"]["count"]
    resource = groups["resource"]["count"]
    output = groups["output"]["count"]
    wealth = groups["wealth"]["count"]
    officer = groups["officer"]["count"]
    month_group = month_relation.get("group")
    month_support = 1.25 if month_group in {"peer", "resource"} else 0.0
    month_pressure = 0.75 if month_group in {"output", "wealth", "officer"} else 0.0
    support_score = peer + resource + month_support
    pressure_score = output * 0.75 + wealth + officer * 1.1 + month_pressure
    total = support_score + pressure_score
    support_index = round(support_score / total, 3) if total else 0.0

    if support_index >= 0.58:
        level = "strong"
        label = "日主支持偏强"
    elif support_index <= 0.28:
        level = "weak"
        label = "日主支持偏弱"
    elif peer >= 3 and support_index >= 0.34:
        level = "self_supported"
        label = "同类明显，有自我支撑"
    else:
        level = "balanced"
        label = "支持与消耗相对均衡"

    return {
        "level": level,
        "label": label,
        "support_index": support_index,
        "support_score": round(support_score, 3),
        "pressure_score": round(pressure_score, 3),
        "peer_count": peer,
        "resource_count": resource,
        "output_count": output,
        "wealth_count": wealth,
        "officer_count": officer,
        "month_relation_group": month_group,
        "method": "visible_ten_god_group_heuristic.v1",
    }


def _practical_focus(
    groups: Dict[str, Dict[str, Any]],
    chart: BaziChart,
) -> List[Dict[str, str]]:
    focus = []
    if groups["peer"]["count"] >= 3:
        focus.append(
            {
                "type": "self_drive",
                "label": "自我驱动明显",
                "summary": "同类星较多，分析时可关注主动性、竞争感、坚持己见和协作弹性。",
            }
        )
    if groups["output"]["count"] >= 2:
        focus.append(
            {
                "type": "execution_expression",
                "label": "表达与输出活跃",
                "summary": "食伤组较多，适合关注表达、作品、执行节奏、技能输出和对规则的张力。",
            }
        )
    if groups["wealth"]["count"] >= 2:
        focus.append(
            {
                "type": "resource_money",
                "label": "财星线索可见",
                "summary": "财星组可见，分析事业或财务问题时可关注资源承接、现金流、定价和现实交换。",
            }
        )
    if groups["resource"]["count"] == 0:
        focus.append(
            {
                "type": "support_method_gap",
                "label": "印星未见",
                "summary": "印星组未见，建议关注学习支持、方法论、授权背书和长期补给是否充足。",
            }
        )
    if groups["officer"]["count"] == 0:
        focus.append(
            {
                "type": "structure_pressure_gap",
                "label": "官杀未见",
                "summary": "官杀组未见，规则、责任、外部约束和职业阶梯需要结合现实信息再判断。",
            }
        )
    if chart.input.hour is None:
        focus.append(
            {
                "type": "missing_hour",
                "label": "时柱缺失",
                "summary": "出生时辰未知，画像无法覆盖时柱对子女、晚年、行动落点和具体时机的影响。",
            }
        )
    return focus


def _structure_signals(
    groups: Dict[str, Dict[str, Any]],
    chart: BaziChart,
    strength: Dict[str, Any],
) -> List[Dict[str, str]]:
    signals = [
        {
            "type": "day_master_strength",
            "label": strength["label"],
            "summary": (
                f"support_index={strength['support_index']}，"
                f"support_score={strength['support_score']}，"
                f"pressure_score={strength['pressure_score']}。"
            ),
        }
    ]
    for group, payload in groups.items():
        count = payload["count"]
        if count == 0:
            signals.append(
                {
                    "type": f"{group}_absent",
                    "label": f"{payload['label']}未见",
                    "summary": "显性四柱中未检出该组十神，后续应结合藏干、大运和现实信息复核。",
                }
            )
        elif count >= 3:
            signals.append(
                {
                    "type": f"{group}_prominent",
                    "label": f"{payload['label']}较显",
                    "summary": "该组十神在显性四柱中出现较多，适合作为画像重点观察项。",
                }
            )
    if chart.input.hour is None:
        signals.append(
            {
                "type": "hour_unknown",
                "label": "时柱未知",
                "summary": "时柱缺失会降低画像完整度，尤其影响晚年、子女、行动落点和细分时机判断。",
            }
        )
    return signals


def _overview(
    chart: BaziChart,
    strength: Dict[str, Any],
    groups: Dict[str, Dict[str, Any]],
    focus: Iterable[Dict[str, str]],
) -> str:
    prominent = [
        payload["label"]
        for payload in groups.values()
        if int(payload.get("count") or 0) >= 2
    ]
    focus_labels = [item["label"] for item in focus][:3]
    return (
        f"日主{chart.day_master}（{chart.day_master_element or '未知'}）画像显示："
        f"{strength['label']}；"
        f"较显十神组为{'、'.join(prominent) or '无'}。"
        f"优先观察{'、'.join(focus_labels) or '基础五行结构'}。"
    )


__all__ = [
    "BAZI_PROFILE_SCHEMA_VERSION",
    "build_bazi_profile",
    "ten_god_for",
]
