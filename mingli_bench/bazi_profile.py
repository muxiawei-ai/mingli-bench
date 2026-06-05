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
HIDDEN_STEM_ROLE_LABELS = {
    "main": "本气",
    "middle": "中气",
    "residual": "余气",
}
HIDDEN_STEMS = {
    "子": [{"stem": "癸", "role": "main", "weight": 1.0}],
    "丑": [
        {"stem": "己", "role": "main", "weight": 0.6},
        {"stem": "癸", "role": "middle", "weight": 0.25},
        {"stem": "辛", "role": "residual", "weight": 0.15},
    ],
    "寅": [
        {"stem": "甲", "role": "main", "weight": 0.6},
        {"stem": "丙", "role": "middle", "weight": 0.25},
        {"stem": "戊", "role": "residual", "weight": 0.15},
    ],
    "卯": [{"stem": "乙", "role": "main", "weight": 1.0}],
    "辰": [
        {"stem": "戊", "role": "main", "weight": 0.6},
        {"stem": "乙", "role": "middle", "weight": 0.25},
        {"stem": "癸", "role": "residual", "weight": 0.15},
    ],
    "巳": [
        {"stem": "丙", "role": "main", "weight": 0.6},
        {"stem": "戊", "role": "middle", "weight": 0.25},
        {"stem": "庚", "role": "residual", "weight": 0.15},
    ],
    "午": [
        {"stem": "丁", "role": "main", "weight": 0.7},
        {"stem": "己", "role": "residual", "weight": 0.3},
    ],
    "未": [
        {"stem": "己", "role": "main", "weight": 0.6},
        {"stem": "丁", "role": "middle", "weight": 0.25},
        {"stem": "乙", "role": "residual", "weight": 0.15},
    ],
    "申": [
        {"stem": "庚", "role": "main", "weight": 0.6},
        {"stem": "壬", "role": "middle", "weight": 0.25},
        {"stem": "戊", "role": "residual", "weight": 0.15},
    ],
    "酉": [{"stem": "辛", "role": "main", "weight": 1.0}],
    "戌": [
        {"stem": "戊", "role": "main", "weight": 0.6},
        {"stem": "辛", "role": "middle", "weight": 0.25},
        {"stem": "丁", "role": "residual", "weight": 0.15},
    ],
    "亥": [
        {"stem": "壬", "role": "main", "weight": 0.7},
        {"stem": "甲", "role": "middle", "weight": 0.3},
    ],
}

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
    """Build a local, auditable Bazi profile from pillars and hidden stems."""

    characters = _visible_characters(chart)
    ten_gods = [_character_ten_god(item, chart.day_master) for item in characters]
    hidden_stems = _hidden_stem_characters(chart)
    hidden_ten_gods = [_character_ten_god(item, chart.day_master) for item in hidden_stems]
    weighted_characters = _weighted_characters(characters, hidden_stems)
    weighted_ten_gods = [
        _character_ten_god(item, chart.day_master) for item in weighted_characters
    ]
    ten_god_summary = dict(Counter(item["ten_god"] for item in ten_gods if item.get("ten_god")))
    weighted_ten_god_summary = _weighted_ten_god_summary(weighted_ten_gods)
    group_counts = _group_counts(ten_god_summary, weighted_ten_god_summary)
    month_relation = _month_branch_relation(chart)
    strength = _day_master_strength(chart, group_counts, month_relation)
    focus = _practical_focus(group_counts, chart)
    structure_signals = _structure_signals(group_counts, chart, strength)

    return {
        "schema_version": BAZI_PROFILE_SCHEMA_VERSION,
        "source": "visible_and_hidden_stems_v1",
        "day_master": {
            "stem": chart.day_master,
            "element": chart.day_master_element,
            "polarity": STEM_POLARITY.get(chart.day_master),
            "polarity_label": POLARITY_LABELS.get(STEM_POLARITY.get(chart.day_master, "")),
        },
        "visible_characters": ten_gods,
        "hidden_stems": hidden_ten_gods,
        "weighted_characters": weighted_ten_gods,
        "ten_god_summary": ten_god_summary,
        "weighted_ten_god_summary": weighted_ten_god_summary,
        "ten_god_groups": group_counts,
        "day_master_strength": strength,
        "month_branch_relation": month_relation,
        "structure_signals": structure_signals,
        "practical_focus": focus,
        "overview": _overview(chart, strength, group_counts, focus),
        "caveats": [
            "画像已展开地支藏干并使用本地权重，但尚未计算旺衰格局、通根强弱、调候和大运。",
            "weighted_count 与 support_index 是本地启发式结构分数，用于提示分析方向，不是传统命理定论。",
        ],
    }


def hidden_stems_for_branch(branch: str) -> List[Dict[str, Any]]:
    """Return auditable hidden-stem metadata for one earthly branch."""

    return [dict(item) for item in HIDDEN_STEMS.get(branch, [])]


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


def _hidden_stem_characters(chart: BaziChart) -> List[Dict[str, Any]]:
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
        branch = pillar[1]
        branch_position = f"{pillar_name}_branch"
        for index, hidden in enumerate(hidden_stems_for_branch(branch), start=1):
            stem = str(hidden["stem"])
            role = str(hidden["role"])
            characters.append(
                {
                    "position": f"{branch_position}_hidden_{index}",
                    "position_label": f"{POSITION_LABELS[branch_position]}藏干{index}",
                    "branch_position": branch_position,
                    "branch_position_label": POSITION_LABELS[branch_position],
                    "branch": branch,
                    "char": stem,
                    "kind": "hidden_stem",
                    "hidden_role": role,
                    "hidden_role_label": HIDDEN_STEM_ROLE_LABELS.get(role, ""),
                    "element": STEM_TO_ELEMENT.get(stem),
                    "polarity": STEM_POLARITY.get(stem),
                    "weight": float(hidden["weight"]),
                    "weight_source": "hidden_stem",
                }
            )
    return characters


def _weighted_characters(
    visible_characters: Iterable[Dict[str, Any]],
    hidden_stems: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    weighted = []
    for item in visible_characters:
        if item.get("kind") != "stem":
            continue
        weighted.append(
            {
                **item,
                "weight": 1.0,
                "weight_source": "visible_stem",
            }
        )
    weighted.extend(dict(item) for item in hidden_stems)
    return weighted


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


def _weighted_ten_god_summary(items: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    summary: Counter[str] = Counter()
    for item in items:
        ten_god = item.get("ten_god")
        if not ten_god:
            continue
        summary[str(ten_god)] += float(item.get("weight") or 0.0)
    return {
        ten_god: round(weight, 3)
        for ten_god, weight in summary.items()
        if round(weight, 3) > 0
    }


def _group_counts(
    ten_god_summary: Dict[str, int],
    weighted_ten_god_summary: Optional[Dict[str, float]] = None,
) -> Dict[str, Dict[str, Any]]:
    counts = {group: 0 for group in GROUP_LABELS}
    details = {group: {} for group in GROUP_LABELS}
    weighted_counts = {group: 0.0 for group in GROUP_LABELS}
    weighted_details = {group: {} for group in GROUP_LABELS}
    for ten_god, count in ten_god_summary.items():
        group = TEN_GOD_GROUPS.get(ten_god)
        if not group:
            continue
        counts[group] += count
        details[group][ten_god] = count
    for ten_god, weight in (weighted_ten_god_summary or {}).items():
        group = TEN_GOD_GROUPS.get(ten_god)
        if not group:
            continue
        weighted_counts[group] += float(weight)
        weighted_details[group][ten_god] = round(float(weight), 3)
    return {
        group: {
            "count": counts[group],
            "weighted_count": round(weighted_counts[group], 3),
            "label": GROUP_LABELS[group],
            "details": details[group],
            "weighted_details": weighted_details[group],
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
    visible_peer = groups["peer"]["count"]
    visible_resource = groups["resource"]["count"]
    visible_output = groups["output"]["count"]
    visible_wealth = groups["wealth"]["count"]
    visible_officer = groups["officer"]["count"]
    peer = _weighted_group_count(groups, "peer")
    resource = _weighted_group_count(groups, "resource")
    output = _weighted_group_count(groups, "output")
    wealth = _weighted_group_count(groups, "wealth")
    officer = _weighted_group_count(groups, "officer")
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
    elif peer >= 2.4 and support_index >= 0.34:
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
        "peer_count": visible_peer,
        "resource_count": visible_resource,
        "output_count": visible_output,
        "wealth_count": visible_wealth,
        "officer_count": visible_officer,
        "peer_weighted_count": round(peer, 3),
        "resource_weighted_count": round(resource, 3),
        "output_weighted_count": round(output, 3),
        "wealth_weighted_count": round(wealth, 3),
        "officer_weighted_count": round(officer, 3),
        "month_relation_group": month_group,
        "method": "hidden_stem_weighted_ten_god_group_heuristic.v1",
    }


def _weighted_group_count(groups: Dict[str, Dict[str, Any]], group: str) -> float:
    payload = groups[group]
    if "weighted_count" in payload:
        return float(payload["weighted_count"])
    return float(payload.get("count") or 0)


def _practical_focus(
    groups: Dict[str, Dict[str, Any]],
    chart: BaziChart,
) -> List[Dict[str, str]]:
    focus = []
    if _weighted_group_count(groups, "peer") >= 2.4:
        focus.append(
            {
                "type": "self_drive",
                "label": "自我驱动明显",
                "summary": "同类星较多，分析时可关注主动性、竞争感、坚持己见和协作弹性。",
            }
        )
    if _weighted_group_count(groups, "output") >= 2:
        focus.append(
            {
                "type": "execution_expression",
                "label": "表达与输出活跃",
                "summary": "食伤组较多，适合关注表达、作品、执行节奏、技能输出和对规则的张力。",
            }
        )
    if _weighted_group_count(groups, "wealth") >= 1.8:
        focus.append(
            {
                "type": "resource_money",
                "label": "财星线索可见",
                "summary": "财星组可见，分析事业或财务问题时可关注资源承接、现金流、定价和现实交换。",
            }
        )
    if groups["resource"]["count"] == 0 and _weighted_group_count(groups, "resource") > 0:
        focus.append(
            {
                "type": "hidden_support_method",
                "label": "印星藏于地支",
                "summary": "显性天干地支主气不见印星，但藏干中有印星，适合把学习、方法论和外部支持作为隐性资源观察。",
            }
        )
    elif _weighted_group_count(groups, "resource") == 0:
        focus.append(
            {
                "type": "support_method_gap",
                "label": "印星未见",
                "summary": "印星组未见，建议关注学习支持、方法论、授权背书和长期补给是否充足。",
            }
        )
    if groups["officer"]["count"] == 0 and _weighted_group_count(groups, "officer") > 0:
        focus.append(
            {
                "type": "hidden_structure_pressure",
                "label": "官杀藏于地支",
                "summary": "显性天干地支主气不见官杀，但藏干中有官杀，规则、责任和压力线索偏隐性。",
            }
        )
    elif _weighted_group_count(groups, "officer") == 0:
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
        weighted_count = float(payload.get("weighted_count") or count)
        if weighted_count == 0:
            signals.append(
                {
                    "type": f"{group}_absent",
                    "label": f"{payload['label']}未见",
                    "summary": "显性四柱与藏干权重中均未检出该组十神，后续应结合大运和现实信息复核。",
                }
            )
        elif count == 0:
            signals.append(
                {
                    "type": f"{group}_hidden",
                    "label": f"{payload['label']}藏干可见",
                    "summary": f"显性计数为0，但藏干权重为{weighted_count:g}，说明该组十神偏隐性。",
                }
            )
        elif weighted_count >= 2.4:
            signals.append(
                {
                    "type": f"{group}_prominent",
                    "label": f"{payload['label']}较显",
                    "summary": f"显性计数为{count}，含藏干权重为{weighted_count:g}，适合作为画像重点观察项。",
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
        if float(payload.get("weighted_count") or payload.get("count") or 0) >= 1.8
    ]
    focus_labels = [item["label"] for item in focus][:3]
    return (
        f"日主{chart.day_master}（{chart.day_master_element or '未知'}）画像显示："
        f"{strength['label']}；"
        f"含藏干权重后较显十神组为{'、'.join(prominent) or '无'}。"
        f"优先观察{'、'.join(focus_labels) or '基础五行结构'}。"
    )


__all__ = [
    "BAZI_PROFILE_SCHEMA_VERSION",
    "HIDDEN_STEMS",
    "build_bazi_profile",
    "hidden_stems_for_branch",
    "ten_god_for",
]
